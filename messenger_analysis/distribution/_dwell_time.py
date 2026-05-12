import numpy as np
import os
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from spacepy import pycdf
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from glob import glob
from common import pytplot, display, path, util, time, cdf, orbit
from common.distribution import rmlatmlt_meshgrid
from messenger_analysis import getdata

def get_dwell_time(
        trange,
        basedir_orb,
        outcdf=False,
        save_cdf=None,
        delta_t_sec=None, # delta time of orb data
        info=True,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
        rmlat_whole=False
):
    getdata.messenger_orb(trange, basedir_orb=basedir_orb)
    # dat_orb = pytplot.get_data('pos')
    # orb = dat_orb.y / 2439.7
    # pytplot.store_data('pos', {'x': dat_orb.times, 'y': orb}, replace=True)
    # orbit.xyz2polar('pos', to='polar')
    # orbit.rmlatmlt2polar('pos_polar', to='rmlatmlt', varname_out='orb_rmlatmlt')
    dict_orb_meshgrid = rmlatmlt_meshgrid(
        'orb_rmlatmlt',
        outcdf=outcdf,
        save_cdf=save_cdf,
        delta_t_sec=delta_t_sec,
        info=info,
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        rmlat_whole=rmlat_whole
    )
    
    return dict_orb_meshgrid


def create_ref_dwell_cdf(
        trange,
        basedir_orb,
        basedir_savecdf=None,
        parent_dir_save_cdf='',
        savename='ref_dwell',
        delta_t_sec=None,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
        rmlat_whole=False
):
    time_list = time.make_time_list(trange, 1, 'months')
    if basedir_savecdf is None:
        dir_savecdf = os.path.join(parent_dir_save_cdf, f'orb/{savename}/1month')
    else:
        dir_savecdf = basedir_savecdf
    loop_start_time = datetime.now()
    for i, trange_i in enumerate(time_list):
        print(f'{trange_i=}')
        try:
            pytplot.del_data()
            display.progress_bar(i, len(time_list), loop_start_time)
            dt_start = time.convert(trange_i[0], frm='str', into='datetime')
            savecdf = os.path.join(dir_savecdf, f'{dt_start.year:04}/messenger_orb_{savename}_{dt_start.year:04}{dt_start.month:02}.cdf')

            get_dwell_time(
                trange_i,
                basedir_orb=basedir_orb,
                outcdf=True,
                save_cdf=savecdf,
                delta_t_sec=delta_t_sec,
                info=False,
                r_bins=r_bins,
                mlt_bins=mlt_bins,
                mlat_bins=mlat_bins,
                rmlat_whole=rmlat_whole
            )
        except Exception as e:
            print(f'Eroor: {e}')

    return


def get_dwell_time_trange_list(
        trange_list,
        basedir_orb,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
        rmlat_whole=False
):
    """
    Return
    -----
    dict: 
    * 'mesh_theta_rmlt'
    * 'mesh_r_rmlt'
    * 'rmlt_grid'
    * 'mesh_theta_rmlat'
    * 'mesh_r_rmlat'
    * 'rmlat_grid'
    """
    dict_orb_meshgrid = None

    
    
    start_loop_time = datetime.now()
    for i, trange_i in enumerate(trange_list):
        display.progress_bar(i, len(trange_list), start_loop_time)
        pytplot.del_data()
        # 個別の期間の滞在時間を計算
        dict_orb_meshgrid_i = get_dwell_time(
            trange_i,
            basedir_orb,
            info=False,
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins,
            rmlat_whole=rmlat_whole,
            delta_t_sec=6
        )

        if dict_orb_meshgrid_i is None:
            print(f"Warning: Skipping time range {i+1} ({trange_i[0]} to {trange_i[1]}) due to error in get_dwell_time.")
            continue
        
        if dict_orb_meshgrid is None:
            # 最初の期間: 全期間合計用の辞書を初期化
            dict_orb_meshgrid = dict_orb_meshgrid_i
        else:
            # 2回目以降: グリッドデータのみを加算
            try:
                # rmlt_grid (R-MLT空間の滞在時間) を加算
                dict_orb_meshgrid['rmlt_grid'] += dict_orb_meshgrid_i['rmlt_grid']
                # rmlat_grid (R-MLAT空間の滞在時間) を加算
                dict_orb_meshgrid['rmlat_grid'] += dict_orb_meshgrid_i['rmlat_grid']
                dict_orb_meshgrid['rmlt_grid_count'] += dict_orb_meshgrid_i['rmlt_grid_count']
                dict_orb_meshgrid['rmlat_grid_count'] += dict_orb_meshgrid_i['rmlat_grid_count']
            except Exception as e:
                print(f"Error summing grid data for trange {i}: {e}")
                # グリッド形状が異なるなど致命的なエラーの場合は処理を中断
                return {} 
                
    if dict_orb_meshgrid is None:
        print("Error: No data was successfully processed from trange_list.")
        return {} # データがない場合は空の辞書を返却

    return dict_orb_meshgrid


