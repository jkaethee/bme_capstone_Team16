![image](https://user-images.githubusercontent.com/47435952/200955114-f659fc55-7e4c-4f24-a0ee-d32de3b95df9.png)

## Situation Impact Statement
The objective is to design a proof-of-concept system with BCI-integrated wheelchair technology for quadriplegic persons that will measure cognitive fatigue and compensate by refining BCI parameters to reduce classification errors of standard wheelchair movement
commands.

## Description
This code repo will host files for SSVEP stimulation, EEG signal acquisiton, signal filtering, and signal classification.
The hardware used is [Mentalab's Explore device](https://mentalab.com/mobile-eeg/). 

## Installation
1. Follow the explorepy [installation guide](https://explorepy.readthedocs.io/en/latest/installation.html) 
2. Clone the repo
3. Run `python run_gui.py`


## Electrode Placement and Mapping
| **Electrode** | **Headset Label** | **Channel #**  |
|:-------------:|:-------------:|:-----:|
| FP1    | O1  | 1 |
| FP2    | O2  | 2 |
| T3     | PO3 | 3 |
| T4     | PO4 | 4 |
| --     | --  | 5 |
| --     | --  | 6 |
| FPz    | Oz  | 7 |
| Pz     | POz | 8 |

Dropout channels: 11001111
