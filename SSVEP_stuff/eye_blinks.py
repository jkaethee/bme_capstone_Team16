from explorepy.explore import Explore
from explorepy.stream_processor import TOPICS
import time

device_name = 'Explore_84A1'
explore = Explore()
explore.connect(device_name=device_name)

# explore.measure_imp()

explore.record_data(file_name='eye_blink_5sec', file_type='csv', do_overwrite=True, duration=125)

    
