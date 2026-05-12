import numpy as np
import os
from common import cdf, display
from .quality_flag import get_quality_flag_outliers, get_quality_flag_sampling_rate


def interpolate_small_gaps(times, data, is_invalid, max_gap_size=5):
    """
    NaNの連続区間を特定し、その個数が max_gap_size 以下の箇所のみ線形補間する。
    
    Args:
        times: 時間軸 (1D array)
        data: データ本体 (2D array: [time, components])
        is_invalid: NaNフラグ (1D bool array, Trueが欠損)
        max_gap_size: 補間を許可する最大の連続サンプル数
    """
    filled_data = data.copy()
    n_times = len(times)
    n_comps = data.shape[1]

    # 差分を使ってNaN区間の開始と終了を検出
    # padded_invalid: [False, ..., True, True, ..., False] のように前後を固める
    padded = np.concatenate(([False], is_invalid, [False]))
    diff = np.diff(padded.astype(int))
    starts = np.where(diff == 1)[0]    # NaN開始インデックス
    ends = np.where(diff == -1)[0]     # NaN終了インデックス (この手前までがNaN)

    for s, e in zip(starts, ends):
        gap_size = e - s
        
        # 1. 配列の端（最初や最後）の欠損は補間できないのでスキップ
        if s == 0 or e == n_times:
            continue
            
        # 2. 隙間が閾値以下の場合のみ補間処理を実行
        if gap_size <= max_gap_size:
            # 補間に使用する前後のインデックス
            idx_before = s - 1
            idx_after = e
            
            t0, t1 = times[idx_before], times[idx_after]
            dt = t1 - t0
            
            for c in range(n_comps):
                v0, v1 = filled_data[idx_before, c], filled_data[idx_after, c]
                
                # 線形補間: y = v0 + (v1 - v0) * (t - t0) / (t1 - t0)
                # 隙間部分の各点について計算
                t_gap = times[s:e]
                filled_data[s:e, c] = v0 + (v1 - v0) * (t_gap - t0) / dt
                
    return filled_data


def create_pl2_data(
        cdf_filepath,
        savecdf,
        max_gap_interpolate=5,
):
    if not os.path.exists(cdf_filepath):
        display.warning(f'Not found: {cdf_filepath}')
        return
    
    dict_data = cdf.cdffile_to_dict(cdf_filepath)
    times = dict_data['time']
    mag_mso = dict_data['mag']
    mag_norm = np.linalg.norm(mag_mso, axis=1)

    quality_flag_outliers = get_quality_flag_outliers(mag_norm)
    quality_flag_sampling = get_quality_flag_sampling_rate(times, target_rate=20)

    quality_flag = np.stack([quality_flag_outliers, quality_flag_sampling]).T

    # apply quality flag
    is_invalid = (quality_flag == 1).any(axis=1)

    if np.all(is_invalid):
        display.warning(f'All data points are invalid -> Skipping file creation.')
        return
    
    mag_mso_with_nan = mag_mso.copy()
    mag_mso_with_nan[is_invalid] = np.nan

    # interpolate small gaps
    mag_mso_interpolated = interpolate_small_gaps(
        times, 
        mag_mso_with_nan, 
        is_invalid, 
        max_gap_size=max_gap_interpolate
    )

    dict_return = {
        'times': times,
        'mag_mso': mag_mso_interpolated,
        'quality_flag': quality_flag
    }

    # savecdf
    cdf.dict_to_cdffile(dict_return, savecdf)
    
    return