def get_trange_list_from_csv(
        csv_filepath
):
    """
    CSVファイルから 'start' と 'end' の列を読み込み、
    [[start_time_0, end_time_0], [start_time_1, end_time_1], ...] 形式の
    期間リスト (trange_list) を作成して返します。

    Args:
        csv_filepath (str): 読み込むCSVファイルのパス。

    Returns:
        Optional[List[List[str]]]: 期間リスト、またはファイル読み込み失敗時は None。
    """
    try:
        # CSVを読み込みます。ヘッダーは1行目にあると仮定します。
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"Error: File not found at {csv_filepath}")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

    # 必要な列が存在するかチェック
    required_columns = ['start', 'end']
    if not all(col in df.columns for col in required_columns):
        print(f"Error: CSV must contain both 'start' and 'end' columns. Found columns: {list(df.columns)}")
        return None

    # 'start' と 'end' の列を選択し、それらをNumPy配列に変換した後、最終的なリストのリストに変換します。
    # この形式は [ [start_time, end_time], [start_time, end_time], ... ] となります。
    trange_list = df[required_columns].values.tolist()
    
    return trange_list


def get_trange_list_from_csvs(
        csv_file_list
):
    trange_list = None
    for csv_file in csv_file_list:
        trange_list_i = get_trange_list_from_csv(csv_file)
        if trange_list_i is None:
            continue
        else:
            if trange_list is None:
                trange_list = trange_list_i
            else:
                trange_list.extend(trange_list_i)
            
    return trange_list



