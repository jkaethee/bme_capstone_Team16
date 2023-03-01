import PySimpleGUIQt as sg
from explorepy.explore import Explore
from explorepy.stream_processor import TOPICS
from ssvep_stimulation import OnlineSSVEP, CarDrive, open_likert_window, sanity_check
import sys
import time

device_name = 'Explore_84A1'
refresh_rate = 60
arduino_flag = False
explore = Explore()
explore.connect(device_name=device_name)
sg.theme('Reddit')


# Everything inside the window
layout = [  [sg.Text(f'Mentalab Explore Device: {device_name}', font=('MS Sans Serif', 17, 'italics'))],
            [sg.Button('Sanity Check', button_color = ('white', '#52bf9b'))],
            [sg.Button('Check Impedance', button_color = ('white', '#52bf9b'))],
            [sg.Button('Arduino Test?', key='-Arduino-', button_color = ('white', 'red'))],
            [sg.Text('What would you like to do?', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Button('Data Collection', key='trials', button_color = ('white', '#9462a8'), font=('MS Sans Serif', 15, 'bold'))],
            [sg.Button('Car Navigation', key='car', button_color = ('white', '#9462a8'), font=('MS Sans Serif', 15, 'bold'))]]

trial_layout = [[sg.Text('SSVEP simulation window', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Text('Trial File Name?', font=('MS Sans Serif', 11)), sg.InputText(default_text='Trial_0', key='file_name')],
            [sg.Text('How many trials for each stimuli?', font=('MS Sans Serif', 11)), sg.InputText(default_text='1')],
            [sg.Text('EEG signal length to be analyzed (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='2')],
            [sg.Text('EEG sampling rate (Hz)?', font=('MS Sans Serif', 11)), sg.Combo(['250', '500', '1000'], default_value='250')],
            [sg.Text('Top left frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='12', key='top_left')],
            [sg.Text('Bottom left frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='10', key='bottom_left')],
            [sg.Text('Top right frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='8.5', key='top_right')],
            [sg.Text('Bottom right frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='7.5', key='bottom_right')],
            [sg.Text('Classification Method', font=('MS Sans Serif', 11)), sg.Combo(['CCA'], default_value='CCA', key='analysis')],
            [sg.Button('Start'), sg.Button('Cancel')] ]

car_layout = [[sg.Text('Car Navigation Window', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Text('Duration of Experiment (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='10')],
            [sg.Text('EEG signal length to be analyzed (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='2')],
            [sg.Text('EEG sampling rate (Hz)?', font=('MS Sans Serif', 11)), sg.Combo(['250', '500', '1000'], default_value='250')],
            [sg.Text('Forward Frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='12', key='top_left')],
            [sg.Text('Braking Frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='10', key='bottom_left')],
            [sg.Text('Turn Right Frequency  (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='8.5', key='top_right')],
            [sg.Text('Turn Left Frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='7.5', key='bottom_right')],
            [sg.Text('Classification Method', font=('MS Sans Serif', 11)), sg.Combo(['CCA'], default_value='CCA', key='analysis')],
            [sg.Button('Start'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('CorticoChair', layout, size=(500, 250), return_keyboard_events=True)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    events, values = window.read()
    if events == sg.WIN_CLOSED or events == 'Cancel': # if user closes window or clicks cancel
        break

    if events == 'Sanity Check':
        sanity_check(explore)

    if events == 'Check Impedance':
        explore.measure_imp()

    if events == '-Arduino-':
        
        if not arduino_flag:
            window['-Arduino-'].update(button_color =('white', 'green'))
            arduino_flag = True
        else:
            arduino_flag = False
            window['-Arduino-'].update(button_color =('white', 'red'))

    if events == 'trials':
        window_trial = sg.Window('Data Collection', trial_layout, size=(800, 300), return_keyboard_events=True)
        while True:
            trial_events, trial_values = window_trial.read()

            if trial_events == sg.WIN_CLOSED or trial_events == 'Cancel': # if user closes window or clicks cancel
                window_trial.close()
                break
            
            # If the user clicks Start or uses the 'Enter' button on their keyboard
            if trial_events == 'Start' or trial_events == 'special 16777220':

                # Check user fatigue levels prior to starting
                start_rating = open_likert_window("Pre-SSVEP")

                ssvep_trials = int(trial_values[0])
                signal_len = int(trial_values[1])
                eeg_s_rate = int(trial_values[2])
                explore.set_sampling_rate(sampling_rate=eeg_s_rate)

                freq_keys = ['top_left', 'bottom_left', 'top_right', 'bottom_right']
                fr_rates = []
                for freq_key in freq_keys:
                    fr_rates.append(round(refresh_rate/float(trial_values[freq_key])))
                analysis_type = trial_values['analysis']
                experiment = OnlineSSVEP(refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type, trial_values['file_name'], arduino_flag)

                # subscribe the experiment buffer to the EEG data stream
                explore.stream_processor.subscribe(callback=experiment.update_buffer, topic=TOPICS.raw_ExG)
                explore.record_data(file_name=trial_values['file_name'], file_type='csv', do_overwrite=True)
                start_time = time.time()
                experiment.run_ssvep(ssvep_trials, start_rating, start_time)
                explore.stop_recording()
    
    if events == 'car':
        window_car = sg.Window('Data Collection', car_layout, size=(800, 300), return_keyboard_events=True)
        while True:
            car_events, car_values = window_car.read()

            if car_events == sg.WIN_CLOSED or car_events == 'Cancel': # if user closes window or clicks cancel
                window_car.close()
                break

            # If the user clicks Start or uses the 'Enter' button on their keyboard
            if car_events == 'Start' or car_events == 'special 16777220':
                print(car_values)
                length = int(car_values[0])
                signal_len = int(car_values[1])
                eeg_s_rate = int(car_values[2])
                explore.set_sampling_rate(sampling_rate=eeg_s_rate)

                freq_keys = ['top_left', 'bottom_left', 'top_right', 'bottom_right']
                fr_rates = []
                for freq_key in freq_keys:
                    fr_rates.append(round(refresh_rate/float(car_values[freq_key])))
                analysis_type = car_values['analysis']
                experiment = CarDrive(refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type, arduino_flag)

                # subscribe the experiment buffer to the EEG data stream
                explore.stream_processor.subscribe(callback=experiment.update_buffer, topic=TOPICS.raw_ExG)
                start_time = time.time()
                experiment.drive_car(length, start_time)

window.close()
sys.exit(1)

