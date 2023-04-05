![image](https://user-images.githubusercontent.com/47435952/200955114-f659fc55-7e4c-4f24-a0ee-d32de3b95df9.png)

## Situation Impact Statement
The objective is to design a proof-of-concept system with BCI-integrated wheelchair technology for quadriplegic persons that will measure cognitive fatigue and compensate by refining BCI parameters to reduce classification errors of standard wheelchair movement
commands.

## Description

This code repo will host files for SSVEP stimulation, EEG signal acquisiton, signal filtering, and signal classification.

The code is built off explorepy opensource demo for SSVEP experiments:

https://github.com/Mentalab-hub/explorepy/tree/master/examples/ssvep_demo

## Installation
1. Follow the explorepy installation guide: https://explorepy.readthedocs.io/en/latest/installation.html
2. Clone the repo
3. Run `python run_gui.py`

<i> Note that it is best to install all the necessary packages in a virtual environment, personally I used Anaconda! </i>

## Electrode Placement and Mapping
| **Label on Electrode** | **Actual Position** | **Channel #**  |
|:-------------:|:-------------:|:-----:|
| FP1    | FP1  | 1 |
| FP2    | FP2  | 2 |
| T3     | PO3 | 3 |
| T4     | PO4 | 4 |
| O1     | O1  | 5 |
| O2     | O2  | 6 |
| FPz    | Oz  | 7 |
| Pz     | POz | 8 |
