import numpy as np
import pandas as pd
from common import pytplot, time, path, display

from .get_event_flag import get_event_flag
from ._extract import extract_event


def flatten_event_data(event_times, event_freqs, multiple_band=False):
    """
    イベントデータ（時間と周波数バンド）をCSV/DataFrameに適したロングフォーマットに変換する。

    Parameters:
    event_times (list of tuples): [(t_start, t_end), ...]
    event_freqs (list): [ [f_start, f_end], または [[f1_start, f1_end], [f2_start, f2_end], ...], ...]

    Returns:
    pandas.DataFrame: 整形されたイベントデータ
    """
    records = []
    
    for event_id, (time_span, freq_data) in enumerate(zip(event_times, event_freqs)):
        t_start, t_end = time.convert(time_span, frm='unix', into='str')

        if multiple_band:
            # event_freqs_regulated の出力構造を正規化
            if isinstance(freq_data[0], list) or isinstance(freq_data[0], np.ndarray):
                # 複数バンドのケース: [[f1_start, f1_end], [f2_start, f2_end], ...]
                bands = freq_data
            else:
                # 単一バンドのケース: [f_start, f_end]
                bands = [freq_data]
                
            # 各バンドを独立したレコードとして展開
            for band_index, (f_start, f_end) in enumerate(bands):
                records.append({
                    'start': t_start,
                    'end': t_end,
                    'band_index': band_index,
                    'freq_band_low': f_start,
                    'freq_band_high': f_end
                })
        
        else:
            if isinstance(freq_data[0], list) or isinstance(freq_data[0], np.ndarray):
                flattened_freq_list = []
                for i in range(len(freq_data)):
                    flattened_freq_list.append(freq_data[i][0])
                    flattened_freq_list.append(freq_data[i][1])
                band = [min(flattened_freq_list), max(flattened_freq_list)]
            
            else:
                band = freq_data

            records.append({
                'start': t_start,
                'end': t_end,
                'freq_band_low': band[0],
                'freq_band_high': band[1]
            })
            
    return pd.DataFrame(records)



def search_emic(
        var_psd_norm_x,
        var_psd_norm_y,
        var_psd_norm_z,
        var_polari,
        threshold_psd=1e3,
        threshold_ratio=10,
        threshold_polari=-.5,
        min_event_delta_time=60,
        min_event_delta_freq=.1,
        merge_timespan=60, # timespan to merge events [s]
):
    get_event_flag(
        var_psd_norm_x,
        var_psd_norm_y,
        var_psd_norm_z,
        var_polari,
        threshold_psd=threshold_psd,
        threshold_ratio=threshold_ratio,
        threshold_polari=threshold_polari
    )
    dat_flag_dense = pytplot.get_data('event_flag_dense')
    times = dat_flag_dense.times
    freqs = dat_flag_dense.v
    flag_dense = dat_flag_dense.y
    event_times, event_freqs = extract_event(
        times,
        freqs,
        flag_dense,
        min_event_delta_time=min_event_delta_time,
        min_event_delta_freq=min_event_delta_freq,
        merge_span=merge_timespan
    )

    # DataFrameに変換
    event_df = flatten_event_data(event_times, event_freqs, multiple_band=False)

    return event_df
