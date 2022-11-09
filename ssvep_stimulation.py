import time
import numpy as np
from psychopy import visual, event

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
    log_time (bool): Whether to log toggle times
    """

    self._window = window
    self._fr_rate = n_frame
    self._fr_counter = n_frame
    self._stim1 = visual.Circle(win=self._window, pos=position, size=size, radius=0.4, opacity=1)
    # self._stim2 = visual.Circle(win=self._window, pos=position, size=size, radius=0.4, opacity=1)
    self._toggle_flag = False

  def draw(self):
    """Draw stimulation"""
    if self._fr_counter == 0:
        self._fr_counter = self._fr_rate
        if self._toggle_flag:
            self._stim1.draw()
        
        self._toggle_flag = not self._toggle_flag
    self._fr_counter -= 1

def main():
  targets = []
  target_positions = [(-.6, -.6), (-.6, .6), (.6, .6), (.6, -.6)]
  fr_rates = [5, 6, 7, 8] # 12Hz, 10Hz, 8.5Hz, 7.5Hz.
  window = visual.Window([800,600], monitor="testMonitor", fullscr=True, allowGUI=True, screen=1, units='norm', color=[0.1,0.1,0.1])
  stim_size = (0.6 * window.size[1]/window.size[0], 0.6)

  for fr_no, pos in zip(fr_rates, target_positions):
    targets.append(Stimulus(
      window=window,
      size=stim_size,
      n_frame=fr_no,
      position=pos
    ))
  
  duration = 5

  start_time = time.time()

  print('Starting trial')
  while time.time() - start_time < duration:
    window.flip()
    for stim in targets:
      stim.draw()
  
  window.close()
  print('Done trial')

if __name__ == '__main__':
  main()