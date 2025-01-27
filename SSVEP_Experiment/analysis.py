import numpy as np
from sklearn.cross_decomposition import CCA
from scipy import signal
import tensorflow as tf
import matplotlib.pyplot as plt

# index --- label on electrode --- actual position
# 1         FP1                    FP1
# 2         FP2                    FP2
# 3         T3                     PO3
# 4         T4                     PO4
# 5         O1                     O1
# 6         O2                     O2
# 7         FPz                    Oz
# 8         Pz                     POz
CLASSIFICATION_CHANNELS = [2, 3, 4, 5, 6, 7]
FATIGUE_CHANNELS = [0, 1]

class CNNAnalysis:
    """
    Convolutional Neural Network for SSVEP paradigm and fatigue estimation
    """
    def __init__(self, path, freqs, win_len, s_rate, nyq=125.0,lower=4,upper=40):
        """
        Args:
            path (str): Local path to saved model
            freqs (list): List of target frequencies
            win_len (float): Window length
            s_rate (int): Sampling rate of EEG signal
        """
        self.freqs = freqs
        self.win_len = win_len
        self.s_rate = s_rate
        self.model = tf.keras.models.load_model(path)
        self.input_shape = self.model.input_shape
        self.lower = lower
        self.upper = upper
        normal_cutoffs = [self.lower/nyq, self.upper/nyq]
        self.filter_vals = signal.butter(4, normal_cutoffs,btype="band",analog=False)
    
    def measure_fatigue(self, eeg):
        """
        estimate cognitive fatigue on window using bandpower ratio
        """

        # get alpha, beta, theta bands
        beta_bounds = 12, 30
        alpha_bounds = 8, 12
        theta_bounds = 4, 8

        freqs, psd = signal.welch(np.mean(eeg, axis=-1), fs=self.s_rate, nperseg=self.win_len*self.s_rate)
        beta_coeffs = psd[np.logical_and(freqs > beta_bounds[0], freqs < beta_bounds[1])]
        beta_power = np.sum(beta_coeffs)

        alpha_coeffs = psd[np.logical_and(freqs > alpha_bounds[0], freqs < alpha_bounds[1])]
        alpha_power = np.sum(alpha_coeffs)

        theta_coeffs = psd[np.logical_and(freqs > theta_bounds[0], freqs < theta_bounds[1])]
        theta_power = np.sum(theta_coeffs)

        # return theta_power, alpha_power, beta_power
        return (theta_power + alpha_power) / beta_power

    def analyse(self,eeg):
        pred = self.apply_CNN(eeg)
        fatigue = self.measure_fatigue(eeg[:, FATIGUE_CHANNELS])
        return pred, fatigue

    def apply_CNN(self,eeg,nyq=125.0):
        eeg = np.transpose(eeg)
        assert len(eeg.shape) == 2
        assert eeg.shape[0] < eeg.shape[1]
        
        comp_feats = []
        for channel in eeg:
            filtered = signal.filtfilt(
                self.filter_vals[0],
                self.filter_vals[1],
                channel
            )

            temp_fft = np.fft.fft(filtered,853) / len(channel)
            real = np.real(temp_fft)[self.lower:self.upper]
            imag = np.imag(temp_fft)[self.lower:self.upper]
            comp_feats.append(
                np.concatenate([real,imag],axis=0)
            )
        model_input = np.expand_dims(np.array(comp_feats),axis=2)
        model_input = np.expand_dims(model_input,axis=0)

        return list(self.model(model_input)[0])

class CCAAnalysis:
    """
    Canonical Correlation Analysis for SSVEP paradigm and fatigue estimation
    """
    def __init__(self, freqs, win_len, s_rate, n_harmonics=1):
        """
        Args:
            freqs (list): List of target frequencies
            win_len (float): Window length
            s_rate (int): Sampling rate of EEG signal
            n_harmonics (int): Number of harmonics to be considered
        """
        self.freqs = freqs
        self.win_len = win_len
        self.s_rate = s_rate
        self.n_harmonics = n_harmonics
        self.train_data = self._init_train_data()
        self.cca = CCA(n_components=1)

    def _init_train_data(self):
        t_vec = np.linspace(0, self.win_len, int(self.s_rate * self.win_len))
        targets = {}
        for freq in self.freqs:
            sig_sin, sig_cos = [], []
            for harmonics in range(self.n_harmonics):
                sig_sin.append(np.sin(2 * np.pi * harmonics * freq * t_vec))
                sig_cos.append(np.cos(2 * np.pi * harmonics * freq * t_vec))
            targets[freq] = np.array(sig_sin + sig_cos).T
        return targets

    def apply_cca(self, eeg):
        """Apply CCA analysis to EEG data and return scores for each target frequency

        Args:
            eeg (np.array): EEG array [n_samples, n_chan]

        Returns:
            list of scores for target frequencies
        """
        scores = []
        for key in self.train_data:
            sig_c, t_c = self.cca.fit_transform(eeg, self.train_data[key])
            scores.append(np.corrcoef(sig_c.T, t_c.T)[0, 1])
        return scores

    def measure_fatigue(self, eeg):
        """
        estimate cognitive fatigue on window using bandpower ratio
        """

        # get alpha, beta, theta bands
        beta_bounds = 12, 30
        alpha_bounds = 8, 12
        theta_bounds = 4, 8

        freqs, psd = signal.welch(np.mean(eeg, axis=-1), fs=self.s_rate, nperseg=self.win_len*self.s_rate)
        beta_coeffs = psd[np.logical_and(freqs > beta_bounds[0], freqs < beta_bounds[1])]
        beta_power = np.sum(beta_coeffs)

        alpha_coeffs = psd[np.logical_and(freqs > alpha_bounds[0], freqs < alpha_bounds[1])]
        alpha_power = np.sum(alpha_coeffs)

        theta_coeffs = psd[np.logical_and(freqs > theta_bounds[0], freqs < theta_bounds[1])]
        theta_power = np.sum(theta_coeffs)

        # return theta_power, alpha_power, beta_power
        return (theta_power + alpha_power) / beta_power

        
    def analyse(self, eeg):
        raw_cca_scores = self.apply_cca(eeg[:, CLASSIFICATION_CHANNELS])
        fatigue = self.measure_fatigue(eeg[:, FATIGUE_CHANNELS])

        return raw_cca_scores, fatigue

if __name__ == '__main__':
    freqs = [7, 10, 15, 12]
    t_len = 2
    s_rate = 250
    t_vec = np.linspace(0, t_len, s_rate * t_len)

    test_sig = np.sin(2 * np.pi * 10 * t_vec) + 0.05 * np.random.rand(len(t_vec))

    cca_analysis = CCAAnalysis(freqs=freqs, win_len=t_len, s_rate=s_rate, n_harmonics=2)
    r, f = cca_analysis.analyse(np.random.rand(500,8))