def get_dwell_time_cdf_files(
        list_cdf_filepaths,
        r_bins,
        mlt_bins,
        mlat_bins,
        rmlat_whole=False,
        info=True,
):
    # check cdf file paths
    paths = sorted(list_cdf_filepaths)

    # 存在しないfile pathを削除
    path_not_exist = []
    for i, filepath in enumerate(paths):
        if not os.path.exists(filepath):
            path_not_exist.append(filepath)
            display.warning(f'the file does not exist: {filepath}')

    [paths.remove(i) for i in path_not_exist]
    list_cdf_filepaths = paths

    if len(list_cdf_filepaths) == 0:
        display.warning('No cdf file to read')
        return None

    else:
        print(f"number of cdf files to read: {len(list_cdf_filepaths)}")
    

    ref_cdf_filepath = list_cdf_filepaths[0]
    mesh_theta_rmlt = cdf.get_data(ref_cdf_filepath, 'mesh_theta_rmlt')
    mesh_r_rmlt = cdf.get_data(ref_cdf_filepath, 'mesh_r_rmlt')
    rmlt_grid = cdf.get_data(ref_cdf_filepath, 'rmlt_grid')
    rmlt_grid_count = cdf.get_data(ref_cdf_filepath, 'rmlt_grid_count')
    mesh_theta_rmlat = cdf.get_data(ref_cdf_filepath, 'mesh_theta_rmlat')
    mesh_r_rmlat = cdf.get_data(ref_cdf_filepath, 'mesh_r_rmlat')
    rmlat_grid = cdf.get_data(ref_cdf_filepath, 'rmlat_grid')
    rmlat_grid_count = cdf.get_data(ref_cdf_filepath, 'rmlat_grid_count')
    
    loop_start_time = datetime.now()
    for i, cdf_filepath in enumerate(list_cdf_filepaths):
        if info:
            display.progress_bar(i, len(list_cdf_filepaths), loop_start_time)
        rmlt_grid_i = cdf.get_data(cdf_filepath, 'rmlt_grid')
        rmlat_grid_i = cdf.get_data(cdf_filepath, 'rmlat_grid')
        rmlt_grid_count_i = cdf.get_data(cdf_filepath, 'rmlt_grid_count')
        rmlat_grid_count_i = cdf.get_data(cdf_filepath, 'rmlat_grid_count')

        rmlt_grid = rmlt_grid + rmlt_grid_i
        rmlat_grid = rmlat_grid + rmlat_grid_i
        rmlt_grid_count = rmlt_grid_count + rmlt_grid_count_i
        rmlat_grid_count = rmlat_grid_count + rmlat_grid_count_i
    
    return {
        'mesh_theta_rmlt': mesh_theta_rmlt,
        'mesh_r_rmlt': mesh_r_rmlt,
        'rmlt_grid': rmlt_grid,
        'rmlt_grid_count': rmlt_grid_count,
        'mesh_theta_rmlat': mesh_theta_rmlat,
        'mesh_r_rmlat': mesh_r_rmlat,
        'rmlat_grid': rmlat_grid,
        'rmlat_grid_count': rmlat_grid_count,
    }
    # else:
    #     display.error('To be deleted')
    #     return get_dwell_time_cdf_files_interp(
    #         list_cdf_filepaths,
    #         r_bins,
    #         mlt_bins,
    #         mlat_bins,
    #         info,
    #         rmlat_whole=rmlat_whole
    #     )


def _bins_to_centers(bins: np.ndarray) -> np.ndarray:
    """ビンの境界配列から中心座標を計算します。"""
    return (bins[:-1] + bins[1:]) / 2.0

def _bins_to_mesh_rmlt(r_bins: np.ndarray, mlt_bins: np.ndarray):
    """R-MLTプロット用のメッシュ座標を生成します。"""
    # MLT (0-24) を角度 (0-2*pi) に線形マッピング (境界定義)
    theta_rmlt_rad = (mlt_bins / 24.0) * (2 * np.pi)
    # pcolormeshの境界メッシュを生成
    mesh_theta_rmlt, mesh_r_rmlt = np.meshgrid(theta_rmlt_rad, r_bins)
    return mesh_theta_rmlt, mesh_r_rmlt

def _bins_to_mesh_rmlat(r_bins: np.ndarray, mlat_bins: np.ndarray, rmlat_whole=False):
    """R-MLATプロット用のメッシュ座標を生成します。"""
    if rmlat_whole:
        dayside_theta = np.deg2rad(180 - mlat_bins) 
        nightside_theta = np.deg2rad(mlat_bins[::-1]) 
        full_theta_mlat = np.concatenate([dayside_theta[:-1], nightside_theta])
        mesh_theta_rmlat, mesh_r_rmlat = np.meshgrid(full_theta_mlat, r_bins)
    else:
        # MLAT (-90 - 90) を角度 (ラジアン) に変換 (境界定義)
        theta_rmlat_rad = np.deg2rad(mlat_bins)
        # pcolormeshの境界メッシュを生成
        mesh_theta_rmlat, mesh_r_rmlat = np.meshgrid(theta_rmlat_rad, r_bins)

    return mesh_theta_rmlat, mesh_r_rmlat


