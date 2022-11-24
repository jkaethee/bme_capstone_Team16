import PySimpleGUIQt as sg
from explorepy.explore import Explore
from explorepy.stream_processor import TOPICS
from ssvep_stimulation import OnlineSSVEP
import math

device_name = 'Explore_84A1'
refresh_rate = 60
# explore = Explore()
# explore.connect(device_name=device_name)
# explore.set_channels(channel_mask='11001111')
# explore.measure_imp()

sg.theme('Reddit')
# Everything inside the window
layout = [  [sg.Text(f'Mentalab Explore Device: {device_name}', font=('MS Sans Serif', 17, 'italics'))],
            [sg.Text('SSVEP simulation window', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Text('How long should the simulation be (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='30')],
            [sg.Text('EEG signal length to be analyzed (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='3')],
            [sg.Text('EEG sampling rate (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='250')],
            [sg.Text('Top left frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='12', key='top_left')],
            [sg.Text('Bottom left frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='10', key='bottom_left')],
            [sg.Text('Top right frame frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='8.5', key='top_right')],
            [sg.Text('Bottom right frame frequency (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='7.5', key='bottom_right')],
            [sg.Text('Classification Method', font=('MS Sans Serif', 11)), sg.Combo(['CCA'], default_value='CCA', key='analysis')],
            [sg.Button('Start'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('SSVEP simulation', layout, size=(800, 300), return_keyboard_events=True)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    
    # If the user clicks Start or uses the 'Enter' button on their keyboard
    if event == 'Start' or event == 'special 16777220':
        ssvep_duration = int(values[0])
        signal_len = int(values[1])
        eeg_s_rate = int(values[2])
        freq_keys = ['top_left', 'bottom_left', 'top_right', 'bottom_right']
        fr_rates = []
        for freq_key in freq_keys:
            fr_rates.append(round(refresh_rate/float(values[freq_key])))
        analysis_type = values['analysis']

        experiment = OnlineSSVEP(refresh_rate, signal_len, eeg_s_rate, fr_rates, analysis_type)

        # subscribe the experiment buffer to the EEG data stream
        # explore.stream_processor.subscribe(callback=experiment.update_buffer, topic=TOPICS.raw_ExG)
        # explore.record_data(file_name='test', duration=ssvep_duration, file_type='csv', do_overwrite=True)
        experiment.run_ssvep(ssvep_duration)

window.close()