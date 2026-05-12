from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import numpy as np
import cdflib
# import pytplot
from common import pytplot, cdf, path
from common.base import display, mathpy

def all_paths_messenger(
    start_period: str,
    end_period: str,
    parent_dir_cdf_files: str = "messenger_data",
    basedir_cdf_files = None,
    display_cdf_paths: bool = False
):
    """
    指定期間のMESSENGER CDFファイルパスをリストで返す（hours, minutes単位もOK）
    例: messenger_data/mag_mso/2008/10/messenger_mag_mso_20081004.cdf
    :param start_period: 開始日時 (YYYY-mm-dd HH:MM:SS)
    :param end_period: 終了日時 (YYYY-mm-dd HH:MM:SS)
    :param parent_dir_cdf_files: CDFファイルの親ディレクトリ
    :param display_cdf_paths: パスをprintするか
    :return: CDFファイルパスのリスト
    """
    dt_start = datetime.strptime(start_period, '%Y-%m-%d %H:%M:%S')
    dt_end = datetime.strptime(end_period, '%Y-%m-%d %H:%M:%S')

    # 日単位で全ての該当日をリストアップ
    days = []
    dt = dt_start.replace(hour=0, minute=0, second=0)
    while dt <= dt_end:
        days.append(dt)
        dt += timedelta(days=1)

    paths = []
    for day in days:
        year = day.year
        month = day.month
        date_str = day.strftime('%Y%m%d')
        if basedir_cdf_files is None:
            file_path = os.path.join(
                parent_dir_cdf_files,
                "mag_mso",
                f"{year}",
                f"{month:02}",
                f"messenger_mag_mso_{date_str}.cdf"
            )
        else:
            file_path = os.path.join(
                basedir_cdf_files,
                f"{year}",
                f"{month:02}",
                f"messenger_mag_mso_{date_str}.cdf"
            )
        paths.append(file_path)

    # 期間に該当しないファイル（最初と最後の日の部分的な範囲）を除外する場合はここでフィルタ可能
    # ただし、MESSENGERのCDFは日単位なので、日単位で返すのが基本

    if display_cdf_paths:
        print("# cdf files to read:")
        for i, p in enumerate(paths):
            print(i, p)

    return paths


def all_paths_messenger_orb(
    start_period: str,
    end_period: str,
    basedir_orb,
    timeres=6,
    display_cdf_paths: bool = False
):
    """
    指定期間のMESSENGER CDFファイルパスをリストで返す（hours, minutes単位もOK）
    例: messenger_data/mag_mso/2008/10/messenger_mag_mso_20081004.cdf
    :param start_period: 開始日時 (YYYY-mm-dd HH:MM:SS)
    :param end_period: 終了日時 (YYYY-mm-dd HH:MM:SS)
    :param parent_dir_cdf_files: CDFファイルの親ディレクトリ
    :param display_cdf_paths: パスをprintするか
    :return: CDFファイルパスのリスト
    """
    dt_start = datetime.strptime(start_period, '%Y-%m-%d %H:%M:%S')
    dt_end = datetime.strptime(end_period, '%Y-%m-%d %H:%M:%S')

    # 日単位で全ての該当日をリストアップ
    days = []
    dt = dt_start.replace(hour=0, minute=0, second=0)
    while dt <= dt_end:
        days.append(dt)
        dt += timedelta(days=1)

    paths = []
    for day in days:
        year = day.year
        month = day.month
        date_str = day.strftime('%Y%m%d')
        file_path_search = os.path.join(
            basedir_orb,
            f"{year:04}",
            f"{month:02}",
            f"messenger_orb_{timeres}s_{date_str}.cdf"
        )
        file_path = path.glob_one(file_path_search)
        if file_path is None:
            continue
        else:
            paths.append(file_path)
    



    if display_cdf_paths:
        print("# cdf files to read:")
        for i, p in enumerate(paths):
            print(i, p)

    return paths