def get_dwell_time_cdf_files_interp(
        list_cdf_filepaths,
        r_bins: np.ndarray,
        mlt_bins: np.ndarray,
        mlat_bins: np.ndarray,
        info: bool,
        rmlat_whole=False
):
    
    # ----------------------------------------------------------------------
    # 1. 出力用メッシュとグリッドの準備
    # ----------------------------------------------------------------------
    # 決定されたビンから出力用のメッシュグリッドを生成 (境界定義)
    mesh_theta_rmlt, mesh_r_rmlt = _bins_to_mesh_rmlt(r_bins, mlt_bins)
    mesh_theta_rmlat, mesh_r_rmlat = _bins_to_mesh_rmlat(r_bins, mlat_bins, rmlat_whole=rmlat_whole)
    
    # 滞在時間グリッドの初期化
    rmlt_grid = np.zeros((r_bins.size - 1, mlt_bins.size - 1), dtype=np.float64)
    if rmlat_whole:
        rmlat_grid = np.zeros((r_bins.size - 1, 2 * (mlat_bins.size - 1)), dtype=np.float64)
    else:
        rmlat_grid = np.zeros((r_bins.size - 1, mlat_bins.size - 1), dtype=np.float64)

    # 補間処理のためのターゲット座標の中心を計算
    target_r_centers = _bins_to_centers(r_bins)
    target_mlt_centers = _bins_to_centers(mlt_bins)
    target_mlat_centers = _bins_to_centers(mlat_bins)
    
    # ターゲットグリッドの座標メッシュを生成（補間用）
    target_mlt_mesh, target_r_mesh_rmlt = np.meshgrid(target_mlt_centers, target_r_centers)
    target_mlat_mesh, target_r_mesh_rmlat = np.meshgrid(target_mlat_centers, target_r_centers) 

    expected_rmlt_shape = rmlt_grid.shape
    
    # ----------------------------------------------------------------------
    # 2. 元のメッシュ情報の読み込みと中心座標の導出 (補間用ソース)
    # ----------------------------------------------------------------------
    
    ref_cdf_filepath = list_cdf_filepaths[0]
    
    # 元のメッシュグリッドを読み込む
    original_mesh_r_rmlt = cdf.get_data(ref_cdf_filepath, 'mesh_r_rmlt')
    original_mesh_theta_rmlt = cdf.get_data(ref_cdf_filepath, 'mesh_theta_rmlt')
    original_mesh_theta_rmlat = cdf.get_data(ref_cdf_filepath, 'mesh_theta_rmlat')

    # 元のビンの境界座標を導出 (pcolormeshの境界から)
    original_r_bins = original_mesh_r_rmlt[:, 0]
    original_mlt_bins = (original_mesh_theta_rmlt[0, :] / (2 * np.pi)) * 24.0
    original_mlat_bins = np.rad2deg(original_mesh_theta_rmlat[0, :])
    
    # 元のビンの中心座標を導出 (RegularGridInterpolatorの軸座標)
    original_r_centers = _bins_to_centers(original_r_bins)
    original_mlt_centers = _bins_to_centers(original_mlt_bins)
    original_mlat_centers = _bins_to_centers(original_mlat_bins)
    
    # --- 【診断用追加】元のCDFのR範囲チェック ---
    r_min_source = original_r_centers.min()
    r_max_source = original_r_centers.max()
    r_min_target = target_r_centers.min()

    # print(f"--- R-Axis Range Check (診断用) ---")
    # print(f"Original R Centers Range: [{r_min_source:.3f}, {r_max_source:.3f}]")
    # print(f"Target R Centers Min: {r_min_target:.3f}")
    
    # ターゲットの最小R中心がソース範囲外の場合に警告
    if r_min_target < r_min_source:
        display.warning(
            'get_dwell_time_cdf_files_interp',
            f"Target R minimum center ({r_min_target:.3f}) is outside the original R center range minimum ({r_min_source:.3f}). "
            "Data in this area will be filled with NaN (formerly 0)."
        )
    # ----------------------------------------------

    # ----------------------------------------------------------------------
    # 3. CDFデータの読み込みと集計/補間
    # ----------------------------------------------------------------------
    
    loop_start_time = datetime.now()
    for i, cdf_filepath in enumerate(list_cdf_filepaths):
        if info:
            display.progress_bar(i, len(list_cdf_filepaths), loop_start_time)
            
        rmlt_grid_i = cdf.get_data(cdf_filepath, 'rmlt_grid')
        rmlat_grid_i = cdf.get_data(cdf_filepath, 'rmlat_grid')
        
        # 形状チェック
        current_rmlt_shape = rmlt_grid_i.shape
        # グリッドサイズが一致するかどうかを確認（一致しない場合はリグリッドが必要）
        is_shape_match = (current_rmlt_shape[0] == expected_rmlt_shape[0] and 
                          current_rmlt_shape[1] == expected_rmlt_shape[1])

        if not is_shape_match:
            # --------------------------------------------------------
            # 補間（Re-gridding）が必要な場合
            # fill_value=np.nan に変更し、範囲外を診断可能にする
            # --------------------------------------------------------
            
            # --- R-MLTの補間 ---
            try:
                interp_rmlt = RegularGridInterpolator(
                    (original_r_centers, original_mlt_centers), 
                    rmlt_grid_i, 
                    method='nearest', # 最も近いグリッドの値を使用
                    bounds_error=False, 
                    fill_value=np.nan # 【修正】範囲外はNaNで埋めて診断しやすくする
                )
                
                points_rmlt = np.vstack((target_r_mesh_rmlt.ravel(), target_mlt_mesh.ravel())).T 
                rmlt_regridded = interp_rmlt(points_rmlt).reshape(expected_rmlt_shape)
                
                # NaNを除去して加算
                rmlt_grid = np.nansum(np.dstack([rmlt_grid, rmlt_regridded]), axis=2)
            
            except Exception as e:
                display.error('_plot/plot_dist_cdf_files', 
                              f"R-MLT re-gridding failed: {e}. Check original bin definitions."
                )
                return None
            
            # --- R-MLATの補間 ---
            try:
                interp_rmlat = RegularGridInterpolator(
                    (original_r_centers, original_mlat_centers), 
                    rmlat_grid_i, 
                    method='nearest', # 最も近いグリッドの値を使用
                    bounds_error=False, 
                    fill_value=np.nan # 【修正】範囲外はNaNで埋めて診断しやすくする
                )
                
                points_rmlat = np.vstack((target_r_mesh_rmlat.ravel(), target_mlat_mesh.ravel())).T 
                
                rmlat_regridded = interp_rmlat(points_rmlat).reshape(rmlat_grid.shape)

                # NaNを除去して加算
                rmlat_grid = np.nansum(np.dstack([rmlat_grid, rmlat_regridded]), axis=2)

            except Exception as e:
                display.error('_plot/plot_dist_cdf_files', 
                              f"R-MLAT re-gridding failed: {e}. Check original bin definitions."
                )
                return None
            
        else:
            # --------------------------------------------------------
            # 形状が一致する場合（元のロジック：単に加算）
            # --------------------------------------------------------
            rmlt_grid = rmlt_grid + rmlt_grid_i
            rmlat_grid = rmlat_grid + rmlat_grid_i
    
    # ----------------------------------------------------------------------
    # 4. 結果の返却
    # ----------------------------------------------------------------------
    return {
        'mesh_theta_rmlt': mesh_theta_rmlt,
        'mesh_r_rmlt': mesh_r_rmlt,
        'rmlt_grid': rmlt_grid,
        'mesh_theta_rmlat': mesh_theta_rmlat,
        'mesh_r_rmlat': mesh_r_rmlat,
        'rmlat_grid': rmlat_grid,
    }


