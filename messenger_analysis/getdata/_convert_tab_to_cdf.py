import numpy as np
import spacepy.pycdf as pycdf # cdflib の代わりに spacepy.pycdf をインポート
from datetime import datetime, timedelta
from typing import Optional
import os


def tab_to_cdf(tab_file_path: str, output_cdf_path: str, info: bool = True) -> Optional[str]:
    """
    PDSのTABファイル（スペース区切り）をCDFファイルに変換する (spacepy.pycdf版)。

    TABファイルの列順序は以下の通りと仮定:
    YEAR, DAY_OF_YEAR, HOUR, MINUTE, SECOND, TIME_TAG, X_MSO, Y_MSO, Z_MSO, BX_MSO, BY_MSO, BZ_MSO

    CDFファイルの変数構成:
    - 'time': Unix Time (秒), (N,)
    - 'pos': MSO座標系での位置データ, (N, 3)
    - 'mag': MSO座標系での磁場データ, (N, 3)

    Args:
        tab_file_path (str): 入力TABファイルのパス。
        output_cdf_path (str): 出力CDFファイルのパス。
        info (bool): 処理の詳細を表示するかどうか。

    Returns:
        Optional[str]: 成功した場合、出力CDFファイルのパス。失敗した場合、None。
    """
    if not os.path.exists(tab_file_path):
        if info:
            print(f"Error: Input file not found at {tab_file_path}")
        return None

    if info:
        print(f"1. Reading data from {tab_file_path}...")
    
    # --- 1. データの読み込み ---
    try:
        data = np.genfromtxt(
            tab_file_path,
            dtype=np.float64,
            delimiter=None, 
            encoding='utf-8'
        )
    except Exception as e:
        if info:
            print(f"Error reading TAB file: {e}")
        return None
        
    if data.ndim != 2 or data.shape[1] != 12:
        if info:
            print(f"Error: Expected (N, 12) shape, but got {data.shape}. Check file format.")
        return None
        
    num_records = data.shape[0]
    
    # データのインデックス
    COL_YEAR, COL_DOY, COL_HOUR, COL_MIN, COL_SEC = 0, 1, 2, 3, 4
    COL_X_MSO, COL_Y_MSO, COL_Z_MSO = 6, 7, 8
    COL_BX_MSO, COL_BY_MSO, COL_BZ_MSO = 9, 10, 11

    # --- 2. 時刻変換 (Unix Timeの生成) ---
    if info:
        print(f"2. Converting time columns ({num_records} records) to Unix Time...")
        
    datetimes = []
    time_data = data[:, [COL_YEAR, COL_DOY, COL_HOUR, COL_MIN, COL_SEC]]

    for row in data:
        try:
            year = int(row[COL_YEAR])
            doy = int(row[COL_DOY])
            hour = int(row[COL_HOUR])
            minute = int(row[COL_MIN])
            sec_full = row[COL_SEC] # 小数点を含む秒 (例: 12.345)

            # 年始からの経過時間を計算
            dt = datetime(year, 1, 1) + timedelta(days=doy - 1)
            # 時・分・秒を一気に timedelta で加算 (second に小数をそのまま渡すのが最も安全)
            dt += timedelta(hours=hour, minutes=minute, seconds=sec_full)
            
            datetimes.append(dt)
        except Exception:
            datetimes.append(None)
    
    # for year, doy, hour, minute, second in time_data:
    #     try:
    #         start_of_year = datetime(int(year), 1, 1, 0, 0, 0)
            
    #         time_delta = timedelta(
    #             days=int(doy) - 1, 
    #             hours=int(hour), 
    #             minutes=int(minute), 
    #             seconds=int(second),
    #             microseconds=int((second - int(second)) * 1000000)
    #         )
    #         dt = start_of_year + time_delta
    #         datetimes.append(dt)
    #     except ValueError as ve:
    #         if info:
    #              print(f"Warning: Skipping invalid time record ({year}, {doy}, {hour}, {minute}, {second}): {ve}")
    #         datetimes.append(None)

    valid_datetimes = [dt for dt in datetimes if dt is not None]
    valid_data_indices = [i for i, dt in enumerate(datetimes) if dt is not None]
    
    if len(valid_datetimes) == 0:
        if info:
            print("Error: No valid time records found.")
        return None
        
    EPOCH = datetime(1970, 1, 1)
    # CDF Epochデータ型（UTCエポックからのミリ秒）ではなく、Unix Time（1970/01/01 00:00:00 UTCからの秒数）を使用
    unix_time = np.array([
        (dt - EPOCH).total_seconds() for dt in valid_datetimes
    ], dtype=np.float64)
    
    filtered_data = data[valid_data_indices, :]
    
    # --- 3. データ整形 ---
    pos_data = filtered_data[:, [COL_X_MSO, COL_Y_MSO, COL_Z_MSO]].astype(np.float32)
    mag_data = filtered_data[:, [COL_BX_MSO, COL_BY_MSO, COL_BZ_MSO]].astype(np.float32)

    if info:
        print(f"3. Data shapes: time={unix_time.shape}, pos={pos_data.shape}, mag={mag_data.shape}")
        
    # --- 4. CDFファイルへの書き出し (pycdfを使用) ---
    if info:
        print(f"4. Writing to CDF file: {output_cdf_path} (using pycdf)...")

    # cdfファイルのメタデータ（グローバル属性）
    global_attrs = {
        'Title': 'MESSENGER MAG MSO Calibrated Data (TAB to CDF Conversion)',
        'Project': 'MESSENGER',
        'Discipline': 'Space Physics',
        'Source_Name': 'MESSENGER',
        'Data_type': 'MAG_MSO',
        'Generated_by': 'Python spacepy.pycdf'
    }

    # 変数のデータ型と属性を定義
    variable_specs = {
        'time': {
            'data': unix_time,
            'type': pycdf.const.CDF_DOUBLE, # Unix Time (秒) には double を使用
            'attrs': {
                'Variable': 'time',
                'UNITS': 's',
                'FIELD_REPRESENTATION': 'Epoch',
                'VAR_TYPE': 'support_data',
                'DISPLAY_TYPE': 'time_series',
                'FORMAT': 'E14.8',
            }
        },
        'pos': {
            'data': pos_data,
            'type': pycdf.const.CDF_FLOAT, # 位置データには float を使用
            'attrs': {
                'Variable': 'pos',
                'UNITS': 'km',
                'FIELD_REPRESENTATION': 'Cartesian',
                'VAR_TYPE': 'data',
                'FORMAT': 'E12.6',
                'COMPONENT_0': 'X_MSO',
                'COMPONENT_1': 'Y_MSO',
                'COMPONENT_2': 'Z_MSO',
            }
        },
        'mag': {
            'data': mag_data,
            'type': pycdf.const.CDF_FLOAT,
            'attrs': {
                'Variable': 'mag',
                'UNITS': 'nT',
                'FIELD_REPRESENTATION': 'Cartesian',
                'VAR_TYPE': 'data',
                'FORMAT': 'E12.6',
                'COMPONENT_0': 'BX_MSO',
                'COMPONENT_1': 'BY_MSO',
                'COMPONENT_2': 'BZ_MSO',
            }
        }
    }
    
    # cdfファイルを作成
    try:
        # 既存ファイルがある場合、削除して新規作成を保証
        if os.path.exists(output_cdf_path):
            os.remove(output_cdf_path)

        # pycdfでCDFファイルを新規作成 ('create=True' で新規作成モード)
        cdf_file = pycdf.CDF(output_cdf_path, create=True)
        
        # グローバル属性を書き込む
        # pycdfでは .attrs.update() でグローバル属性を設定する
        cdf_file.attrs.update(global_attrs)

        # 変数を書き込む
        for var_name, spec in variable_specs.items():
            data_array = spec['data']
            
            if data_array.ndim == 1:
                # 1次元変数 (time) の作成
                cdf_var = cdf_file.new(
                    var_name, 
                    data=data_array, 
                    type=spec['type']
                    # rec_vary=True は古いバージョンでは非対応なため削除。デフォルトで可変と見なされる
                )
            else:
                # 2次元変数 (pos, mag) の作成
                cdf_var = cdf_file.new(
                    var_name, 
                    data=data_array, 
                    type=spec['type'],
                    dims=data_array.shape[1:] # レコードサイズ (3) を指定
                    # rec_vary=True は古いバージョンでは非対応なため削除
                )
            
            # 変数属性を書き込む
            cdf_var.attrs.update(spec['attrs'])
                 
        cdf_file.close()

        if info:
            print(f"Success: CDF file created at {output_cdf_path}")
        return output_cdf_path
    
    except Exception as e:
        if info:
            print(f"Error writing CDF file: {e}")
            # 書き込み失敗した場合、作成途中のファイルを削除
            if os.path.exists(output_cdf_path):
                os.remove(output_cdf_path)
        return None
    

