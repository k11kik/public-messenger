import numpy as np
from common import display


def get_quality_flag_sampling_rate(times, target_rate=20, tolerance=0.1):
    """
    サンプリングレートに基づいてQuality Flagを生成する。
    
    Args:
        times (np.array): タイムスタンプの配列 (秒)
        target_rate (float): 基準とするサンプリング周波数 (Hz)
        tolerance (float): 許容誤差 (Hz)
        
    Returns:
        np.array: 20Hzなら0, それ以外（変動・欠損）なら1の整数配列
    """
    if len(times) < 2:
        return np.array([1] * len(times))

    dt = np.diff(times)
    
    rates = np.divide(1.0, dt, out=np.zeros_like(dt), where=dt != 0)

    is_target_rate_interval = np.abs(rates - target_rate) < tolerance
    # is_valid = np.zeros(len(times), dtype=bool)
    valid_forward = np.append(is_target_rate_interval, is_target_rate_interval[-1])
    valid_backward = np.insert(is_target_rate_interval, 0, is_target_rate_interval[0])
    
    # 両方のインターバルが適切である点のみを「0」とする (厳密な判定)
    # 片方でも良しとする場合は `logical_or` に変更してください
    full_target_condition = np.logical_and(valid_forward, valid_backward)
    
    quality_flag = np.where(full_target_condition, 0, 1)

    # quality_flag_forward = np.where(valid_forward, 0, 1)
    # quality_flag_backward = np.where(valid_backward, 0, 1)
    
    return quality_flag
    # return np.stack([quality_flag, quality_flag_forward, quality_flag_backward]).T


