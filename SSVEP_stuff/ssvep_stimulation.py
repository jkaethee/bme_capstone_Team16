import time
import numpy as np
from psychopy import visual, event
from threading import Lock
from analysis import Analysis

SCORE_TH = .1

#  https://github.com/Mentalab-hub/explorepy/blob/master/examples/ssvep_demo/ssvep.py
class Stimulus:
  """
  Class to generate a flickering circle stimulus
  """

  def __init__(self, window, size, position, n_frame) -> None:
    """
    window (psychopy.visual.window): Psychopy window
    size (int): Size of the stimulation
    position (tuple): Position of stimulation on the screen
    n_frame (int): Number of frames for the stim to flicker (frequency = monitor_refresh_rate/n_frame)
    """

    self._window = window
    self._fr_rate = n_frame
    self._fr_counter = n_frame
    pattern = np.ones((4, 4))
    pattern[::2, ::2] *= -1
    pattern[1::2, 1::2] *= -1
    self._stim1 = visual.RadialStim(win=self._window, tex=pattern, pos=position,
                                        size=size, radialCycles=1, texRes=256, opacity=1)
    self._stim2 = visual.RadialStim(win=self._window, tex=pattern*-1, pos=position,
                                    size=size, radialCycles=1, texRes=256, opacity=1)

    self._toggle_flag = False

  def draw(self):
    """Draw stimulation"""
    if self._fr_counter == 0:
        self._fr_counter = self._fr_rate
        if self._toggle_flag:
          self._stim1.draw()
        else:
            self._stim2.draw()
        self._toggle_flag = not self._toggle_flag
    self._fr_counter -= 1

class OnlineSSVEP:

  def __init__(self, screen_refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type):
    """
    Args:
        screen_refresh_rate (int): Refresh rate of your screen
        signal_len (float): EEG signal length (in seconds) to be analysed
        eeg_s_rate (int): Sampling rate of EEG signal
        fr_rates (list): List of number of frames in which each target is flickering (one number for each target)
        overlap (float): Time overlap between two consecutive data chunk
    """
    self.window = visual.Window([800,600], monitor="testMonitor", fullscr=True, allowGUI=True, screen=1, units='norm', color=[0.1,0.1,0.1])
    self.target_positions = [(-.6, .6), (-.6, -.6),(.6, .6), (.6, -.6)]
    self.target_arrows = ['\u2196', '\u2199', '\u2197', '\u2198']
    self.stim_size = (0.6 * self.window.size[1]/self.window.size[0], 0.6)
    self.fr_rates = fr_rates
    self._freqs = [screen_refresh_rate / fr_no for fr_no in self.fr_rates]
    self.targets = []
    self.freq_labels = []
    self._data_buff= np.array([])
    self.signal_len = signal_len
    self.eeg_s_rate = eeg_s_rate
    self.lock = Lock()
    self.overlap = 0.2 # overlap (float): Time overlap between two consecutive data chunk
    self._prediction_arrows = []
    self._prediction_ind = None


    if analysis_type == 'CCA':
      self.analysis = Analysis(freqs=self._freqs, win_len=self.signal_len, s_rate=self.eeg_s_rate, n_harmonics=2)

  
  def _display_stim(self):
    for fr_no, pos, freq, arrow in zip(self.fr_rates, self.target_positions, self._freqs, self.target_arrows):
      self.targets.append(Stimulus(
        window=self.window,
        size=self.stim_size,
        n_frame=fr_no,
        position=pos
      ))
      self.freq_labels.append(visual.TextBox2(win=self.window, text=f'{round(freq,1)} Hz', 
        pos=(pos[0]+0.1,pos[1]+0.1)))
      
      self._prediction_arrows.append(visual.TextStim(win=self.window, pos=[0, 0], text=arrow,
                                                         color=(-1, -1, -1), height=.15,
                                                         colorSpace='rgb', bold=True))

  def _analyze_data_CCA(self):
    if len(self._data_buff) > 0:
      if self._data_buff.shape[0] > self.signal_len * self.eeg_s_rate:
        with self.lock:
          scores, fatigue = self.analysis.analyse(self._data_buff[:self.signal_len * self.eeg_s_rate, :])
          self._data_buff = self._data_buff[:int(self.overlap * self.eeg_s_rate), :]
        print(scores)
        if not all(val < SCORE_TH for val in scores):
            self._prediction_ind = np.argmax(scores)
            print(f'Predicted Frequency: {self._freqs[self._prediction_ind]}')
        else:
            self._prediction_ind = None

  def update_buffer(self, packet):
    """Update EEG buffer of the experiment

    Args:
        packet (explorepy.packet.EEG): EEG packet

    """
    timestamp, eeg = packet.get_data()
    if not len(self._data_buff):
        self._data_buff = eeg.T
    else:
        self._data_buff = np.concatenate((self._data_buff, eeg.T), axis=0)
    
  def run_ssvep(self, duration: int):
    self._display_stim()

    start_time = time.time()
    while time.time() - start_time < duration:
      self.window.flip()
      for stim in self.targets:
        stim.draw()
      if self._prediction_ind is not None:
        self._prediction_arrows[self._prediction_ind].draw()
      for label in self.freq_labels:
          label.draw()
      self._analyze_data_CCA()
    self.window.close()