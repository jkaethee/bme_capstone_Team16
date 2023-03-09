import time
import PySimpleGUIQt as sg
import serial
import numpy as np
import pandas as pd
from psychopy import visual, event
from threading import Lock
from analysis import CCAAnalysis, CNNAnalysis
import matplotlib.pyplot as plt
import random
from scipy.fft import fft, rfft, ifft, fftfreq, irfft
from scipy import signal 

def open_likert_window(title: str):
    '''
    Window to record user's rating of fatigue before and after experiments
    '''
    fatigue_rating = 0
    likert_layout = [[sg.Text("How much fatigue are you having now?")], 
                    [sg.Button(f"{num}", key=f"Rating_{num}",) for num in range(1,11)],
                    [sg.Text("1 = No Fatigue | 10 = Worst Possible Fatigue")]]
    # Record user response
    likert_window = sg.Window(f"{title} Fatigue Likert Scale", likert_layout, size=(300, 100))
    while True:
        event, values = likert_window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if "Rating" in event:
            fatigue_rating = int(likert_window[event].get_text())
            break
    
    likert_window.close()
    return fatigue_rating

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def plot_filtered_eeg_data(data, SAMPLE_RATE, EEG_CHANNEL_NAMES):
  x = data['TimeStamp'].apply(lambda x: x-data['TimeStamp'].iloc[0])

  fig, axes = plt.subplots(8,3)

  fig.tight_layout()
  filtered_y = np.empty((len(x), 8))
  for i in range(1,9):
    filtered_y[:,i-1] = butter_highpass_filter(data.iloc[:,i], cutoff=1, fs=SAMPLE_RATE, order=5)

    N = x.shape[0]
    xf = fftfreq(N, 1 / SAMPLE_RATE)
    yf = np.abs(fft(filtered_y[:,i-1]))

    axes[i-1, 0].set_title(f'filtered {EEG_CHANNEL_NAMES[i-1]} channel')
    axes[i-1, 0].plot(x, filtered_y[:, i-1])
    axes[i-1, 0].set_xlim(0, 5)


    axes[i-1, 1].set_title(f'filtered {EEG_CHANNEL_NAMES[i-1]} FFT channel')
    axes[i-1, 1].plot(xf, yf)
    axes[i-1, 1].set_xlim(0, 15)


    axes[i-1, 2].set_title(f'filtered {EEG_CHANNEL_NAMES[i-1]} Spectrogram channel')
    axes[i-1, 2].specgram(filtered_y[:,i-1], Fs=256)
    axes[i-1, 2].set_ylim(0,30)
  
  plt.title('Sanity Checking Results')
  plt.show()