def load_and_store_messenger_data(
    cdf_paths,
    time_var='time',
    mag_var='mag',
    pos_var='pos',
    tplot_names={'mag': 'mag', 'pos': 'pos'},
    trange=None
):
    """
    複数のMESSENGER CDFファイルからデータを読み出し、pytplotに格納する
    :param cdf_paths: CDFファイルパスのリスト
    :param time_var: 時間変数名
    :param mag_var: 磁場変数名
    :param pos_var: 位置変数名
    :param tplot_names: tplotで使うデータ名のdict
    :param trange: [start, end] でフィルタ（オプション）
    :return: None
    """
    all_time = []
    all_mag = []
    all_pos = []

    for path in cdf_paths:
        if not os.path.exists(path):
            continue
        cdf = cdflib.CDF(path)
        time = cdf.varget(time_var)
        mag = cdf.varget(mag_var)
        pos = cdf.varget(pos_var)
        all_time.append(time)
        all_mag.append(mag)
        all_pos.append(pos)

    if not all_time:
        print("No valid CDF files found.")
        return

    # 連結
    time = np.concatenate(all_time)
    mag = np.concatenate(all_mag)
    pos = np.concatenate(all_pos)

    # trangeでフィルタ
    if trange is not None:
        from datetime import datetime
        t0 = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
        t1 = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
        t_dt = np.array([datetime.utcfromtimestamp(t) for t in time])
        mask = (t_dt >= t0) & (t_dt <= t1)
        time = time[mask]
        mag = mag[mask]
        pos = pos[mask]

    # pytplotに格納
    pytplot.store_data(tplot_names['mag'], {'x': time, 'y': mag})
    pytplot.store_data(tplot_names['pos'], {'x': time, 'y': pos})

    print(f"Loaded and stored {len(time)} points to pytplot.")

def load_messenger_to_tplot_by_trange(
    trange,
    parent_dir_cdf_files="messenger_data",
    time_var='time',
    mag_var='mag',
    pos_var='pos',
    tplot_names={'mag': 'mag', 'pos': 'pos'},
    display_cdf_paths=False
):
    """
    trangeで指定した期間のMESSENGER CDFデータをpytplotに格納する
    :param trange: ["YYYY-mm-dd HH:MM:SS", "YYYY-mm-dd HH:MM:SS"]
    :param parent_dir_cdf_files: CDFファイルの親ディレクトリ
    :param time_var, mag_var, pos_var: 変数名
    :param tplot_names: tplotで使うデータ名のdict
    :param display_cdf_paths: パスをprintするか
    :return: None
    """
    if len(trange) != 2:
        raise ValueError("trange must be a list of [start, end]")

    paths = all_paths_messenger(
        trange[0], trange[1],
        parent_dir_cdf_files=parent_dir_cdf_files,
        display_cdf_paths=display_cdf_paths
    )
    load_and_store_messenger_data(
        paths,
        time_var=time_var,
        mag_var=mag_var,
        pos_var=pos_var,
        tplot_names=tplot_names,
        trange=trange
    )


def detect_and_clean_outliers(
        data,
        method='iqr',
        threshold=3.0,
        info=True,
        threshold_mag=1e3,
        threshold_diff=100,
        window_size=5,
        min_pulse_len=2,    # 'pulse' 用：矩形波と見なす最小連続点数
        pulse_start_diff_factor=5 # 'pulse' 用：パルス前後の変化の急峻さの閾値係数
    ):
    """
    磁場データの異常値を検出してNaNに置き換える
    
    Parameters:
    df (pandas.DataFrame): データフレーム
    columns (list): 異常値検出対象の列名
    method (str): 異常値検出方法 ('iqr', 'zscore', 'mad')
    threshold (float): 異常値判定の閾値
    
    Returns:
    pandas.DataFrame: 異常値をNaNに置き換えたデータフレーム
    """
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
        display.warning('getdata/outliers', f"Unsupposed method: {method} -> No cleaning")
        outliers = None
    
    if outliers is not None:
        outlier_count = outliers.sum()
        total_outliers += outlier_count
    else:
        outlier_count = 0
    
    if outlier_count > 0:
        if info:
            print(f"outlier count: {outlier_count} ({outlier_count/len(data_cleaned)*100:.2f}%)")
            print(f"  range: [{data_cleaned.min():.2f}, {data_cleaned.max():.2f}]")
        
        # 異常値をNaNに置き換え
        data_cleaned[outliers] = np.nan
        
        # 異常値の統計情報
        outlier_values = data[outliers]
        print(f"  outliers: mean={outlier_values.mean():.2f}, std={outlier_values.std():.2f}")
    else:
        pass

    
    
    return data_cleaned