def get_dwell_time_trange_with_ref(
        trange,
        basedir_orb,
        parent_dir_ref_dwell='',
        basedir_ref_dwell=None,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
        rmlat_whole=False
):
    dt_start, dt_end = time.convert(trange, frm='str', into='datetime')
    if dt_start.day == 1:
        dt_start_ref = datetime(dt_start.year, dt_start.month, 1, 0, 0, 0).replace(tzinfo=timezone.utc)
    else:
        dt_start_ref = datetime(dt_start.year, dt_start.month + 1, 1, 0, 0, 0).replace(tzinfo=timezone.utc)
    
    if dt_end.day == 1:
        dt_end_ref = datetime(dt_end.year, dt_end.month, 1, 0, 0, 0).replace(tzinfo=timezone.utc)
    else:
        dt_end_ref = datetime(dt_end.year, dt_end.month + 1, 1, 0, 0, 0).replace(tzinfo=timezone.utc)

    # date when reference data is available

    display.info('Reading reference cdf files')
    ref_cdf_filepaths = []
    current_dt_start_ref = dt_start_ref
    while current_dt_start_ref < dt_end_ref:
        year = current_dt_start_ref.year
        month = current_dt_start_ref.month
        if basedir_ref_dwell is None:
            base_path = f'messenger_data_analysis/orb/ref_dwell/1month/{year:04}/messenger_orb_ref_dwell_{year:04}{month:02}.cdf'
            cdf_filepath = os.path.join(parent_dir_ref_dwell, base_path)
        else:
            cdf_filepath_search = os.path.join(basedir_ref_dwell, f'{year:04}', f'*{year:04}{month:02}.cdf')
            cdf_filepath_candidate = glob(cdf_filepath_search)
            if len(cdf_filepath_candidate) == 0:
                display.warning(f'No cdf filepath: {cdf_filepath_search}')
                current_dt_start_ref += relativedelta(months=1)
                continue
            elif len(cdf_filepath_candidate) == 1:
                cdf_filepath = cdf_filepath_candidate[0]
            else:
                display.warning(f'Multiple candidate for cdf file: {cdf_filepath_search} -> Adopted the 1st one')
                cdf_filepath = cdf_filepath_candidate[0]

        ref_cdf_filepaths.append(cdf_filepath)
        current_dt_start_ref += relativedelta(months=1)
    
    display.print_list(ref_cdf_filepaths, 'ref_cdf_filepaths')

    if ref_cdf_filepaths:
        dict_orb_meshgrid_ref = get_dwell_time_cdf_files(
            ref_cdf_filepaths,
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins,
            rmlat_whole=rmlat_whole
        )
    else:
        dict_orb_meshgrid_ref = None
    
    # former: [dt_start, dt_start_ref]
    if dt_start < dt_start_ref:
        str_start_ref = time.convert(dt_start_ref, frm='datetime', into='str')
        display.info(f'former: [{trange[0]}, {str_start_ref}]')    
        pytplot.del_data()
        start_former = time.convert(dt_start, frm='datetime', into='str')
        end_former = time.convert(dt_start_ref, frm='datetime', into='str')
        dict_orb_meshgrid_former = get_dwell_time(
            [start_former, end_former],
            basedir_orb=basedir_orb,
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins,
            rmlat_whole=rmlat_whole
        )
        # output temporal file
        cdf.dict_to_cdffile(dict_orb_meshgrid_former, '.temporal-dict_orb_meshgrid_former.cdf')
        del dict_orb_meshgrid_former

    # else:
    #     dict_orb_meshgrid_former = None
    
    # latter: [dt_end_ref, dt_end]
    
    if dt_end_ref < dt_end:
        str_end_ref = time.convert(dt_end_ref, frm='datetime', into='str')
        display.info(f'former: [{str_end_ref}, {trange[1]}]')
        pytplot.del_data()
        start_latter = time.convert(dt_end_ref, frm='datetime', into='str')
        end_latter = time.convert(dt_end, frm='datetime', into='str')
        dict_orb_meshgrid_latter = get_dwell_time(
            [start_latter, end_latter],
            basedir_orb=basedir_orb,
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins,
            rmlat_whole=rmlat_whole
        )
        # output temporal file
        cdf.dict_to_cdffile(dict_orb_meshgrid_latter, '.temporal-dict_orb_meshgrid_latter.cdf')
        del dict_orb_meshgrid_latter

    # else:
    #     dict_orb_meshgrid_latter = None

    # read temporal file
    temporal_cdf_filepath_former = '.temporal-dict_orb_meshgrid_former.cdf'
    temporal_cdf_filepath_latter = '.temporal-dict_orb_meshgrid_latter.cdf'
    if os.path.exists(temporal_cdf_filepath_former):
        dict_orb_meshgrid_former = cdf.cdffile_to_dict(temporal_cdf_filepath_former)
        os.remove(temporal_cdf_filepath_former)
    else:
        dict_orb_meshgrid_former = None
    if os.path.exists(temporal_cdf_filepath_latter):
        dict_orb_meshgrid_latter = cdf.cdffile_to_dict(temporal_cdf_filepath_latter)
        os.remove(temporal_cdf_filepath_latter)
    else:
        dict_orb_meshgrid_latter = None


    all_dwell_dicts = [dict_orb_meshgrid_ref, dict_orb_meshgrid_former, dict_orb_meshgrid_latter]
    
    # 1. 最初に有効なデータを持つ辞書を見つける
    first_valid_dict = next((d for d in all_dwell_dicts if d is not None), None)

    if first_valid_dict is None:
        # どの期間にもデータがない場合
        print("Warning: No dwell time data (CDF or calculated) was available for the entire range.")
        return None

    # 2. 結果辞書を初期化
    dict_orb_meshgrid = {}
    
    # 3. メッシュ情報 (座標) を最初に見つかった辞書からコピー
    mesh_keys = ['mesh_theta_rmlt', 'mesh_r_rmlt', 'mesh_theta_rmlat', 'mesh_r_rmlat']
    for key in mesh_keys:
        dict_orb_meshgrid[key] = first_valid_dict[key].copy()
        
    # 4. グリッド情報 (滞在時間) をゼロのNumpy配列で初期化し、加算
    grid_keys = ['rmlt_grid', 'rmlat_grid', 'rmlt_grid_count', 'rmlat_grid_count']
    for key in grid_keys:
        # 最初の有効な辞書の形状を使ってゼロの配列を初期化
        dict_orb_meshgrid[key] = np.zeros_like(first_valid_dict[key], dtype=np.float64)

        # 全てのデータ辞書をループして加算を実行
        for dict_orb in all_dwell_dicts:
            if dict_orb is not None and key in dict_orb:
                # Numpy配列 + Numpy配列なので安全に加算可能
                dict_orb_meshgrid[key] += dict_orb[key]
    
    # dict_orb_meshgrid = {
    #     'mesh_theta_rmlt': None,
    #     'mesh_r_rmlt': None,
    #     'rmlt_grid': None,
    #     'mesh_theta_rmlat': None,
    #     'mesh_r_rmlat': None,
    #     'rmlat_grid': None,
    # }
    # keys = [
    #     'mesh_theta_rmlt',
    #     'mesh_r_rmlt',
    #     'rmlt_grid',
    #     'mesh_theta_rmlat',
    #     'mesh_r_rmlat',
    #     'rmlat_grid',
    # ]

    # for key in dict_orb_meshgrid.keys():
    #     for dict_orb in [dict_orb_meshgrid_ref, dict_orb_meshgrid_former, dict_orb_meshgrid_latter]:
    #         if dict_orb is not None:
    #             dict_orb_meshgrid[key] = dict_orb_meshgrid[key] + dict_orb[key]

    return dict_orb_meshgrid