def sanity_check(explore):
  '''
  Run sanity checking code prior to experiments
  explore (explorepy.explore.Explore): explorepy device
  '''
  EEG_CHANNEL_NAMES = ['TimeStamps', 'Fp1', 'Fp2', 'PO3', 'PO4', 'O1', 'O2', 'OZ', 'POZ']
  SAMPLE_RATE = 256
  EEG_FILE_PATH = 'sanity_check_eeg'

  window = visual.Window([1920, 1080], monitor="testMonitor", fullscr=True, allowGUI=True, units='norm', color=[0.1,0.1,0.1])
  text_position = (0,0)
  text_label = ['Keep eyes open and blink when prompted', 'Keep eyes closed for 30 seconds']
  blink_counter = np.arange(0,6,1)
  eyes_closed_counter = np.linspace(1,30, num=30)
  sanity_time = 10
  
  sanity_1 = []
  sanity_2 = []

  # Create displays for blinks every 5 seconds
  for count in reversed(blink_counter):
    text = ''
    if count != 0:
      text = f'{text_label[0]}: {round(count)}'
    else:
      text = 'BLINK'

    sanity_1.append(visual.TextStim(win=window, text=text, pos=text_position, 
                    color=(-1, -1, -1), height=.20, colorSpace='rgb', bold=True))
  
  # Create display for eyes closed for 30 seconds
  for count in eyes_closed_counter:
    sanity_2.append(visual.TextStim(win=window, text=f'{text_label[1]}: {round(count)} seconds', pos=text_position, 
                  color=(-1, -1, -1), height=.20, colorSpace='rgb', bold=True))
  

  end_time = time.time() + sanity_time

  # Display the prompts for 30 seconds of periodic blinking
  explore.record_data(file_name=EEG_FILE_PATH, file_type='csv', do_overwrite=True)
  while time.time() < end_time:
    for label in sanity_1:
      # Hold the label for 1 second
      end = time.time() + 1
      while time.time() < end:
        label.draw()
        window.flip()
  
  end_time = time.time() + sanity_time
  # Display the prompt for 30 seconds eyes closed
  while time.time() < end_time:
    for label in sanity_2:
      # Hold the label for 1 second
      end = time.time() + 1
      while time.time() < end:
        label.draw()
        window.flip()
  
  window.close()
  explore.stop_recording()

  data = pd.read_csv(EEG_FILE_PATH+'_ExG.csv')
  plot_filtered_eeg_data(data, SAMPLE_RATE, EEG_CHANNEL_NAMES)

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

  def __init__(self, screen_refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type, file_name, arduino_flag):
    """
    Args:
        screen_refresh_rate (int): Refresh rate of your screen
        signal_len (float): EEG signal length (in seconds) to be analysed
        eeg_s_rate (int): Sampling rate of EEG signal
        fr_rates (list): List of number of frames in which each target is flickering (one number for each target)
        overlap (float): Time overlap between two consecutive data chunk
    """

    self.window = visual.Window([1920, 1080], monitor="testMonitor", fullscr=True, allowGUI=True, units='norm', color=[0.1,0.1,0.1])
    self.target_positions = [(-.6, .6), (-.6, -.6),(.6, .6), (.6, -.6)]
    self.target_arrows = ['\u2196', '\u2199', '\u2197', '\u2198']
    self.direction_labels = ['Top Left', 'Bottom Left', 'Top Right', 'Bottom Right']
    self.stim_size = (0.6 * self.window.size[1]/self.window.size[0], 0.6)
    self.fr_rates = fr_rates
    self._freqs = [screen_refresh_rate / fr_no for fr_no in self.fr_rates]
    self.targets = []
    self.freq_labels = []
    self._data_buff= np.array([])
    self.signal_len = signal_len
    self.eeg_s_rate = eeg_s_rate
    self.fatigues = []
    self.fatigue_times = []
    self.file_name = file_name
    self.lock = Lock()
    self.overlap = 0.2 # overlap (float): Time overlap between two consecutive data chunk
    self._prediction_arrows = []
    self._prediction_ind = None
    self.direction_cues = []
    self.arduino_flag = arduino_flag

    # Arduino setup 
    if self.arduino_flag:
      self._arduino = serial.Serial(port='COM7', baudrate=9600, timeout=.1)

    
    # Analysis Type
    if analysis_type == 'CCA':
      self.analysis = CCAAnalysis(freqs=self._freqs, win_len=self.signal_len, s_rate=self.eeg_s_rate, n_harmonics=2)
    
    elif analysis_type == 'CNN':
      self.analysis = CNNAnalysis(path="models/model_3.h5", freqs=self._freqs, win_len=self.signal_len, s_rate=self.eeg_s_rate)

  
  def _display_stim(self):
    for fr_no, pos, freq, arrow, cue in zip(self.fr_rates, self.target_positions, self._freqs, self.target_arrows, self.direction_labels):
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

      self.direction_cues.append(visual.TextStim(win=self.window, pos=[0, 0], text=cue,
                                                         color=(-1, -1, -1), height=.15,
                                                         colorSpace='rgb', bold=True))

  def _analyze_data_CCA(self, start_time):
    if len(self._data_buff) > 0:
      if self._data_buff.shape[0] > self.signal_len * self.eeg_s_rate:
        with self.lock:
          print('before break')
          scores, fatigue = self.analysis.analyse(self._data_buff[:self.signal_len * self.eeg_s_rate, :])
          print('scores: ', scores)
          self.fatigues.append(fatigue)
          self.fatigue_times.append(time.time() - start_time)
          print('Fatigue score: ', fatigue)
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
    
  def run_ssvep(self,trials: int, start_rating: int, start_time: int):
    self._display_stim()
    iterations = np.zeros(4)

    compare_list = []
    ground_truth = []
    actual_preds = []
    ground_truth_times = []

    num_of_wrong = 0
    while np.sum(iterations)/4!= trials:
      
      self.window.flip()

      # First, randomly assign the user 1 of 4 directions to look at (keep track of how many trials for each stimuli)
      direction_idx = random.randint(0,3)
      while iterations[direction_idx] == trials:
        direction_idx = random.randint(0,3)

      # Second, cue the user to look in a certain direction (give them X seconds to look at the prompt)
      end_time = time.time() + 2
      while time.time() < end_time:
        self.window.flip()
        self.direction_cues[direction_idx].draw()

      # Third, flash all the stimuli for and record the user's prediction
      self._prediction_ind = None
      self._data_buff = np.array([])

      latency_start = time.time()
      # Timestamps for each ground_truth
      ground_truth_times.append(time.time()-start_time)
      while self._prediction_ind is None:
        self.window.flip()
        for stim in self.targets:
          stim.draw() # Flash all the stimuli
        for label in self.freq_labels:
          label.draw()
        
        self._analyze_data_CCA(start_time)
      
      print(f'Latency:  {time.time() - latency_start} sec')
      print(f'Actual: {self.direction_labels[direction_idx]} vs. Prediction: {self.direction_labels[self._prediction_ind]}')
      print('------------------------------------------------------------------------------------------')
      
      iterations[direction_idx] += 1

      # Ground_truth for each trial
      ground_truth.append(self._freqs[direction_idx])

      # Actual prediction for each trial
      actual_preds.append(self._freqs[self._prediction_ind])

      if self.arduino_flag:
        self.write_read(str(self._prediction_ind+1))

      ## Append if prediction is True (0) or False (1)
      compare_list.append(int(direction_idx != self._prediction_ind))
      if direction_idx != self._prediction_ind:
        num_of_wrong += 1

    self.window.close()

    # Record fatigue measurement at the end
    end_rating = open_likert_window("Post-SSVEP")

    if self.arduino_flag:
      self.write_read('q')
      self._arduino.close()

    plt.figure()
    plt.suptitle(f'Predictions from {trials*4} trials')
    plt.title(f'Number of incorrect predictions: {num_of_wrong}')
    x_axis = np.arange(len(compare_list))
    plt.plot(x_axis, compare_list)
    plt.yticks([0, 1], ["Correct", "False"])
    plt.ylabel('Prediction')
    plt.locator_params(axis="x", integer=True, tight=True)
    plt.xlabel('Trials')
    plt.legend()
    plt.savefig(f"{self.file_name}_prediction_graph.png")
    
    plt.figure()
    plt.suptitle('Fatigue scores vs. Time')
    plt.title(f'Median: {round(np.median(self.fatigues), 3)}, Mean: {round(np.mean(self.fatigues), 3)}, Integral: {round(np.sum(self.fatigues), 3)}')
    plt.figtext(0.5, 0, s=f"Self-reported Fatigue: Start -> {start_rating} | End -> {end_rating}", horizontalalignment = 'center')
    plt.xlabel('Trials')
    plt.ylabel('Fatigue Score')
    plt.plot(x_axis, self.fatigues)
    plt.savefig(f'{self.file_name}_fatigue_scores.png')

    # Save start of trials
    df = {
      'trial_start': ground_truth_times,
      'ground_truth': ground_truth,
      'actual_pred': actual_preds,
      'fatigue_score': self.fatigues
    }
    pd.DataFrame(df).to_csv(f'{self.file_name}_trial_info.csv')

  def write_read(self, prediction_index):
    self._arduino.write(bytes(prediction_index, 'utf-8'))  # Writing to Arduino