def messenger_mag(
    trange: list,
    parent_dir_cdf_files="messenger_data",
    basedir_cdf_files=None,
    info: bool = False
):
    if len(trange) != 2:
        raise ValueError("trange must be a list of [start, end]")

    paths = all_paths_messenger(
        trange[0], trange[1],
        parent_dir_cdf_files=parent_dir_cdf_files,
        basedir_cdf_files=basedir_cdf_files,
        display_cdf_paths=info
    )

    all_time = []
    all_mag = []

    for path in paths:
        if not os.path.exists(path):
            continue
        cdf = cdflib.CDF(path)
        time = cdf.varget('time')
        mag = cdf.varget('mag')
        all_time.append(time)
        all_mag.append(mag)

    if not all_time:
        print("No valid CDF files found.")
        return

    # 連結
    times = np.concatenate(all_time)
    mag = np.concatenate(all_mag)

    # trangeでフィルタ
    if trange is not None:
        t0 = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
        t1 = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
        t_dt = np.array([datetime.utcfromtimestamp(t) for t in times])
        mask = (t_dt >= t0) & (t_dt <= t1)
        times = times[mask]
        mag = mag[mask]
    
    # magnetic field norm
    mag_norm = np.sqrt(mag[:, 0] ** 2 + mag[:, 1] ** 2 + mag[:, 2] ** 2)
    # pytplot.store_data('mag_norm_before_clean', {'x': times, 'y': mag_norm})
    
    # clean mag data
    if info:
        display.current_time_comment(comment='clean')
    method = 'spike'
    mag_norm_cleaned = detect_and_clean_outliers(mag_norm, info=info, method=method)
    # pytplot.store_data('mag_norm_cleaned', {'x': times, 'y': mag_norm_cleaned})

    # moving average
    if info:
        display.current_time_comment(comment='moving average')
    mag_norm_cleaned_ave = mathpy.moving_average(mag_norm_cleaned, 100)
    diff_from_ave = mag_norm_cleaned - mag_norm_cleaned_ave

    diff_from_ave_cleaned = detect_and_clean_outliers(diff_from_ave, method='mad', threshold=100, info=info)
    indices_invalid = np.isnan(diff_from_ave_cleaned)
    mag_norm_cleaned[indices_invalid] = np.nan

    # median = np.nanmedian(diff_from_ave)
    # mad = np.nanmedian(np.abs(diff_from_ave - median))

    # # MADが0の場合の対策
    # if mad == 0:
    #     modified_z_scores = np.zeros_like(diff_from_ave, dtype=float)
    # else:
    #     modified_z_scores = 0.6745 * (diff_from_ave - median) / mad # 0.6745は正規分布に合わせるための係数

    # threshold_mad = 100 # Z-scoreと同様に2, 2.5, 3 などが使われる

    # outliers_mad = np.abs(modified_z_scores) > threshold_mad

    # pytplot.store_data('modified_z_scores', {'x': times, 'y': modified_z_scores})

    # mag_norm_cleaned[outliers_mad] = np.nan

    # outliers = diff_from_ave > np.nanmedian(diff_from_ave)
    # pytplot.store_data('mag_norm_ave', {'x': times, 'y': mag_norm_cleaned_ave})
    # pytplot.store_data('diff_from_ave', {'x': times, 'y': diff_from_ave})


    mag_x = mag[:, 0]
    mag_y = mag[:, 1]
    mag_z = mag[:, 2]
    mag_x[np.isnan(mag_norm_cleaned)] = np.nan
    mag_y[np.isnan(mag_norm_cleaned)] = np.nan
    mag_z[np.isnan(mag_norm_cleaned)] = np.nan
    mag_cleaned = np.stack([mag_x, mag_y, mag_z], axis=1)
    
    # store data
    pytplot.store_data('mag', {'x': times, 'y': mag_cleaned})
    pytplot.store_data('mag_norm', {'x': times, 'y': mag_norm_cleaned})

    return


