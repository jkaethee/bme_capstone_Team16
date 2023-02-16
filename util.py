import pandas as pd
from scipy import signal
import numpy as np

SAMPLE_RATE = 250

def parse_eeg(ground_truth_csv, raw_eeg_csv, window_start, window_end, use_time_offset=False):

    '''
    retrieve EEG epochs and labels from timestamped ground truth labels

    ground_truth_csv:   str path to ground truth csv 
    raw_eeg_csv:        str path to raw EEG data csv
    window_start:       start of window to use - seconds before prompt ends
    window_end :        end of window - seconds after prompt ends
    use_time_offset:    whether to use time correction. Should be True for
                        data from the Drive folder "Collected Data (without time correction)"

    ie if u want to have epochs of 2 seconds after the prompt ends, 
        window_start=0, window_end=2
    '''

    gt_df = pd.read_csv(ground_truth_csv)
    eeg_df = pd.read_csv(raw_eeg_csv)

    eeg_df['TimeStamp'] -= eeg_df['TimeStamp'][0]
    #gt_df = gt_df.rename({'trial_start' : 'TimeStamp'})

    if use_time_offset:
        # magic number to fix time offset
        eeg_df['TimeStamp'] -= 0.175

    label_map = sorted(list(gt_df['ground_truth'].unique()))

    epochs = []
    labels = []
    for _, row in gt_df.iterrows():
        label = label_map.index(row['ground_truth'])
        epoch_start = row['trial_start'] - window_start
        epoch_end = row['trial_start'] + window_end
        epoch = eeg_df[eeg_df['TimeStamp'].between(epoch_start, epoch_end)].to_numpy().T
        epoch = epoch[:, :int(epoch_end - epoch_start) * SAMPLE_RATE]

        epochs.append(epoch)
        labels.append(label)

    return epochs, labels

def main():
    eeg_pth = 'data/ben_pre_fatigue_feb1/Pre_fatigue_feb1_4sec_ExG.csv'
    gt_pth = 'data/ben_pre_fatigue_feb1/Pre_fatigue_feb1_4sec_trial_info.csv'

    parse_eeg(gt_pth, eeg_pth, window_start=2, window_end=2, use_time_offset=True)

if __name__ == '__main__':
    main()