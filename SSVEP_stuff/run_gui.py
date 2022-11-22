import PySimpleGUIQt as sg
from explorepy.explore import Explore
from explorepy.stream_processor import TOPICS
from ssvep_stimulation import OnlineSSVEP

device_name = 'Explore_84A1'
explore = Explore()
explore.connect(device_name=device_name)
explore.set_channels(channel_mask='11001111')
# explore.measure_imp()

sg.theme('Reddit')
# Everything inside the window
layout = [  [sg.Text(f'Mentalab Explore Device: {device_name}', font=('MS Sans Serif', 17, 'italics'))],
            [sg.Text('SSVEP simulation window', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Text('How long should the simulation be (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='30')],
            [sg.Text('EEG signal length to be analyzed (seconds)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='3')],
            [sg.Text('EEG sampling rate (Hz)?', font=('MS Sans Serif', 11)), sg.InputText(default_text='250')],
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
        analysis_type = values['analysis']

        experiment = OnlineSSVEP(60, signal_len, eeg_s_rate, analysis_type)

        # subscribe the experiment buffer to the EEG data stream
        explore.stream_processor.subscribe(callback=experiment.update_buffer, topic=TOPICS.raw_ExG)

        experiment.run_ssvep(ssvep_duration)

window.close()