import numpy as np
from common import pytplot, display
from ._spectrogram import stft_vec


def spectrogram_vec(
        var_mag_vec: str,
        window_size: int = 256,
        rate_overlap: float = .1,
        nyquist_freq=None
):
    # get data
    dat_mag_vec = pytplot.get_data(var_mag_vec)
    if dat_mag_vec is None:
        display.error('spec/spectrogram_vec', 'No data')
        return
    times, mag_vec = dat_mag_vec.times, dat_mag_vec.y

    # spectrogram
    dict_spectrogram = stft_vec(times, mag_vec, window_size=window_size, rate_overlap=rate_overlap, nyquist_freq=nyquist_freq)

    display.debug('spec', f'{dict_spectrogram['spectrogram_psd_x']=}')
    display.debug('spec', f'{dict_spectrogram['spectrogram_psd_y']=}')
    display.debug('spec', f'{dict_spectrogram['spectrogram_psd_z']=}')

    pytplot.store_data(f'{var_mag_vec}_x_dpwrspc', {'x': dict_spectrogram['times'], 'y': dict_spectrogram['spectrogram_x'], 'v': dict_spectrogram['freqs']})
    pytplot.store_data(f'{var_mag_vec}_y_dpwrspc', {'x': dict_spectrogram['times'], 'y': dict_spectrogram['spectrogram_y'], 'v': dict_spectrogram['freqs']})
    pytplot.store_data(f'{var_mag_vec}_z_dpwrspc', {'x': dict_spectrogram['times'], 'y': dict_spectrogram['spectrogram_z'], 'v': dict_spectrogram['freqs']})
    pytplot.store_data(f'{var_mag_vec}_x_dpwrspc_psd', {'x': dict_spectrogram['times'], 'y': dict_spectrogram['spectrogram_psd_x'], 'v': dict_spectrogram['freqs']})
    pytplot.store_data(f'{var_mag_vec}_y_dpwrspc_psd', {'x': dict_spectrogram['times'], 'y': dict_spectrogram['spectrogram_psd_y'], 'v': dict_spectrogram['freqs']})
    pytplot.store_data(f'{var_mag_vec}_z_dpwrspc_psd', {'x': dict_spectrogram['times'], 'y': dict_spectrogram['spectrogram_psd_z'], 'v': dict_spectrogram['freqs']})

    # psd abs
    psd_abs = np.sqrt(dict_spectrogram['spectrogram_psd_x'] ** 2 + dict_spectrogram['spectrogram_psd_y'] ** 2 + dict_spectrogram['spectrogram_psd_z'] ** 2)

    pytplot.store_data(f'{var_mag_vec}_psd_abs', {'x': dict_spectrogram['times'], 'y': psd_abs, 'v': dict_spectrogram['freqs']})
    return
