import numpy as np
import pandas as pd
from scipy import fft
from common import util


def _fft(times, data, window="hanning", positive_freq=False, info=False):
    """
    :return dict; freq, spec, specabs, powspec, psd
    """
    dt = np.mean(np.diff(times))
    time_total = times[-1] - times[0]
    nyquist_freq = .5 / dt  # Nyquist frequency
    dict_info = {
        'times': len(times),
        'data': len(data),
        'dt': f'{dt:.02} s',
        'total time': f'{time_total:.02} s',
        'Nyquist freq': f'{nyquist_freq}',
        'windwow': window,
    }

    len_data = len(data)

    # window
    if window == "hanning":
        w = np.hanning(len_data)  # ハニング窓
    else:  # no window
        w = np.ones_like(data)


    fft_data = fft.fft(data * w) / len_data  # [x]

    if positive_freq:
        freq = np.linspace(0, int(nyquist_freq), len_data//2)
        fft_data = fft_data[:len_data // 2]  # 正の周波数部分を抽出
        fft_data *= 2  # 負の周波数のエネルギー分
    else:
        fft_data = fft.fftshift(fft_data)
        freq = fft.fftfreq(len_data, dt)
        freq = fft.fftshift(freq)

    # 補正
    acf = 1 / (np.sum(w) / len_data)
    fft_data *= acf  # 補正 [x]

    if info:
        util.print_dict(dict_info, title='FFT information')


    fft_amp = np.abs(fft_data)  # amplitude
    power_spectrum = fft_amp ** 2  # [x^2]
    psd = power_spectrum * time_total  # [x^2/Hz]

    dict_return = {
        'freq': freq,
        'spec': fft_data,
        'specabs': fft_amp,
        'powspec': power_spectrum,
        'psd': psd
    }
    return dict_return


def _stft(
        times,
        data,
        window="hanning",
        window_size=256, rate_overlap=.1,
        info=False,
        positive_freq=True,
        nyquist_freq=None
):
    """
    :return: dict; times, freqs, spectrogram (len_times, len_freqs), spectrogram_psd
    """


    if rate_overlap < 0 or rate_overlap >= 1:
        raise ValueError("rate_overlap must be in the range of (0, 1)")

    if window_size >= len(data):
        window_size = int(len(data) / 10)
        print("window_size must be smaller than data length")
        # return None

    n_overlap = int(window_size * rate_overlap)
    step = window_size - n_overlap

    dt = np.mean(np.diff(times))

    if nyquist_freq is None:
        nyquist_freq = .5 / dt
    delta_t = window_size * dt  # time resolution

    if positive_freq:
        freq = np.linspace(0, int(nyquist_freq), window_size//2)
    else:
        freq = fft.fftfreq(window_size, dt)
        freq = fft.fftshift(freq)

    freq_res = freq[1] - freq[0]

    spectrogram = []
    spectrogram_psd = []
    time_midpoints = []

    # window ごとに処理
    for i in range(0, len(times) - window_size, step):
        times_for_fft = times[i:i+window_size]
        data_for_fft = data[i:i+window_size]
        dict_fft = _fft(times_for_fft, data_for_fft, positive_freq=positive_freq, window=window)
        spectrogram.append(dict_fft['spec'])
        spectrogram_psd.append(dict_fft['psd'])

        # セグメントの中央の時間を記録
        time_midpoint = times[i + window_size // 2]
        time_midpoints.append(time_midpoint)

    time_midpoints = np.array(time_midpoints)
    spectrogram = np.array(spectrogram)
    spectrogram_psd = np.array(spectrogram_psd)

    if info:
        dict_info = {
            'times': len(times),
            'data': len(data),
            'window': window,
            'window size': window_size,
            'rate overlap': rate_overlap,
            'positive freq': positive_freq,
            'dt': dt,
            'frequency res': freq_res,
            'time res': delta_t,
            'freqs': len(freq),
            'time_midpoints': len(time_midpoints),
            'spectrogram': spectrogram.shape,
            'spectrogram_psd': spectrogram_psd.shape
        }
        util.print_dict(dict_info, title='STFT information')

    dict_to_return = {
        'freqs': freq,
        'times': time_midpoints,
        'spectrogram': spectrogram,
        'spectrogram_psd': spectrogram_psd,
    }

    return dict_to_return


def stft_vec(
        times,
        data_vec,
        window_size=256, rate_overlap=.1,
        nyquist_freq=None
):
    """
    STFT 3D
    :param epoch: np.ndarray (n,)
    :param waveform_x: np.ndarray (n,)
    :param waveform_y: np.ndarray (n,)
    :param waveform_z: np.ndarray (n,)
    :param datatype: Default: spec
    :param window_size: window size of FFT
    :param rate_overlap: overlapping rate
    :return: freqs, times, spec_x, spec_y, spec_z, indices
    """
    data_x = data_vec[:, 0]
    data_y = data_vec[:, 1]
    data_z = data_vec[:, 2]
    dict_stft_x = _stft(times, data_x, window_size=window_size, rate_overlap=rate_overlap, nyquist_freq=nyquist_freq)
    dict_stft_y = _stft(times, data_y, window_size=window_size, rate_overlap=rate_overlap, nyquist_freq=nyquist_freq)
    dict_stft_z = _stft(times, data_z, window_size=window_size, rate_overlap=rate_overlap, nyquist_freq=nyquist_freq)

    dict_to_return = {
        'times': dict_stft_x['times'],
        'freqs': dict_stft_x['freqs'],
        'spectrogram_x': dict_stft_x['spectrogram'],
        'spectrogram_y': dict_stft_y['spectrogram'],
        'spectrogram_z': dict_stft_z['spectrogram'],
        'spectrogram_psd_x': dict_stft_x['spectrogram_psd'],
        'spectrogram_psd_y': dict_stft_x['spectrogram_psd'],
        'spectrogram_psd_z': dict_stft_x['spectrogram_psd'],
    }
    return dict_to_return