def messenger_orb_orig(
    trange: list,
    parent_dir_cdf_files="messenger_data",
    info: bool = False,
    basedir_cdf_files=None,
):
    if len(trange) != 2:
        raise ValueError("trange must be a list of [start, end]")

    paths = all_paths_messenger(
        trange[0], trange[1],
        parent_dir_cdf_files=parent_dir_cdf_files,
        display_cdf_paths=info,
        basedir_cdf_files=basedir_cdf_files
    )

    all_time = []
    all_pos = []

    for path in paths:
        if not os.path.exists(path):
            continue
        cdf = cdflib.CDF(path)
        time = cdf.varget('time')
        pos = cdf.varget('pos')
        all_time.append(time)
        all_pos.append(pos)

    if not all_time:
        print("No valid CDF files found.")
        return

    # 連結
    times = np.concatenate(all_time)
    pos = np.concatenate(all_pos)

    # trangeでフィルタ
    if trange is not None:
        t0 = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
        t1 = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
        t_dt = np.array([datetime.utcfromtimestamp(t) for t in times])
        mask = (t_dt >= t0) & (t_dt <= t1)
        times = times[mask]
        pos = pos[mask]
    
    pytplot.store_data('pos', {'x': times, 'y': pos})

    return


def messenger_orb(
    trange: list,
    basedir_orb,
    info: bool = False,
):
    if len(trange) != 2:
        raise ValueError("trange must be a list of [start, end]")

    paths = all_paths_messenger_orb(
        trange[0], trange[1],
        basedir_orb=basedir_orb,
        display_cdf_paths=info,
    )

    if len(paths) == 0:
        display.warning(f'No orb data: {trange=}, {basedir_orb=}')
        return

    dict_data = cdf.read_and_combine_cdf_files(
        paths,
        ['times', 'orb_mso', 'orb_polar', 'orb_rmlatmlt']
    )

    pytplot.store_data('orb_mso', {'x': dict_data['times'], 'y': dict_data['orb_mso']})
    pytplot.store_data('orb_polar', {'x': dict_data['times'], 'y': dict_data['orb_polar']})
    pytplot.store_data('orb_rmlatmlt', {'x': dict_data['times'], 'y': dict_data['orb_rmlatmlt']})
    
    # all_time = []
    # all_pos = []

    # for path in paths:
    #     if not os.path.exists(path):
    #         continue
    #     cdf = cdflib.CDF(path)
    #     time = cdf.varget('time')
    #     pos = cdf.varget('pos')
    #     all_time.append(time)
    #     all_pos.append(pos)

    # if not all_time:
    #     print("No valid CDF files found.")
    #     return

    # 連結
    # times = np.concatenate(all_time)
    # pos = np.concatenate(all_pos)

    # clip by trange
    pytplot.timeclip('orb_mso', trange, 'orb_mso', replace=True)
    pytplot.timeclip('orb_polar', trange, 'orb_polar', replace=True)
    pytplot.timeclip('orb_rmlatmlt', trange, 'orb_rmlatmlt', replace=True)


    # if trange is not None:
    #     t0 = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
    #     t1 = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
    #     t_dt = np.array([datetime.utcfromtimestamp(t) for t in times])
    #     mask = (t_dt >= t0) & (t_dt <= t1)
    #     times = times[mask]
    #     pos = pos[mask]
    
    # pytplot.store_data('pos', {'x': times, 'y': pos})

    return