def detect_outliers(
        data,
        method='spike',
        threshold=3.0,
        info=True,
        threshold_mag=1e3,
        threshold_diff=100,
        window_size=5,
        min_pulse_len=2,    # 'pulse' 用：矩形波と見なす最小連続点数
        pulse_start_diff_factor=5 # 'pulse' 用：パルス前後の変化の急峻さの閾値係数
    ):
    if len(data) == 0:
        return data
    
    total_outliers = 0
    data_cleaned = np.copy(data)
    
    if method == 'magnitude':
        outliers = np.abs(data) > 100 * np.median(data)

    elif method == 'iqr':
        # IQR法による異常値検出
        Q1 = np.quantile(data_cleaned, .25)
        Q3 = np.quantile(data_cleaned, .75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        outliers = (data_cleaned < lower_bound) | (data_cleaned > upper_bound)
        
    elif method == 'zscore':
        # Z-score法による異常値検出
        z_scores = np.abs((data_cleaned - data.mean()) / data_cleaned.std())
        outliers = z_scores > threshold
        
    elif method == 'mad':
        # Median Absolute Deviation法による異常値検出
        median = np.nanmedian(data_cleaned)
        mad = np.nanmedian(np.abs(data_cleaned) - median)
        if mad == 0:
            modified_z_scores = np.zeros_like(data_cleaned, dtype=float)
        else:
            modified_z_scores = 0.6745 * (data_cleaned - median) / mad # 0.6745は正規分布に合わせるための係数
        
        outliers = np.abs(modified_z_scores) > threshold
    
    elif method == 'spike':
        # スパイクノイズ特化型検出
        # 1. 絶対値が非常に大きいスパイク (threshold_mag)
        outliers_mag = np.abs(data_cleaned) > threshold_mag

        # 2. 移動中央値からの逸脱 (近傍との差)
        # NaNを考慮した移動中央値
        # pandasのmoving windowは便利だが、numpyだけでやるなら手動実装かscipy.ndimage.median_filter
        # ここでは単純な移動中央値を実装（端の処理はパディングやスライスで対応）
        if window_size % 2 == 0:
            display.warning("Warning: window_size should be odd for 'spike' method. Adding 1.")
            window_size += 1 # 奇数に調整
        
        half_window = window_size // 2
        
        # 移動中央値を計算するための配列（端の処理）
        padded_data = np.pad(data_cleaned, (half_window, half_window), mode='edge')
        
        moving_median = np.zeros_like(data_cleaned, dtype=float)
        for i in range(len(data_cleaned)):
            # NaNを除外して中央値を計算
            window_values = padded_data[i : i + window_size]
            moving_median[i] = np.nanmedian(window_values)

        # 中央値からの絶対差が閾値を超える
        # np.abs(data_cleaned - moving_median) は、データ点と近傍中央値との差
        outliers_median_diff = np.abs(data_cleaned - moving_median) > threshold_diff
        
        # 3. 隣接点との急激な変化 (オプション、ノイズによっては有効)
        diff_data = np.abs(np.diff(data_cleaned))
        # outliers_diff_forward = np.zeros_like(data_cleaned, dtype=bool)
        # outliers_diff_backward = np.zeros_like(data_cleaned, dtype=bool)
        # if len(diff_data) > 0:
        #     outliers_diff_forward[:-1] = diff_data > threshold_diff
        #     outliers_diff_backward[1:] = diff_data > threshold_diff
        # outliers_diff = outliers_diff_forward | outliers_diff_backward
        outliers_diff = np.zeros_like(data_cleaned, dtype=bool)
        if data_cleaned[0] > threshold_mag:
            outliers_diff[0] = True
        outliers_diff[1:] = np.abs(diff_data) > threshold_diff

        # 論理ORで条件を結合
        # 非常に大きい値 OR 移動中央値から大きく外れる値
        outliers = outliers_mag | outliers_median_diff | outliers_diff # 必要に応じて diff も追加
        # outliers = outliers_mag | outliers_diff # 必要に応じて diff も追加
    
    elif method == 'pulse':
        # 矩形波ノイズ特化型検出
        
        # 1. 絶対値が閾値以上の点を候補とする
        high_mag_candidates = np.abs(data_cleaned) > threshold_mag
        
        # 2. 連続する異常値のグループを特定
        # Trueの連続を数える
        from itertools import groupby
        
        temp_outliers = np.zeros_like(data_cleaned, dtype=bool) # 一時的な異常値マスク

        i = 0
        while i < len(data_cleaned):
            if high_mag_candidates[i]:
                # 連続する高マグニチュード部分の開始
                pulse_start = i
                pulse_end = i
                # パルスの終わりを探す
                while pulse_end + 1 < len(data_cleaned) and high_mag_candidates[pulse_end + 1]:
                    pulse_end += 1
                
                current_pulse_len = pulse_end - pulse_start + 1

                if current_pulse_len >= min_pulse_len:
                    # 矩形波の候補を発見
                    
                    # 3. 前後のデータとの急峻な変化を確認
                    # パルス開始前の値
                    val_before_pulse = data_cleaned[pulse_start - 1] if pulse_start > 0 else np.nan
                    # パルス終了後の値
                    val_after_pulse = data_cleaned[pulse_end + 1] if pulse_end < len(data_cleaned) - 1 else np.nan
                    
                    # パルス中の平均または中央値
                    pulse_mean = np.mean(data_cleaned[pulse_start : pulse_end + 1])
                    
                    is_start_sharp = False
                    if not np.isnan(val_before_pulse):
                        if np.abs(pulse_mean - val_before_pulse) > threshold_diff:
                            is_start_sharp = True
                    else: # 開始点が配列の最初の場合、Sharpかどうかは決めにくい
                        is_start_sharp = True # とりあえずTrueとしておく

                    is_end_sharp = False
                    if not np.isnan(val_after_pulse):
                        if np.abs(pulse_mean - val_after_pulse) > threshold_diff:
                            is_end_sharp = True
                    else: # 終了点が配列の最後の場合
                        is_end_sharp = True # とりあえずTrueとしておく
                    
                    # 両端が急峻に変化していることを確認
                    if is_start_sharp and is_end_sharp:
                        # この連続する高マグニチュード部分を異常値としてマーク
                        temp_outliers[pulse_start : pulse_end + 1] = True
                
                i = pulse_end + 1 # 処理したパルス部分をスキップ
            else:
                i += 1 # 高マグニチュードではない場合、次の点へ

        outliers = temp_outliers
        
    else:
        display.warning(f"Unsupposed method: {method} -> No cleaning")
        outliers = None
    
    return outliers


def get_quality_flag_outliers(
        data
):
    is_outliers = detect_outliers(data)

    return np.where(is_outliers, 1, 0)


def get_quality_flag_mag(
        times,
        mag_norm
):
    quality_flag_outliers = get_quality_flag_outliers(mag_norm)
    quality_flag_sampling = get_quality_flag_sampling_rate(times, target_rate=20)

    quality_flag = np.stack([quality_flag_outliers, quality_flag_sampling]).T

    return quality_flag