# def get_dwell_time_trange_with_ref(
#         trange,
#         parent_dir_ref_dwell='',
#         basedir_ref_dwell=None,
#         r_bins=None,
#         mlt_bins=None,
#         mlat_bins=None,
#         rmlat_whole=False
# ):
#     # --- 1. 初期設定 ---
#     dt_start, dt_end = time.convert(trange, frm='str', into='datetime')
#     dt_start_ref = datetime(dt_start.year, dt_start.month + 1, 1, 0, 0, 0, tzinfo=timezone.utc)
#     dt_end_ref = datetime(dt_end.year, dt_end.month, 1, 0, 0, 0, tzinfo=timezone.utc) # dt_endの月まで

#     # 結果を格納する変数（最初はNone）
#     result_dict = None

#     def accumulate_dict(current_res, new_data):
#         """新しいデータを累積結果に加算し、メモリ節約のためnew_dataをNoneにする補助関数"""
#         if new_data is None:
#             return current_res
        
#         if current_res is None:
#             # 初回はコピーを作成
#             return new_data
        
#         # 滞在時間グリッドを加算
#         grid_keys = ['rmlt_grid', 'rmlat_grid']
#         for key in grid_keys:
#             if key in new_data:
#                 current_res[key] += new_data[key]
        
#         # 計算が終わった古いデータへの参照を明示的に消すヒント
#         del new_data
#         return current_res