class CarDrive(OnlineSSVEP):
  def __init__(self, screen_refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type, arduino_flag):
    self.window = visual.Window([1920, 1080], monitor="testMonitor", fullscr=True, allowGUI=True, units='norm', color=[0.1,0.1,0.1])
    # self.target_positions = [(0, .6), (-.6, 0),(.6, 0), (0, -.6)]
    self.target_positions = [(-.6, .6), (-.6, -.6),(.6, .6), (.6, -.6)]
    self.target_arrows = ['\u2196', '\u2199', '\u2197', '\u2198']
    self.direction_labels = ['Top Left', 'Bottom Left', 'Top Right', 'Bottom Right']
    self.stim_size = (0.6 * self.window.size[1]/self.window.size[0], 0.6)
    self.fr_rates = fr_rates
    self._freqs = [screen_refresh_rate / fr_no for fr_no in self.fr_rates]
    self.directions = ['Forward', 'Left', 'Right', 'Stop']
    self.targets = []
    self.freq_labels = []
    self._data_buff= np.array([])
    self.signal_len = signal_len
    self.eeg_s_rate = eeg_s_rate
    self.fatigues = []
    self.fatigue_times = []
    self.lock = Lock()
    self.overlap = 0.2 # overlap (float): Time overlap between two consecutive data chunk
    self._prediction_arrows = []
    self._prediction_ind = None
    self.direction_cues = []
    self.arduino_flag = arduino_flag
    self.screen_refresh_rate = screen_refresh_rate

    # Arduino setup 
    if self.arduino_flag:
      self._arduino = serial.Serial(port='COM7', baudrate=9600, timeout=.1)

    if analysis_type == 'CCA':
      self.analysis = CCAAnalysis(freqs=self._freqs, win_len=self.signal_len, s_rate=self.eeg_s_rate, n_harmonics=2)

  def write_read(self, prediction_index):
    self._arduino.write(bytes(prediction_index, 'utf-8'))  # Writing to Arduino

  def _display_stim(self):
    for fr_no, pos, direction, label, arrow, cue in zip(self.fr_rates, self.target_positions, self.directions, self._freqs, self.target_arrows, self.direction_labels):
      self.targets.append(Stimulus(
        window=self.window,
        size=self.stim_size,
        n_frame=fr_no,
        position=pos
      ))
      self.freq_labels.append(visual.TextBox2(win=self.window, text=f'{label} Hz -> {direction}', 
        pos=(pos[0]+0.1,pos[1]+0.1)))
      
      self._prediction_arrows.append(visual.TextStim(win=self.window, pos=[0, 0], text=arrow,
                                                         color=(-1, -1, -1), height=.15,
                                                         colorSpace='rgb', bold=True))

      self.direction_cues.append(visual.TextStim(win=self.window, pos=[0, 0], text=cue,
                                                         color=(-1, -1, -1), height=.15,
                                                         colorSpace='rgb', bold=True))

  def drive_car(self, length, start_time):
    self._display_stim()
    
    while time.time() < length+start_time:
      self._prediction_ind = None
      self._data_buff = np.array([])

      while self._prediction_ind is None:
        self.window.flip()
        for stim in self.targets:
          stim.draw() # Flash all the stimuli
        for label in self.freq_labels:
          label.draw()
        
        OnlineSSVEP._analyze_data_CCA(self, start_time)
      
      if self.arduino_flag:
        print(f'Prediction: {self.directions[self._prediction_ind]}')
        self.write_read(str(self._prediction_ind+1))
        self._prediction_ind = None

    if self.arduino_flag:
      self.write_read('q')
      self._arduino.close()

    self.window.close()