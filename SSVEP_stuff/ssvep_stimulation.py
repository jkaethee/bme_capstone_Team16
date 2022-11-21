import time
import numpy as np
from psychopy import visual, event
from analysis import CCAAnalysis

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
    self._stim1 = visual.Circle(win=self._window, pos=position, size=size, radius=0.4, opacity=1)

  def draw(self):
    """Draw stimulation"""
    if self._fr_counter == 0:
        self._fr_counter = self._fr_rate
        self._stim1.draw()
    self._fr_counter -= 1

class OnlineSSVEP:

  def __init__(self, screen_refresh_rate, signal_len, eeg_s_rate, analysis_type):
    """
    Args:
        screen_refresh_rate (int): Refresh rate of your screen
        frame_rates (list): List of number of frames in which each target is flickering (one number for each target)
        positions (list): List of target positions in the screen
        signal_len (float): EEG signal length (in seconds) to be analysed
        eeg_s_rate (int): Sampling rate of EEG signal
        overlap (float): Time overlap between two consecutive data chunk
    """
    self.window = visual.Window([800,600], monitor="testMonitor", fullscr=True, allowGUI=True, screen=1, units='norm', color=[0.1,0.1,0.1])
    self.target_positions = [(-.6, -.6), (-.6, .6), (.6, .6), (.6, -.6)]
    self.target_arrows = ['\u2199', '\u2196', '\u2197', '\u2198']
    self.stim_size = (0.6 * self.window.size[1]/self.window.size[0], 0.6)
    self.fr_rates = [5, 6, 7, 8] # 12Hz, 10Hz, 8.5Hz, 7.5Hz.
    self._freqs = [round(screen_refresh_rate / fr_no, 1) for fr_no in self.fr_rates]
    self.targets = []
    self.freq_labels = []
    self._data_buff= np.array([])
    self.signal_len = signal_len
    self.eeg_s_rate = eeg_s_rate
    self.overlap = 0.2 # overlap (float): Time overlap between two consecutive data chunk
    self._prediction_arrows = []
    self._prediction_ind = None


    if analysis_type == 'CCA':
      self.cca = CCAAnalysis(freqs=self._freqs, win_len=self.signal_len, s_rate=self.eeg_s_rate, n_harmonics=2)

  
  def _display_stim(self):
    for fr_no, pos, freq, arrow in zip(self.fr_rates, self.target_positions, self._freqs, self.target_arrows):
      self.targets.append(Stimulus(
        window=self.window,
        size=self.stim_size,
        n_frame=fr_no,
        position=pos
      ))
      self.freq_labels.append(visual.TextBox2(win=self.window, text=f'{freq} Hz', 
        pos=(pos[0]+0.1,pos[1]+0.1)))
      
      self._prediction_arrows.append(visual.TextStim(win=self.window, pos=[0, 0], text=arrow,
                                                         color=(-1, -1, -1), height=.15,
                                                         colorSpace='rgb', bold=True))

  
  def _analyze_data_CCA(self):
    if len(self._data_buff) > 0:
      if self._data_buff.shape[0] > self.signal_len * self.eeg_s_rate:
          scores = self.cca.apply_cca(self._data_buff[:self.signal_len * self.eeg_s_rate, :])
          self._data_buff = self._data_buff[:int(self.overlap * self.eeg_s_rate), :]
          print(scores)
          if not all(val < SCORE_TH for val in scores):
              self._predicted_ind = np.argmax(scores)
              print(self._predicted_ind)
          else:
              self._predicted_ind = None

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

    print('Starting trial')
    while time.time() - start_time < duration:
      self.window.flip()
      for stim in self.targets:
        stim.draw()
      if self._prediction_ind is not None:
        self._prediction_arrows[self._predicition_ind].draw()
      for label in self.freq_labels:
          label.draw()
      self._analyze_data_CCA()
    
    self.window.close()
    print('Done trial')