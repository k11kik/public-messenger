"""
Docstring pour messenger_analysis.distribution.freq_over_fcp

* f/fcp distribution
"""
import numpy as np

from common import display, util, orbit


def get_representative_freqs_norm_from_spectrogram(
        times, # (n,)
        freqs_norm, # (m,)
        spectrogram, # (n, m)
        threshold_mean_intensity=100,
        n_mode=1,
        percentile_value=75,
):
    n, m = spectrogram.shape
    if len(times) != n or len(freqs_norm) != m:
        display.warning(f'shape error: spectrogram=({n}, {m}), times=({len(times)},), freqs_norm=({len(freqs_norm)},)')
        return
    
    display.info(f'{n_mode=}')

    freqs_norm_representative = []
    for i in range(len(times)):
        spectrogram_i = spectrogram[i, :]
        freqs_norm_representative_i = np.nan
        if n_mode == 1: # max -> 大きいnoiseを拾ってしまう可能性あり
            spectrogram_representative_i = np.nanmax(spectrogram_i)
            if spectrogram_representative_i < threshold_mean_intensity or np.isnan(spectrogram_representative_i):
                freqs_norm_representative.append(freqs_norm_representative_i)
            else:
                idx_representative = util.get_closest_idx(spectrogram_i, spectrogram_representative_i)
                freqs_norm_representative_i = freqs_norm[idx_representative]
                freqs_norm_representative.append(freqs_norm_representative_i)
        elif n_mode == 2: # percenttile
            spectrogram_representative_i = np.percentile(spectrogram_i, percentile_value)
            if spectrogram_representative_i < threshold_mean_intensity or np.isnan(spectrogram_representative_i):
                freqs_norm_representative.append(freqs_norm_representative_i)
            else:
                idx_representative = util.get_closest_idx(spectrogram_i, spectrogram_representative_i)
                freqs_norm_representative_i = freqs_norm[idx_representative]
                freqs_norm_representative.append(freqs_norm_representative_i)

    return np.array(freqs_norm_representative)