def _tab_to_cdf(tab_file_path: str, output_cdf_path: str, info: bool = True) -> Optional[str]:# 20260322
    """
    PDSのTABファイル（スペース区切り）をCDFファイルに変換する (spacepy.pycdf版)。

    TABファイルの列順序は以下の通りと仮定:
    YEAR, DAY_OF_YEAR, HOUR, MINUTE, SECOND, TIME_TAG, X_MSO, Y_MSO, Z_MSO, BX_MSO, BY_MSO, BZ_MSO

    CDFファイルの変数構成:
    - 'time': Unix Time (秒), (N,)
    - 'pos': MSO座標系での位置データ, (N, 3)
    - 'mag': MSO座標系での磁場データ, (N, 3)

    Args:
        tab_file_path (str): 入力TABファイルのパス。
        output_cdf_path (str): 出力CDFファイルのパス。
        info (bool): 処理の詳細を表示するかどうか。

    Returns:
        Optional[str]: 成功した場合、出力CDFファイルのパス。失敗した場合、None。
    """
    if not os.path.exists(tab_file_path):
        if info:
            print(f"Error: Input file not found at {tab_file_path}")
        return None

    if info:
        print(f"1. Reading data from {tab_file_path}...")
    
    # --- 1. データの読み込み ---
    try:
        data = np.genfromtxt(
            tab_file_path,
            dtype=np.float64,
            delimiter=None, 
            encoding='utf-8'
        )
    except Exception as e:
        if info:
            print(f"Error reading TAB file: {e}")
        return None
        
    if data.ndim != 2 or data.shape[1] != 12:
        if info:
            print(f"Error: Expected (N, 12) shape, but got {data.shape}. Check file format.")
        return None
        
    num_records = data.shape[0]
    
    # データのインデックス
    COL_YEAR, COL_DOY, COL_HOUR, COL_MIN, COL_SEC = 0, 1, 2, 3, 4
    COL_X_MSO, COL_Y_MSO, COL_Z_MSO = 6, 7, 8
    COL_BX_MSO, COL_BY_MSO, COL_BZ_MSO = 9, 10, 11

    # --- 2. 時刻変換 (Unix Timeの生成) ---
    if info:
        print(f"2. Converting time columns ({num_records} records) to Unix Time...")
        
    datetimes = []
    time_data = data[:, [COL_YEAR, COL_DOY, COL_HOUR, COL_MIN, COL_SEC]]
    
    for year, doy, hour, minute, second in time_data:
        try:
            start_of_year = datetime(int(year), 1, 1, 0, 0, 0)
            
            time_delta = timedelta(
                days=int(doy) - 1, 
                hours=int(hour), 
                minutes=int(minute), 
                seconds=int(second),
                microseconds=int((second - int(second)) * 1000000)
            )
            dt = start_of_year + time_delta
            datetimes.append(dt)
        except ValueError as ve:
            if info:
                 print(f"Warning: Skipping invalid time record ({year}, {doy}, {hour}, {minute}, {second}): {ve}")
            datetimes.append(None)

    valid_datetimes = [dt for dt in datetimes if dt is not None]
    valid_data_indices = [i for i, dt in enumerate(datetimes) if dt is not None]
    
    if len(valid_datetimes) == 0:
        if info:
            print("Error: No valid time records found.")
        return None
        
    EPOCH = datetime(1970, 1, 1)
    # CDF Epochデータ型（UTCエポックからのミリ秒）ではなく、Unix Time（1970/01/01 00:00:00 UTCからの秒数）を使用
    unix_time = np.array([
        (dt - EPOCH).total_seconds() for dt in valid_datetimes
    ], dtype=np.float64)
    
    filtered_data = data[valid_data_indices, :]
    
    # --- 3. データ整形 ---
    pos_data = filtered_data[:, [COL_X_MSO, COL_Y_MSO, COL_Z_MSO]].astype(np.float32)
    mag_data = filtered_data[:, [COL_BX_MSO, COL_BY_MSO, COL_BZ_MSO]].astype(np.float32)

    if info:
        print(f"3. Data shapes: time={unix_time.shape}, pos={pos_data.shape}, mag={mag_data.shape}")
        
    # --- 4. CDFファイルへの書き出し (pycdfを使用) ---
    if info:
        print(f"4. Writing to CDF file: {output_cdf_path} (using pycdf)...")

    # cdfファイルのメタデータ（グローバル属性）
    global_attrs = {
        'Title': 'MESSENGER MAG MSO Calibrated Data (TAB to CDF Conversion)',
        'Project': 'MESSENGER',
        'Discipline': 'Space Physics',
        'Source_Name': 'MESSENGER',
        'Data_type': 'MAG_MSO',
        'Generated_by': 'Python spacepy.pycdf'
    }

    # 変数のデータ型と属性を定義
    variable_specs = {
        'time': {
            'data': unix_time,
            'type': pycdf.const.CDF_DOUBLE, # Unix Time (秒) には double を使用
            'attrs': {
                'Variable': 'time',
                'UNITS': 's',
                'FIELD_REPRESENTATION': 'Epoch',
                'VAR_TYPE': 'support_data',
                'DISPLAY_TYPE': 'time_series',
                'FORMAT': 'E14.8',
            }
        },
        'pos': {
            'data': pos_data,
            'type': pycdf.const.CDF_FLOAT, # 位置データには float を使用
            'attrs': {
                'Variable': 'pos',
                'UNITS': 'km',
                'FIELD_REPRESENTATION': 'Cartesian',
                'VAR_TYPE': 'data',
                'FORMAT': 'E12.6',
                'COMPONENT_0': 'X_MSO',
                'COMPONENT_1': 'Y_MSO',
                'COMPONENT_2': 'Z_MSO',
            }
        },
        'mag': {
            'data': mag_data,
            'type': pycdf.const.CDF_FLOAT,
            'attrs': {
                'Variable': 'mag',
                'UNITS': 'nT',
                'FIELD_REPRESENTATION': 'Cartesian',
                'VAR_TYPE': 'data',
                'FORMAT': 'E12.6',
                'COMPONENT_0': 'BX_MSO',
                'COMPONENT_1': 'BY_MSO',
                'COMPONENT_2': 'BZ_MSO',
            }
        }
    }
    
    # cdfファイルを作成
    try:
        # 既存ファイルがある場合、削除して新規作成を保証
        if os.path.exists(output_cdf_path):
            os.remove(output_cdf_path)

        # pycdfでCDFファイルを新規作成 ('create=True' で新規作成モード)
        cdf_file = pycdf.CDF(output_cdf_path, create=True)
        
        # グローバル属性を書き込む
        # pycdfでは .attrs.update() でグローバル属性を設定する
        cdf_file.attrs.update(global_attrs)

        # 変数を書き込む
        for var_name, spec in variable_specs.items():
            data_array = spec['data']
            
            if data_array.ndim == 1:
                # 1次元変数 (time) の作成
                cdf_var = cdf_file.new(
                    var_name, 
                    data=data_array, 
                    type=spec['type']
                    # rec_vary=True は古いバージョンでは非対応なため削除。デフォルトで可変と見なされる
                )
            else:
                # 2次元変数 (pos, mag) の作成
                cdf_var = cdf_file.new(
                    var_name, 
                    data=data_array, 
                    type=spec['type'],
                    dims=data_array.shape[1:] # レコードサイズ (3) を指定
                    # rec_vary=True は古いバージョンでは非対応なため削除
                )
            
            # 変数属性を書き込む
            cdf_var.attrs.update(spec['attrs'])
                 
        cdf_file.close()

        if info:
            print(f"Success: CDF file created at {output_cdf_path}")
        return output_cdf_path
    
    except Exception as e:
        if info:
            print(f"Error writing CDF file: {e}")
            # 書き込み失敗した場合、作成途中のファイルを削除
            if os.path.exists(output_cdf_path):
                os.remove(output_cdf_path)
        return None
    