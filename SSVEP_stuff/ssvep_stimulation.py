import time
import numpy as np
from psychopy import visual, event

#  https://github.com/Mentalab-hub/explorepy/blob/master/examples/ssvep_demo/ssvep.py
class Stimulus:
  """
  Class to generate a flickering circle stimulus
  """

  def __init__(self, window, size, position, n_frame, freq) -> None:
    """
    window (psychopy.visual.window): Psychopy window
    size (int): Size of the stimulation
    position (tuple): Position of stimulation on the screen
    n_frame (int): Number of frames for the stim to flicker (frequency = monitor_refresh_rate/n_frame)
    log_time (bool): Whether to log toggle times
    """

    self._window = window
    self._fr_rate = n_frame
    self._fr_counter = n_frame
    self._stim1 = visual.Circle(win=self._window, pos=position, size=size, radius=0.4, opacity=1)
    # self._stim2 = visual.Circle(win=self._window, pos=position, size=size, radius=0.4, opacity=1)
    self._toggle_flag = False
    self._freq = freq

  def draw(self):
    """Draw stimulation"""
    if self._fr_counter == 0:
        self._fr_counter = self._fr_rate
        if self._toggle_flag:
            self._stim1.draw()
        self._toggle_flag = not self._toggle_flag
    self._fr_counter -= 1

class OnlineSSVEP:

  def __init__(self, screen_refresh_rate=60):
    self.window = visual.Window([800,600], monitor="testMonitor", fullscr=True, allowGUI=True, screen=1, units='norm', color=[0.1,0.1,0.1])
    self.target_positions = [(-.6, -.6), (-.6, .6), (.6, .6), (.6, -.6)]
    self.stim_size = (0.6 * self.window.size[1]/self.window.size[0], 0.6)
    self.fr_rates = [5, 6, 7, 8] # 12Hz, 10Hz, 8.5Hz, 7.5Hz.
    self._freqs = [round(screen_refresh_rate / fr_no, 1) for fr_no in self.fr_rates]
    self.targets = []
    self.labels = []
  
  def display_stim(self):
    for fr_no, pos, freq in zip(self.fr_rates, self.target_positions, self._freqs):
      self.targets.append(Stimulus(
        window=self.window,
        size=self.stim_size,
        n_frame=fr_no,
        position=pos,
        freq=freq
      ))
      self.labels.append(visual.TextBox2(win=self.window, 
        text=f'{freq} Hz', 
        pos=(pos[0]+0.1,pos[1]+0.1)))
    
  def run_ssvep(self, duration: int):
    self.display_stim()
    start_time = time.time()

    print('Starting trial')
    while time.time() - start_time < duration:
      self.window.flip()
      for stim in self.targets:
        stim.draw()
      for label in self.labels:
          label.draw()
    
    self.window.close()
    print('Done trial')