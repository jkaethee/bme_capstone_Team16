import PySimpleGUIQt as sg
from ssvep_stimulation import OnlineSSVEP

sg.theme('Reddit')

# Everything inside the window
layout = [  [sg.Text('SSVEP simulation window', font=('MS Sans Serif', 15, 'bold'))],
            [sg.Text('How long should the simulation be (seconds)?', font=('MS Sans Serif', 11)), sg.InputText()],
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
        experiment = OnlineSSVEP()
        experiment.run_ssvep(ssvep_duration)

window.close()