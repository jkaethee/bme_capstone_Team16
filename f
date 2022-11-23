import PySimpleGUIQt as sg
from explorepy.explore import Explore
from explorepy.stream_processor import TOPICS
from ssvep_stimulation import OnlineSSVEP

device_name = 'Explore_84A1'
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
            [sg.Text('Top left frame divisor ?', font=('MS Sans Serif', 11)), sg.InputText(default_text='5', key='top_left'), sg.Text('', key='-TL-')],
            [sg.Text('Bottom left frame divisor ?', font=('MS Sans Serif', 11)), sg.InputText(default_text='6', key='bottom_left'), sg.Text('', key='-BL-')],
            [sg.Text('Top right frame divisor ?', font=('MS Sans Serif', 11)), sg.InputText(default_text='7', key='top_right'), sg.Text('', key='-TR-')],
            [sg.Text('Bottom right frame divisor ?', font=('MS Sans Serif', 11)), sg.InputText(default_text='8', key='bottom_right'), sg.Text('', key='-BR-')],
            [sg.Text('Classification Method', font=('MS Sans Serif', 11)), sg.Combo(['CCA'], default_value='CCA', key='analysis')],
            [sg.Button('Start'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('SSVEP simulation', layout, size=(800, 300), return_keyboard_events=True)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if type(values['top_left']) != '':
        window['-TL-'].update(f"{60/int(values['top_left'])} Hz")
    if type(values['bottom_left']) != 'int':
        window['-BL-'].update(f"{60/int(values['bottom_left'])} Hz")
    if type(values['top_right']) != 'int':
        window['-TR-'].update(f"{60/int(values['top_right'])} Hz")
    if type(values['bottom_right']) != 'int':
        window['-BR-'].update(f"{60/int(values['bottom_right'])} Hz")

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    
    # If the user clicks Start or uses the 'Enter' button on their keyboard
    if event == 'Start' or event == 'special 16777220':
        ssvep_duration = int(values[0])
        signal_len = int(values[1])
        eeg_s_rate = int(values[2])
        fr_rates = [values['top_left'], values['bottom_left'], values['top_right'], values['bottom_right']]
        analysis_type = values['analysis']

        experiment = OnlineSSVEP(60, signal_len, eeg_s_rate, fr_rates, analysis_type)

        # subscribe the experiment buffer to the EEG data stream
        # explore.stream_processor.subscribe(callback=experiment.update_buffer, topic=TOPICS.raw_ExG)
        # explore.record_data(file_name='test', duration=ssvep_duration, file_type='csv', do_overwrite=True)
        experiment.run_ssvep(ssvep_duration)

window.close()