#     # --- 2. 前半の計算 (Referenceがない期間) ---
#     if dt_start < dt_start_ref:
#         pytplot.del_data()
#         start_str = time.convert(dt_start, frm='datetime', into='str')
#         end_str = time.convert(dt_start_ref, frm='datetime', into='str')
#         tmp_data = get_dwell_time(
#             [start_str, end_str],
#             r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins, rmlat_whole=rmlat_whole
#         )
#         result_dict = accumulate_dict(result_dict, tmp_data)

#     # --- 3. 中間の計算 (CDFファイルから月ごとに読み込み) ---
#     # get_dwell_time_cdf_filesを一気に呼ぶのではなく、1ファイルずつ処理する（もし関数が対応していれば）
#     # ここでは元のロジックを尊重しつつ、リストを最小限に抑える
#     current_dt = dt_start_ref
#     while current_dt < dt_end_ref:
#         year, month = current_dt.year, current_dt.month
        
#         # パス探索
#         if basedir_ref_dwell is None:
#             rel_path = f'messenger_data_analysis/orb/ref_dwell/1month/{year:04}/messenger_orb_ref_dwell_{year:04}{month:02}.cdf'
#             cdf_path = os.path.join(parent_dir_ref_dwell, rel_path)
#         else:
#             search_pattern = os.path.join(basedir_ref_dwell, f'{year:04}', f'*{year:04}{month:02}.cdf')
#             candidates = glob(search_pattern)
#             cdf_path = candidates[0] if candidates else None

#         if cdf_path and os.path.exists(cdf_path):
#             # 1ファイルずつ読み込んで加算することで、大量のファイルを同時にメモリに載せない
#             tmp_data = get_dwell_time_cdf_files(
#                 [cdf_path], # リストで渡すが要素は1つ
#                 r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins, rmlat_whole=rmlat_whole
#             )
#             result_dict = accumulate_dict(result_dict, tmp_data)
        
#         current_dt += relativedelta(months=1)

#     # --- 4. 後半の計算 (残りの端数期間) ---
#     if dt_end_ref < dt_end:
#         pytplot.del_data()
#         start_str = time.convert(dt_end_ref, frm='datetime', into='str')
#         end_str = time.convert(dt_end, frm='datetime', into='str')
#         tmp_data = get_dwell_time(
#             [start_str, end_str],
#             r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins, rmlat_whole=rmlat_whole
#         )
#         result_dict = accumulate_dict(result_dict, tmp_data)

#     return result_dict
