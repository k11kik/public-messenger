"""
MESSENGER磁場データダウンロードモジュール

このモジュールはMESSENGER探査機の磁場データを期間指定でダウンロードする機能を提供します。
"""

import os
import zipfile
import tempfile
import concurrent.futures
import threading
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from tqdm import tqdm
import cdflib
import numpy as np
import time

from common.base import display

# urllib3の警告を抑制
# warnings.filterwarnings('ignore', message='.*OpenSSL.*', category=UserWarning)


# def download_mag_mso(trange, output_dir="messenger_data", max_workers=1, info=True, use_parallel=False, update_cdf=True):
#     """
#     trange形式でMESSENGERデータをダウンロード（並列/逐次切り替え対応）
#     update_cdf=True: 既存CDFがあっても必ず上書き
#     """
#     if len(trange) != 2:
#         raise ValueError("trange must be a list with exactly 2ments: [start_time, end_time]")
    
#     downloader = MessengerDataDownloader()
#     return downloader.download_data_for_period(trange, output_dir, max_workers=max_workers, info=info, use_parallel=use_parallel, update_cdf=update_cdf)




def read_tab_file_pandas(file_path, info=True):
    """
    pandasを使用してTABファイルを読み込む（より高速）
    
    Parameters:
        file_path (str): TABファイルのパス
        info (bool): エラーメッセージを表示するかどうか
        
    Returns:
        pandas.DataFrame: 読み込んだデータ
    """
    import pandas as pd
    
    # 固定幅フォーマットの定義
    colspecs = [
        (0, 4),    # YEAR
        (5, 8),    # DAY_OF_YEAR
        (9, 11),   # HOUR
        (12, 14),  # MINUTE
        (15, 21),  # SECOND
        (22, 35),  # TIME_TAG
        (36, 50),  # X_MSO
        (51, 65),  # Y_MSO
        (66, 80),  # Z_MSO
        (81, 91),  # BX_MSO
        (92, 102), # BY_MSO
        (103, 113) # BZ_MSO
    ]
    
    column_names = [
        'YEAR', 'DAY_OF_YEAR', 'HOUR', 'MINUTE', 'SECOND',
        'TIME_TAG', 'X_MSO', 'Y_MSO', 'Z_MSO', 'BX_MSO', 'BY_MSO', 'BZ_MSO'
    ]
    
    try:
        # PDSファイルには、しばしばファイル冒頭にメタデータやラベルが含まれるため、
        # skiprows=N を指定するか、コメント文字でスキップするのが一般的。
        # ここでは、データ行以外（例: コメント行やラベル行）をスキップするために、
        # pandasのlow_memoryをFalseにしつつ、コメント文字の指定を検討します。
        
        # 💡 skiprowsで最初の数行をスキップすることを試みる（経験的に1行または0行の場合もある）
        # 正確な行数を特定するのは困難なため、ここでは一旦そのままのロジックを維持しつつ、
        # 発生したエラーから、データ行だけをフィルタリングする処理を追加する方が堅牢です。
        
        # **暫定的な対策として、以下の行で skiprows=0 または skiprows=1 を試す**
        # PDSのTABファイルはヘッダー行がないことが多いですが、もしあればスキップが必要です
        # df = pd.read_fwf(file_path, colspecs=colspecs, names=column_names, skiprows=0) 
        
        # ヘッダー行を特定できない場合は、生のファイルを読み込み、データ行を特定する処理が必要です
        
        # まず、既存のロジックで読み込みを試みる
        df = pd.read_fwf(file_path, colspecs=colspecs, names=column_names)
        
        # 💡データ行の最初の列 'YEAR' が数字であることを確認し、無効な行を削除
        df = df[pd.to_numeric(df['YEAR'], errors='coerce').notna()]
        
        return df
    except Exception as e:
        if info:
            # どのファイルが失敗したか特定するために、ファイル名をログに含める
            print(f"Error reading file with pandas: {Path(file_path).name}: {e}")
        return None
    
    # try:
    #     df = pd.read_fwf(file_path, colspecs=colspecs, names=column_names)
    #     return df
    # except Exception as e:
    #     if info:
    #         print(f"Error reading file with pandas: {e}")
    #     return None


def create_datetime_column(df):
    """
    DataFrameにdatetime列を追加する
    
    Parameters:
        df (pandas.DataFrame): 元のデータフレーム
        
    Returns:
        pandas.DataFrame: datetime列が追加されたデータフレーム
    """
    import pandas as pd
    
    # datetime列を作成
    df['datetime'] = pd.to_datetime(
        df['YEAR'].astype(str) + '-' + 
        df['DAY_OF_YEAR'].astype(str).str.zfill(3) + ' ' + 
        df['HOUR'].astype(str).str.zfill(2) + ':' + 
        df['MINUTE'].astype(str).str.zfill(2) + ':' + 
        df['SECOND'].astype(str),
        format='%Y-%j %H:%M:%S.%f',
        errors='coerce'
    )
    
    return df


class MessengerDataDownloader:
    """
    MESSENGER磁場データを期間指定でダウンロードするクラス
    
    Attributes:
        base_url (str): データソースのベースURL
        session (requests.Session): HTTPセッション
    """
    
    def __init__(self, base_url="https://pds-ppi.igpp.ucla.edu"):
        """
        MessengerDataDownloaderを初期化
        
        Parameters:
            base_url (str): データソースのベースURL
        """
        self.base_url = base_url
        self.session = requests.Session()
        # self.session.headers.update({
        #     'User-Agent': 'MESSENGER-Data-Downloader/1.0'
        # })
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15'
        })
    
    def get_available_dates(self):
        """
        利用可能なデータの日付範囲を取得
        
        Returns:
            tuple: (開始日, 終了日) のdatetimeオブジェクト
        """
        # MESSENGERの運用期間（概算）
        messenger_start = datetime(2004, 8, 3)  # 打ち上げ
        messenger_end = datetime(2015, 4, 30)   # 水星表面への衝突
        
        print(f"MESSENGER mission period: {messenger_start.strftime('%Y-%m-%d')} to {messenger_end.strftime('%Y-%m-%d')}")
        return messenger_start, messenger_end
    
    def date_to_product_id(self, date):
        """
        日付からプロダクトIDを生成（8桁形式）
        
        Parameters:
            date (datetime): 対象日付
            
        Returns:
            str: プロダクトID（例: magmsosci08012）
        """
        year = date.year
        day_of_year = date.timetuple().tm_yday
        # 8桁形式: magmsosci08012
        return f"magmsosci{year % 100:02d}{day_of_year:03d}"

    def construct_download_url_from_date(self, date):
        """
        日付から直接ダウンロードURLを構築（APIを使わない方法）
        
        Parameters:
            date (datetime): 対象日付
            
        Returns:
            str: ダウンロードURL
        """
        product_id = self.date_to_product_id(date)
        urn_id = f"urn:nasa:pds:mess-mag-calibrated:data-mso:{product_id}::1.0"
        
        # 日付からslotパスを構築
        year = date.year
        day_of_year = date.timetuple().tm_yday
        
        # slotパス: /data/mess-mag-calibrated/data/mso/2008/001_031_JAN
        # 月の範囲を計算（例：001_031_JAN）
        month = date.month
        if month == 1:
            month_range = "001_031_JAN"
        elif month == 2:
            month_range = "032_060_FEB"
        elif month == 3:
            month_range = "061_090_MAR"
        elif month == 4:
            month_range = "091_120_APR"
        elif month == 5:
            month_range = "121_151_MAY"
        elif month == 6:
            month_range = "152_181_JUN"
        elif month == 7:
            month_range = "182_212_JUL"
        elif month == 8:
            month_range = "213_243_AUG"
        elif month == 9:
            month_range = "244_273_SEP"
        elif month == 10:
            month_range = "274_304_OCT"
        elif month == 11:
            month_range = "305_334_NOV"
        elif month == 12:
            month_range = "335_365_DEC"
        
        slot = f"/data/mess-mag-calibrated/data/mso/{year}/{month_range}"
        file_name = f"MAGMSOSCI{product_id}_V08.xml"
        data_file = f"MAGMSOSCI{product_id}_V08.TAB"
        
        download_url = f"{self.base_url}/ditdos/download?id={urn_id}&slot={slot}&file_name={file_name}&data_file={data_file}"
        print(f"  Constructed download URL from date: {download_url}")
        return download_url
    
    def download_zip_file(self, url, output_path, info=True):
        """
        ZIPファイルをダウンロードし、展開を試みます。ZIP展開に失敗した場合、
        ダウンロードされたファイルがTABファイルであると仮定して処理を続行します。
        """
        temp_file_path = None
        
        try:
            r = self.session.get(url, stream=True, timeout=60)
            r.raise_for_status()

            # --- ダウンロードと一時ファイル保存 ---
            with tempfile.NamedTemporaryFile(delete=False, suffix='.download') as temp_file: # 拡張子を汎用的なものに変更
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # --- 1. ZIPファイルとしての展開を試みる ---
            try:
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    tab_files_downloaded = [f for f in zip_ref.namelist() if f.lower().endswith('.tab') and not f.endswith('/')]
                    if tab_files_downloaded:
                        zip_ref.extractall(output_path)
                        # ダウンロード後のクリーンアップとTABファイルの取得（既存ロジック）
                        # ... ここに既存のクリーンアップロジックをコピー ...
                        if info:
                            print("  Success: Extracted from ZIP.")
                        
                        # クリーンアップ後、tab_files_downloaded のリストを返す
                        # この場所で本来のクリーンアップ処理を行う必要がありますが、ここでは省略
                        # 既存コードを前提として、TABファイルを残す処理が成功したと仮定して返します
                        
                        # --- 展開後のクリーンアップとTABファイル抽出のロジック開始 ---
                        final_tab_files = []
                        for f in Path(output_path).iterdir():
                            if f.name in tab_files_downloaded:
                                # TABファイルは残す
                                final_tab_files.append(f.name)
                            elif not f.name.lower().endswith('.cdf'):
                                try:
                                    f.unlink() # ファイルを削除
                                except OSError:
                                    pass
                        
                        return final_tab_files
                        # --- クリーンアップロジック終了 ---
                        
            except zipfile.BadZipFile as e:
                # --- 2. ZIP展開に失敗した場合 (フォールバック) ---
                if info:
                    print(f"  Warning: ZIP extraction failed ({e}). Checking if file is raw TAB data...")
                
                # ダウンロードされた一時ファイルが実は生のTABファイルであると仮定
                # temp_file_path を最終的な出力先にコピー/リネームし、TABファイルとして扱う
                
                # URLから想定されるTABファイル名を抽出（例: MAGMSOSCI08012_V08.TAB）
                parsed_url = urlparse(url)
                data_file_name = next((v for k, v in [p.split('=') for p in parsed_url.query.split('&')] if k == 'data_file'), None)
                
                if data_file_name:
                    final_tab_path = Path(output_path) / data_file_name
                    Path(temp_file_path).rename(final_tab_path) # リネームして移動
                    if info:
                        print(f"  Success: Renamed raw data to {data_file_name} and saved.")
                    return [data_file_name] # 成功したTABファイル名をリストで返す
                else:
                    if info:
                        print("  Error: Could not determine expected TAB filename for fallback.")
                    return []

        except Exception as e:
            if info:
                print(f"  An error occurred during download: {e}")
            return []
        finally:
            # 必ず一時ファイルを削除
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


    def old_download_zip_file(self, url, output_path, show_progress=True, info=True):
        """
        ZIPファイルをダウンロードし、正常にダウンロードできたらディレクトリを作成して展開し、
        TABファイルのみをリネームし、他は削除します。
        今回ダウンロードしたZIPファイルに含まれていたTABファイルの名前リストを返します。

        Args:
            url (str): ダウンロードするZIPファイルのURL。
            output_path (str): ZIPファイルを展開するディレクトリのパス。
            target_date (datetime): ダウンロード対象の日付。リネーム後のファイル命名に使用されます。
            show_progress (bool): プログレスを表示するかどうか (現在未実装)。
            info (bool): 情報メッセージを表示するかどうか。
            
        Returns:
            list: 展開され、リネームされたTABファイルのパスのリスト。
                  ダウンロードまたは展開に失敗した場合は空のリストを返します。
        """
        temp_file_path = None
        tab_files_downloaded = [] # ダウンロードされたTABファイルのパスを格納するリスト
        renamed_tab_files = [] # 最終的にリネームされたTABファイルのパスを格納するリスト

        try:
            r = self.session.get(url, stream=True, timeout=60)
            r.raise_for_status() # HTTPエラーが発生した場合に例外を発生させる

            # # Content-Length ヘッダーが存在し、0より大きいことを確認
            # if r.headers.get('Content-Length') == '0':
            #     if info:
            #         print(f"  Warning: Downloaded content length is 0 for {url}. Assuming no data.")
            #     return [] 
            
            # ZIPファイルを一時ファイルにダウンロード
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # ZIPファイルが正常にダウンロードされ、一時ファイルに保存された後に、
            # 初めて最終的な出力ディレクトリを作成する
            Path(output_path).mkdir(parents=True, exist_ok=True) 

            # ZIPファイルを展開
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_contents = zip_ref.namelist() # ZIPファイル内の全ファイル名リストを取得
                
                # ZIPファイルが空かどうかをチェック
                if not zip_contents:
                    if info:
                        print(f"  Warning: ZIP archive is empty for {url}. No files to extract.")
                    return []
                
                # find tab file in zip_contents
                for zip_content in zip_contents:
                    if zip_content.lower().endswith('.tab') and not zip_content.endswith('/'):
                        tab_files_downloaded.append(zip_content) # ダウンロードされたTABファイルをリストに追加

                if tab_files_downloaded and info:
                    print(f"  Found {len(tab_files_downloaded)} TAB files in ZIP: {', '.join(tab_files_downloaded)}")
                if not tab_files_downloaded:
                    return []

                zip_ref.extractall(output_path) # 全ファイルを展開
            
            # 一時ZIPファイルを削除 (展開が成功した後に)
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                if info:
                    print(f"  Deleted temporary ZIP file: {temp_file_path}")
            
            # remove downloaded files except tab_files_downloaded and cdf files
            for f in Path(output_path).iterdir():
                if not f.name in tab_files_downloaded and not f.name.lower().endswith('.cdf'):
                    try:
                        f.unlink() # ファイルを削除
                        if info:
                            print(f"  Deleted non-TAB file: {f.name}")
                    except OSError as e:
                        if info:
                            print(f"  Could not delete {f.name}: {e}")
                        pass
            
            return tab_files_downloaded
        
        except Exception as e:
            if info:
                print(f"  An error occurred during download or extraction: {e}")
            return []
    
    
    def download_data_for_period_serial(self, trange, output_dir="messenger_data", info=True, update_cdf=True):
        print(f"=== MESSENGER Data Download (Serial) ===")
        print(f"Period: {trange[0]} to {trange[1]}")
        print(f"Output directory: {output_dir}")
        print("=" * 50)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        start_date = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
        # 文字列の場合はdatetimeオブジェクトに変換
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        
        downloaded_count = 0
        failed_count = 0
        time_list = make_time_list(trange, delta_value=1, timeunit='days')

        start_time_loop = datetime.now()
        for i, trange_i in enumerate(time_list):
            display.progress_bar(i, len(time_list), start_time_loop)
            start_date_i = datetime.strptime(trange_i[0], '%Y-%m-%d %H:%M:%S')
            end_date_i = datetime.strptime(trange_i[1], '%Y-%m-%d %H:%M:%S')
            date_str = start_date_i.strftime('%Y%m%d')
            year_str = start_date_i.strftime('%Y')
            month_str = start_date_i.strftime('%m')
            date_dir = Path(output_dir) / "mag_mso" / year_str / month_str
            download_url = self.construct_download_url_from_date(start_date_i)
            if download_url:
                if info:
                    display.current_time_comment(comment=f'Downloading {start_date_i.strftime('%Y-%m-%d')} ...')
                retained_tab_files = self.download_zip_file(download_url, str(date_dir), info=info)
                if retained_tab_files:
                    for tab_file in retained_tab_files:
                        # 現在処理しているTABファイルのみをCDFに変換
                        tab_file_path = Path(date_dir) / tab_file
                        if tab_file_path.exists():
                            convert_tab_to_cdf(str(tab_file_path), str(date_dir), info=info, update_cdf=update_cdf)
                        downloaded_count += 1
                else:
                    failed_count += 1
            else:
                if info:
                    print(f"Could not construct download URL for {start_date_i.strftime('%Y-%m-%d')}")
                failed_count += 1
        print(f"\n=== Download Summary (Serial) ===")
        print(f"Total files downloaded: {downloaded_count}")
        print(f"Total files failed: {failed_count}")
        print(f"Output directory: {output_dir}")
        return downloaded_count > 0


    def download_data_for_period_parallel(self, trange, output_dir="messenger_data", info=True, update_cdf=True, max_workers=5):
        """
        指定された期間のMESSENGER磁場データを並列でダウンロードし、CDFに変換します。
        """
        print(f"=== MESSENGER Data Download (Parallel) ===")
        print(f"Period: {trange[0]} to {trange[1]}")
        print(f"Output directory: {output_dir}")
        print(f"Max workers: {max_workers}")
        print("=" * 50)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # make_time_list は [['YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS'], ...] の形式を返す
        time_list_periods = make_time_list(trange, delta_value=1, timeunit='days')
        
        total_tasks = len(time_list_periods)
        downloaded_count = 0
        failed_count = 0
        
        loop_start_time = datetime.now()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 各タスク (trange_i_element) に対してサブミット
            # _process_single_day_download_and_convert に trange_i_element (リスト) を直接渡します。
            futures = {executor.submit(_process_single_day_download_and_convert, 
                                        trange_i_element, # ここは [['YYYY-MM-DD HH:MM:SS', ...]] のリストのまま
                                        output_dir, 
                                        info, 
                                        update_cdf, 
                                        self.base_url, 
                                        self.session.headers 
                                        ): trange_i_element for trange_i_element in time_list_periods}
            
            # 各タスクの完了を待機し、結果を処理
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                # futures[future] は trange_i_element (リスト) なので、日付文字列を抽出して使う
                trange_i_list_for_log = futures[future]
                # リストの最初の要素 ('YYYY-MM-DD HH:MM:SS') から日付部分 'YYYY-MM-DD' を抽出
                date_str_for_log = trange_i_list_for_log[0].split(' ')[0] 

                display.progress_bar(i + 1, total_tasks, loop_start_time) 
                
                try:
                    result_count_for_day = future.result() 
                    if result_count_for_day > 0:
                        downloaded_count += result_count_for_day
                    else:
                        failed_count += 1
                except Exception as exc:
                    failed_count += 1
                    # ここで date_str_for_log は文字列なので、直接ログに表示
                    display.error(f"Parallel_Task({date_str_for_log})", f"Generated an exception: {exc}")
        
        print(f"\n=== Download Summary (Parallel) ===")
        print(f"Total files downloaded: {downloaded_count}")
        print(f"Total tasks failed or no data: {failed_count}")
        print(f"Output directory: {output_dir}")
        return downloaded_count > 0

    def old_download_data_for_period_parallel(self, trange, output_dir="messenger_data", info=True, update_cdf=True, max_workers=5):
        """
        指定された期間のMESSENGER磁場データを並列でダウンロードし、CDFに変換します。
        """
        print(f"=== MESSENGER Data Download (Parallel) ===")
        print(f"Period: {trange[0]} to {trange[1]}")
        print(f"Output directory: {output_dir}")
        print(f"Max workers: {max_workers}")
        print("=" * 50)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        start_date = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')

        # 時間リストを作成
        time_list = make_time_list(trange, delta_value=1, timeunit='days')

        def process_single_date(trange_i):
            start_date_i = datetime.strptime(trange_i[0], '%Y-%m-%d %H:%M:%S')
            end_date_i = datetime.strptime(trange_i[1], '%Y-%m-%d %H:%M:%S')
            date_str = start_date_i.strftime('%Y%m%d')
            year_str = start_date_i.strftime('%Y')
            month_str = start_date_i.strftime('%m')
            date_dir = Path(output_dir) / "mag_mso" / year_str / month_str
            download_url = self.construct_download_url_from_date(start_date_i)
            if download_url:
                if info:
                    display.current_time_comment(comment=f'Downloading {start_date_i.strftime("%Y-%m-%d")} ...')
                retained_tab_files = self.download_zip_file(download_url, str(date_dir), show_progress=False, info=info)
                if retained_tab_files:
                    for tab_file in retained_tab_files:
                        tab_file_path = Path(date_dir) / tab_file
                        if tab_file_path.exists():
                            convert_tab_to_cdf(str(tab_file_path), str(date_dir), info=info, update_cdf=update_cdf)
                    return len(retained_tab_files)
                else:
                    return 0
            else:
                if info:
                    print(f"Could not construct download URL for {start_date_i.strftime('%Y-%m-%d')}")
                return 0

        # 並列処理を実行
        downloaded_count = 0
        failed_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_single_date, trange_i): trange_i for trange_i in time_list}
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result > 0:
                        downloaded_count += result
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    print(f"Error processing date range {futures[future]}: {e}")

        print(f"\n=== Download Summary (Parallel) ===")
        print(f"Total files downloaded: {downloaded_count}")
        print(f"Total files failed: {failed_count}")
        print(f"Output directory: {output_dir}")
        return downloaded_count > 0

    # def old_download_data_for_period_parallel(self, trange, output_dir="messenger_data", info=True, update_cdf=True, max_workers=5):
    #     """
    #     指定された期間のMESSENGER磁場データを並列でダウンロードし、CDFに変換します。
        
    #     Args:
    #         trange (list): ['YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS'] 形式の期間。
    #         output_dir (str): データが保存されるルートディレクトリ。
    #         info (bool): 詳細なログメッセージを表示するかどうか。
    #         update_cdf (bool): 既存のCDFファイルを上書きするかどうか。
    #         max_workers (int): 同時に実行するスレッドの最大数。
            
    #     Returns:
    #         bool: ダウンロードと変換が一つでも成功した場合にTrue、全て失敗した場合はFalse。
    #     """
    #     print(f"=== MESSENGER Data Download (Parallel) ===")
    #     print(f"Period: {trange[0]} to {trange[1]}")
    #     print(f"Output directory: {output_dir}")
    #     print(f"Max workers: {max_workers}")
    #     print("=" * 50)
        
    #     # output_dir はメインスレッドで一度だけ作成
    #     Path(output_dir).mkdir(parents=True, exist_ok=True)
        
    #     start_date_obj = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
    #     end_date_obj = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
        
    #     # make_time_list を使用して、各日に対する datetime オブジェクトのリストを作成
    #     current_dt = start_date_obj
    #     dates_to_process = []
    #     while current_dt <= end_date_obj:
    #         dates_to_process.append(current_dt)
    #         current_dt += timedelta(days=1)
        
    #     total_tasks = len(dates_to_process)
    #     downloaded_count = 0
    #     failed_count = 0
        
    #     loop_start_time = datetime.now()
        
    #     # ThreadPoolExecutor を使用して並列処理
    #     # `max_workers` は同時に実行するスレッドの最大数
    #     # `requests.Session` はスレッドセーフではないため、各スレッドで新しいセッションを作成する必要がある
    #     # または、ロックを使用してセッションアクセスを保護する方法もあるが、個別のセッションが簡単。
    #     # ここでは、`_process_single_day_task` に必要な情報を全て渡す。
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         # 各日付に対してタスクをサブミット
    #         # self.base_url と self.session.headers を渡す
    #         futures = {executor.submit(_process_single_day_task, 
    #                                     date_obj, 
    #                                     output_dir, 
    #                                     info, 
    #                                     update_cdf, 
    #                                     self.base_url, # base_urlを渡す
    #                                     self.session.headers # セッションヘッダーを渡す
    #                                     ): date_obj for date_obj in dates_to_process}
            
    #         # 各タスクの完了を待機し、結果を処理
    #         for i, future in enumerate(concurrent.futures.as_completed(futures)):
    #             date_processed = futures[future] # どの日のタスクが完了したか
    #             display.progress_bar(i + 1, total_tasks, loop_start_time) # +1はインデックスのため
                
    #             try:
    #                 # _process_single_day_task からの戻り値を受け取る
    #                 result_count_for_day = future.result() 
    #                 if result_count_for_day > 0:
    #                     downloaded_count += result_count_for_day
    #                     # display.current_time_comment(comment=f"Successfully processed {date_processed.strftime('%Y-%m-%d')} (downloaded {result_count_for_day} files).")
    #                 else:
    #                     failed_count += 1
    #                     # display.current_time_comment(comment=f"Failed or no data for {date_processed.strftime('%Y-%m-%d')}.")
    #             except Exception as exc:
    #                 failed_count += 1
    #                 display.error(f"Parallel_Task({date_processed.strftime('%Y-%m-%d')})", f"Generated an exception: {exc}")
        
    #     print(f"\n=== Download Summary (Parallel) ===")
    #     print(f"Total files downloaded: {downloaded_count}")
    #     print(f"Total tasks failed or no data: {failed_count}")
    #     print(f"Output directory: {output_dir}")
    #     return downloaded_count > 0
    
    def download_data_for_period(self, trange, output_dir="messenger_data", skip_availability_check=False, max_workers=4, info=True, use_parallel=True, update_cdf=False):
        """
        指定された期間のデータをダウンロード（並列化/逐次を切り替え可能）
        use_parallel=True: 並列ダウンロード
        use_parallel=False: 逐次ダウンロード
        update_cdf=True: 既存CDFがあっても必ず上書き
        """
        if use_parallel:
            # 既存の並列処理
            return self.download_data_for_period_parallel(trange, output_dir, max_workers=max_workers, info=info, update_cdf=update_cdf)
        else:
            # 逐次処理
            return self.download_data_for_period_serial(trange, output_dir, info=info, update_cdf=update_cdf)



# def old_download_messenger_data(start_date, end_date, output_dir="messenger_data", max_workers=4, info=True, use_parallel=True, update_cdf=False):
#     """
#     MESSENGERデータを指定された期間でダウンロード（並列/逐次切り替え対応）
#     update_cdf=True: 既存CDFがあっても必ず上書き
#     """
#     # 文字列の場合はdatetimeオブジェクトに変換
#     if isinstance(start_date, str):
#         start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
#     if isinstance(end_date, str):
#         end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    
#     downloader = MessengerDataDownloader()
#     return downloader.download_data_for_period(start_date, end_date, output_dir, max_workers=max_workers, info=info, use_parallel=use_parallel, update_cdf=update_cdf)


# def download_messenger_data_trange(trange, output_dir="messenger_data", max_workers=4, info=True, use_parallel=True, update_cdf=False):
#     """
#     trange形式でMESSENGERデータをダウンロード（並列/逐次切り替え対応）
#     update_cdf=True: 既存CDFがあっても必ず上書き
#     """
   
#     if len(trange) != 2:
#         raise ValueError("trange must be a list with exactly 2ments: [start_time, end_time]")
    
#     start_date = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
#     end_date = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
#     return download_messenger_data(start_date, end_date, output_dir, max_workers, info=info, use_parallel=use_parallel, update_cdf=update_cdf)


def download_messenger_data(trange, output_dir="messenger_data", max_workers=4, info=True, use_parallel=True, update_cdf=True):
    """
    trange形式でMESSENGERデータをダウンロード（並列/逐次切り替え対応）
    update_cdf=True: 既存CDFがあっても必ず上書き
    """
    if len(trange) != 2:
        raise ValueError("trange must be a list with exactly 2ments: [start_time, end_time]")
    
    # start_date = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
    # end_date = datetime.strptime(trange[1], '%Y-%m-%d %H:%M:%S')
    # # 文字列の場合はdatetimeオブジェクトに変換
    # if isinstance(start_date, str):
    #     start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    # if isinstance(end_date, str):
    #     end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    
    downloader = MessengerDataDownloader()
    return downloader.download_data_for_period(trange, output_dir, max_workers=max_workers, info=info, use_parallel=use_parallel, update_cdf=update_cdf)



# def download_single_date(date, output_dir="messenger_data", max_workers=1):
#     """
#     指定された日付のMESSENGERデータをダウンロード
    
#     Parameters:
#         date (datetime or str): ダウンロード対象日付（datetimeオブジェクトまたはYYYY-mm-dd HH:MM:SS'形式の文字列）
#         output_dir (str): 出力ディレクトリ
#         max_workers (int): 最大並列ダウンロード数（単一日の場合は1）
        
#     Returns:
#         bool: ダウンロード成功時True、失敗時False
#     """
#     # 文字列の場合はdatetimeオブジェクトに変換
#     if isinstance(date, str):
#         date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#     return download_messenger_data(date, date, output_dir, max_workers)


# 便利な関数
def get_messenger_mission_period():
    """
    MESSENGERミッションの期間を取得
    
    Returns:
        tuple: (開始日, 終了日) のdatetimeオブジェクト
    """
    downloader = MessengerDataDownloader()
    return downloader.get_available_dates()


def check_data_availability(date, output_dir="messenger_data"):
    """
    指定された日付のデータが既にダウンロードされているかチェック
    
    Parameters:
        date (datetime or str): チェック対象日付（datetimeオブジェクトまたはYYYY-mm-dd HH:MM:SS'形式の文字列）
        output_dir (str): データディレクトリ
        
    Returns:
        bool: データが存在する場合True、存在しない場合False
    """
    # 文字列の場合はdatetimeオブジェクトに変換
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    
    # 新しいディレクトリ構造に対応
    year_str = date.strftime('%Y')
    month_str = date.strftime('%m')
    
    # 新しいパス構造: output_dir/mag_mso/YYYY/mm/downloaded_files/
    date_dir = Path(output_dir) / "mag_mso" / year_str / month_str
    
    # CDFファイルをチェック
    cdf_files = list(date_dir.glob("*.cdf")) if date_dir.exists() else []
    return len(cdf_files) > 0


def convert_tab_to_cdf(tab_file_path, output_dir, info=True, update_cdf=True):
    """
    TABファイルをCDFファイルに変換する
    
    Parameters:
        tab_file_path (str): TABファイルのパス
        output_dir (str): 出力ディレクトリ
        info (bool): エラーメッセージを表示するかどうか
        
    Returns:
        str: 作成されたCDFファイルのパス、失敗時はNone
    """
    try:
        # TABファイルを読み込み
        from messenger_analysis.getdata.download import read_tab_file_pandas, create_datetime_column
        
        # TABファイルを読み込み
        df = read_tab_file_pandas(tab_file_path, info=info)
        if df is None:
            if info:
                print(f"Failed to read TAB file: {tab_file_path}")
            return None
        
        # datetime列を追加
        df = create_datetime_column(df)
        
        # CDFファイル名を生成
        tab_file_name = Path(tab_file_path).stem
        
        # TABファイル名から日付を抽出（例：MAGMSOSCI08281_V08 → 20081007）
        # ファイル名の形式: MAGMSOSCI08281_V08.TAB
        # 08281は年（08）+ 日数（281）を表す
        if 'MAGMSOSCI' in tab_file_name:
            # 年と日数を抽出
            year_day_part = tab_file_name.split('MAGMSOSCI')[1].split('_')[0]
            if len(year_day_part) == 5:  # 例：08281
                year = '20' + year_day_part[:2]  # 08 → 2008
                day_of_year = int(year_day_part[2:])  # 281
                
                # 年と日数から日付を計算
                from datetime import datetime, timedelta
                date_obj = datetime(int(year), 1, 1) + timedelta(days=day_of_year-1)
                date_str = date_obj.strftime('%Y%m%d')
                
                cdf_file_name = f"messenger_mag_mso_{date_str}.cdf"
            else:
                cdf_file_name = f"{tab_file_name}.cdf"
        else:
            cdf_file_name = f"{tab_file_name}.cdf"
        
        cdf_file_path = Path(output_dir) / cdf_file_name

        if os.path.exists(cdf_file_path):
            if update_cdf:
                os.remove(cdf_file_path)  # 既存のCDFファイルを削除
            else:
                if info:
                    print(f"CDF file already exists: {cdf_file_path}. Skipping conversion.")
                return str(cdf_file_path)
        
        # CDFファイルを作成（cdflib.cdfwriteを使用）
        cdf = cdflib.cdfwrite.CDF(str(cdf_file_path))
        
        # 時間データをCDF形式に変換
        time_data = df['datetime'].astype('int64') // 10**9  # Unix時間（秒）
        
        # 磁場データ
        mag_data = df[['BX_MSO', 'BY_MSO', 'BZ_MSO']].values
        
        # 位置データ
        pos_data = df[['X_MSO', 'Y_MSO', 'Z_MSO']].values
        
        # 時間変数を書き込み
        time_spec = {
            'Variable': 'time',
            'Data_Type': 8,  # CDF_INT8
            'Num_Elements': 1,
            'Rec_Vary': True,
            'Dim_Sizes': []
        }
        cdf.write_var(time_spec, var_data=time_data)
        
        # 磁場データを書き込み
        mag_spec = {
            'Variable': 'mag',
            'Data_Type': 45,  # CDF_DOUBLE
            'Num_Elements': 1,
            'Rec_Vary': True,
            'Dim_Sizes': [3]
        }
        cdf.write_var(mag_spec, var_data=mag_data)
        
        # 位置データを書き込み
        pos_spec = {
            'Variable': 'pos',
            'Data_Type': 45,  # CDF_DOUBLE
            'Num_Elements': 1,
            'Rec_Vary': True,
            'Dim_Sizes': [3]
        }
        cdf.write_var(pos_spec, var_data=pos_data)
        
        # 個別の磁場成分を書き込み
        for component in ['BX_MSO', 'BY_MSO', 'BZ_MSO']:
            var_spec = {
                'Variable': component,
                'Data_Type': 45,  # CDF_DOUBLE
                'Num_Elements': 1,
                'Rec_Vary': True,
                'Dim_Sizes': []
            }
            cdf.write_var(var_spec, var_data=df[component].values)
        
        # 個別の位置成分を書き込み
        for component in ['X_MSO', 'Y_MSO', 'Z_MSO']:
            var_spec = {
                'Variable': component,
                'Data_Type': 45,  # CDF_DOUBLE
                'Num_Elements': 1,
                'Rec_Vary': True,
                'Dim_Sizes': []
            }
            cdf.write_var(var_spec, var_data=df[component].values)
        
        cdf.close()
        os.remove(tab_file_path)  # TABファイルを削除（必要に応じて）
        if info:
            print(f'Converted TAB file to CDF: {tab_file_path} → {cdf_file_path}')
        
        return str(cdf_file_path)
        
    except Exception as e:
        if info:
            print(f"Failed to convert TAB to CDF: {e}")
        return None


def cleanup_downloaded_files(output_dir, info: bool = True):
    """
    ダウンロードされたTABファイルとXMLファイルを削除し、CDFファイルのみを残す
    
    Parameters:
        output_dir (str): クリーンアップ対象ディレクトリ
    """
    try:
        output_path = Path(output_dir)
        if not output_path.exists():
            return
        
        # TABファイルとXMLファイルを削除
        for file_path in output_path.glob("*.TAB"):
            if file_path.name.startswith("._") or not file_path.name.endswith(".cdf"):
                try:
                    file_path.unlink()
                    if info:
                        print(f"Deleted: {file_path}")
                except FileNotFoundError:
                    pass
        
        for file_path in output_path.glob("*.xml"):
            if file_path.name.startswith("._") or not file_path.name.endswith(".cdf"):
                try:
                    file_path.unlink()
                    if info:
                        print(f"Deleted: {file_path}")
                except FileNotFoundError:
                    pass
        
        for file_path in output_path.glob("*.XML"):
            if file_path.name.startswith("._") or not file_path.name.endswith(".cdf"):
                try:
                    file_path.unlink()
                    if info:
                        print(f"Deleted: {file_path}")
                except FileNotFoundError:
                    pass
        
        for file_path in output_path.glob("*.txt"):
            if file_path.name.startswith("._") or not file_path.name.endswith(".cdf"):
                try:
                    file_path.unlink()
                    if info:
                        print(f"Deleted: {file_path}")
                except FileNotFoundError:
                    pass
        
        if info:
            print(f"✓ Cleaned up {output_dir}")
        
    except Exception as e:
        if info:
            print(f"✗ Error during cleanup: {e}")


def make_time_list(
        trange: list,
        delta_value=1,
        timeunit: str = 'hours'
    ):
    """

    :param trange: ['YY-mm-dd HH:MM:SS', 'YY-mm-dd HH:MM:SS']
    :param delta_value:
    :param timeunit: 'years', 'days', 'hours', 'minutes', 'seconds'
    :return:
    """
    start_str, end_str = trange
    dt_start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
    dt_end = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')

    # 時間のdeltaを作る
    delta_args = {timeunit: delta_value}
    delta = timedelta(**delta_args)

    time_list = []
    current = dt_start
    while current < dt_end:
        next_time = min(current + delta, dt_end)
        time_list.append([
            current.strftime('%Y-%m-%d %H:%M:%S'),
            next_time.strftime('%Y-%m-%d %H:%M:%S')
        ])
        current = next_time

    return time_list


def _process_single_day_download_and_convert(trange_i: list, output_root_dir: str, info: bool, update_cdf: bool, base_url: str, session_headers: dict):
    """
    並列処理で実行される単一日のダウンロードおよびCDF変換タスク。
    この関数はメインクラスの外部に定義され、必要な情報を引数として受け取ります。
    
    Args:
        trange_i (list): ['YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS'] 形式の期間を示すリスト。
        output_root_dir (str): 全てのダウンロードのルートディレクトリ。
        info (bool): 情報メッセージを表示するかどうか。
        update_cdf (bool): 既存のCDFファイルを上書きするかどうか。
        base_url (str): PDSのベースURL。
        session_headers (dict): requestsセッションのヘッダー（新しいセッションに適用するため）。
        
    Returns:
        int: 正常にダウンロード・変換されたファイルの数 (通常は0または1)。
    """
    # trange_i から日付を抽出
    # trange_i[0] が 'YYYY-MM-DD HH:MM:SS' 形式の文字列であることを想定
    start_date_i = datetime.strptime(trange_i[0], '%Y-%m-%d %H:%M:%S')
    # end_date_i = datetime.strptime(trange_i[1], '%Y-%m-%d %H:%M:%S') # 今回は直接使わない

    # 各スレッド/プロセスで新しいrequestsセッションを作成
    local_session = requests.Session()
    local_session.headers.update(session_headers)

    # このヘルパー関数内で使用する MessengerDataDownloader のメソッド相当のロジックを再実装/再利用
    # date_to_product_id はシンプルなのでそのまま実装
    def _date_to_product_id_local(date: datetime):
        year = date.year
        day_of_year = date.timetuple().tm_yday
        return f"magmsosci{year % 100:02d}{day_of_year:03d}"

    # construct_download_url_from_date も同様に再実装
    def _construct_download_url_from_date_local(date: datetime, session: requests.Session, base_url_local: str):
        product_id = _date_to_product_id_local(date)
        urn_id = f"urn:nasa:pds:mess-mag-calibrated:data-mso:{product_id}::1.0"
        
        year = date.year
        month = date.month
        month_ranges = {
            1: "001_031_JAN", 2: "032_060_FEB", 3: "061_090_MAR",
            4: "091_120_APR", 5: "121_151_MAY", 6: "152_181_JUN",
            7: "182_212_JUL", 8: "213_243_AUG", 9: "244_273_SEP",
            10: "274_304_OCT", 11: "305_334_NOV", 12: "335_365_DEC"
        }
        month_range = month_ranges.get(month, "UNKNOWN")
        # 閏年でない2月の修正 (元のコードのロジックを維持)
        if month == 2 and not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            month_range = "032_059_FEB"
        
        slot = f"/data/mess-mag-calibrated/data/mso/{year}/{month_range}"
        file_name_xml = f"MAGMSOSCI{product_id}_V08.xml" 
        data_file_tab = f"MAGMSOSCI{product_id}_V08.TAB" 
        
        url = f"{base_url_local}/ditdos/download?id={urn_id}&slot={slot}&file_name={file_name_xml}&data_file={data_file_tab}"
        
        try:
            # HEADリクエストでURLの存在を確認。
            head_response = session.head(url, timeout=30) 
            return url if head_response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None

    # download_zip_file もほぼ元のロジックを維持しつつ、セッションを引数で受け取る形に
    def _download_zip_file_local(url: str, output_path_str: str, target_date: datetime, session: requests.Session, info_local: bool):
        temp_file_path = None
        tab_files_in_zip = [] # ZIP内の元のTABファイル名リスト (削除ロジック用)
        extracted_tab_file_paths = [] # 実際に抽出されたTABファイルの絶対パス

        try:
            r = session.get(url, stream=True, timeout=120)
            r.raise_for_status() # HTTPエラーが発生した場合に例外を発生させる
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            Path(output_path_str).mkdir(parents=True, exist_ok=True) 

            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_contents = zip_ref.namelist()
                
                if not zip_contents:
                    if info_local:
                        print(f"  [Worker] Warning: ZIP archive is empty for {url}. No files to extract.")
                    return []
                
                # ZIP内のTABファイルを特定 (削除ロジックで使用するため、元の名前を保持)
                for zip_content in zip_contents:
                    if zip_content.lower().endswith('.tab') and not zip_content.endswith('/'):
                        tab_files_in_zip.append(zip_content) 

                if tab_files_in_zip and info_local:
                    display.debug('Worker_Download_Zip', f"  Found {len(tab_files_in_zip)} TAB files in ZIP: {', '.join(tab_files_in_zip)}")
                if not tab_files_in_zip:
                    return []

                zip_ref.extractall(output_path_str) # 全ファイルを展開
            
            # 一時ZIPファイルを削除
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                if info_local:
                    display.debug('Worker_Download_Zip', f"  Deleted temporary ZIP file: {temp_file_path}")
            
            # 展開されたファイルの中から、目的のTABファイル以外の不要なファイルを削除
            for f_path in Path(output_path_str).iterdir():
                # MacOSの隠しファイル (.DS_Store や ._*) は削除
                if f_path.name.startswith('._') or f_path.name == '.DS_Store':
                    try:
                        if f_path.exists(): f_path.unlink()
                        if info_local: display.debug('Worker_Download_Zip', f"  Deleted macOS hidden file: {f_path.name}")
                    except OSError as e:
                        if info_local:
                            if e.errno != 2: display.error('Worker_Download_Zip', f"  Could not delete macOS hidden file {f_path.name}: {e}")
                    continue
                
                # ZIP内のTABファイルリストに含まれるか、またはCDFファイルであれば残す
                # ZIP内の元のTABファイル名がそのまま展開されている前提
                is_target_tab = f_path.name in tab_files_in_zip
                is_cdf = f_path.name.lower().endswith('.cdf')

                if is_target_tab:
                    # これは残すべきTABファイルなので、リストに追加
                    extracted_tab_file_paths.append(str(f_path.resolve()))
                elif not is_cdf and f_path.is_file(): # CDFでも対象TABでもないファイルは削除
                    try:
                        f_path.unlink() 
                        if info_local:
                            print(f"  Deleted non-target file: {f_path.name}") # `non-TAB file` ではなく `non-target file`
                    except OSError as e:
                        if info_local:
                            print(f"  Could not delete {f_path.name}: {e}")
                        pass
                elif f_path.is_dir(): # 展開された空のディレクトリも削除 (オプション)
                    try:
                        if f_path.exists() and not any(f_path.iterdir()): 
                            f_path.rmdir()
                            if info_local: display.debug('Worker_Download_Zip', f"  Removed empty extracted directory: {f_path.name}")
                    except OSError as e:
                        if info_local: display.error('Worker_Download_Zip', f"  Could not remove directory {f_path.name}: {e}")
                        pass
            
            if not extracted_tab_file_paths and info_local:
                print(f"  No TAB files were successfully extracted for {target_date.strftime('%Y-%m-%d')}.")
            
            return extracted_tab_file_paths # 実際に展開されたTABファイルの絶対パスのリストを返す

        except requests.exceptions.RequestException as e:
            if info_local:
                display.error('Worker_Download_Zip', f"  Network or HTTP error during download for {target_date.strftime('%Y-%m-%d')}: {e}")
            return []
        except zipfile.BadZipFile as e:
            if info_local:
                display.error('Worker_Download_Zip', f"  Invalid ZIP file (could be corrupted or not a valid ZIP) for {target_date.strftime('%Y-%m-%d')}: {e}")
            return []
        except Exception as e:
            if info_local:
                display.error('Worker_Download_Zip', f"  An unexpected error occurred during download or processing for {target_date.strftime('%Y-%m-%d')}: {e}")
            return []
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    if info_local:
                        display.debug('Worker_Download_Zip', f"  Cleaned up residual temporary ZIP file: {temp_file_path}")
                except Exception as e:
                    if info_local:
                        display.error('Worker_Download_Zip', f"  Error during final temp file cleanup: {e}")

    # --- _process_single_day_download_and_convert の本体ロジック ---
    start_date_i = datetime.strptime(trange_i[0], '%Y-%m-%d %H:%M:%S')
    year_str = start_date_i.strftime('%Y')
    month_str = start_date_i.strftime('%m')
    date_dir = Path(output_root_dir) / "mag_mso" / year_str / month_str
    
    result_count = 0
    
    # CDFファイルが既に存在し、かつ更新が不要な場合はスキップ
    cdf_file_name_expected = f"messenger_mag_mso_{start_date_i.strftime('%Y%m%d')}.cdf"
    expected_cdf_path = date_dir / cdf_file_name_expected

    if expected_cdf_path.exists() and not update_cdf:
        if info:
            display.debug('Worker_Task', f"CDF file for {start_date_i.strftime('%Y-%m-%d')} already exists: {expected_cdf_path.name}. Skipping download.")
        return 1 # 既に存在するので成功としてカウント

    max_retries = 5 # リトライ回数を増やす (例: 3から5へ)
    initial_wait_time = 5 # 最初の待機時間 (秒)

    for current_retries in range(max_retries):
        if current_retries > 0:
            wait_time = initial_wait_time * (2 ** (current_retries - 1)) # 指数関数的バックオフ
            if info:
                print(f"  [Worker] Retrying download for {start_date_i.strftime('%Y-%m-%d')} in {wait_time} seconds (Attempt {current_retries + 1}/{max_retries})...")
            time.sleep(wait_time)

        try:
            download_url = _construct_download_url_from_date_local(start_date_i, local_session, base_url)
            
            if not download_url:
                if info:
                    print(f"  [Worker] Could not construct download URL for {start_date_i.strftime('%Y-%m-%d')}. Marking as failed for this attempt.")
                continue # 次のリトライへ

            if info:
                display.current_time_comment(comment=f'  [Worker] Downloading {start_date_i.strftime("%Y-%m-%d")} (Attempt {current_retries + 1}/{max_retries})...')
            
            retained_tab_file_paths_str = _download_zip_file_local(download_url, str(date_dir), start_date_i, local_session, info)
            
            if retained_tab_file_paths_str: # 実際にZIPから展開されたTABファイルの絶対パスリスト
                all_converted_successfully = True
                temp_result_count = 0
                for tab_file_full_path_str in retained_tab_file_paths_str:
                    tab_file_path_obj = Path(tab_file_full_path_str)
                    if tab_file_path_obj.exists():
                        if convert_tab_to_cdf(tab_file_full_path_str, str(date_dir), info=info, update_cdf=update_cdf):
                            temp_result_count += 1
                            # CDF変換後に元のTABファイルを削除
                            try:
                                tab_file_path_obj.unlink(missing_ok=True) 
                                if info:
                                    display.debug('Worker_Task', f"  Deleted TAB file after CDF conversion: {tab_file_path_obj.name}")
                            except Exception as e:
                                if info:
                                    display.error('Worker_Task', f"  Error deleting TAB file {tab_file_path_obj.name}: {e}")
                        else:
                            all_converted_successfully = False
                            if info:
                                print(f"  [Worker] Failed to convert TAB to CDF for {tab_file_path_obj.name}. This attempt failed.")
                            break # 1つでも変換失敗したらこの日の処理は失敗
                    else:
                        all_converted_successfully = False
                        if info:
                            display.error('Worker_Task', f"  Extracted TAB file {tab_file_path_obj.name} not found for CDF conversion. This attempt failed.")
                        break

                if all_converted_successfully and temp_result_count > 0: # 全て成功し、かつファイルが1つ以上変換された
                    result_count = temp_result_count
                    return result_count # 成功したので関数を抜ける
                else:
                    if info:
                        print(f"  [Worker] Conversion/Extraction failed for {start_date_i.strftime('%Y-%m-%d')}. Retrying if possible.")
            else:
                if info:
                    print(f"  [Worker] No TAB files were extracted for {start_date_i.strftime('%Y-%m-%d')}. Retrying if possible.")

        except requests.exceptions.Timeout as e:
            if info:
                display.error('Worker_Task', f"  Timeout during download for {start_date_i.strftime('%Y-%m-%d')}: {e}. Retrying.")
            # タイムアウトはリトライ対象
        except requests.exceptions.ConnectionError as e:
            if info:
                display.error('Worker_Task', f"  Connection error (e.g., WinError 1005) for {start_date_i.strftime('%Y-%m-%d')}: {e}. Retrying.")
            # 接続エラーもリトライ対象
        except requests.exceptions.RequestException as e:
            if info:
                display.error('Worker_Task', f"  Other network/HTTP error for {start_date_i.strftime('%Y-%m-%d')}: {e}. Retrying.")
            # その他のrequests関連エラーもリトライ対象
        except zipfile.BadZipFile as e:
            if info:
                display.error('Worker_Task', f"  Corrupted ZIP file for {start_date_i.strftime('%Y-%m-%d')}: {e}. Retrying.")
            # ZIPファイル破損もリトライ対象（再ダウンロードを試みる）
        except Exception as e:
            if info:
                display.error('Worker_Task', f"  Unexpected error for {start_date_i.strftime('%Y-%m-%d')}: {e}. Not retrying this type of error.")
            # 予期せぬエラーはリトライせずに終了
            return 0 
    
    # 全てのリトライが失敗した場合
    if info:
        print(f"  [Worker] Failed to download and convert {start_date_i.strftime('%Y-%m-%d')} after {max_retries} attempts.")
    return 0

def old_process_single_day_task(target_date: datetime, output_root_dir: str, info: bool, update_cdf: bool, base_url: str, session_headers: dict):
    """
    並列処理で実行される単一日のダウンロードおよびCDF変換タスク。
    この関数はメインクラスの外部に定義され、必要な情報を引数として受け取ります。
    
    Args:
        target_date (datetime): 処理対象の日付。
        output_root_dir (str): 全てのダウンロードのルートディレクトリ。
        info (bool): 情報メッセージを表示するかどうか。
        update_cdf (bool): 既存のCDFファイルを上書きするかどうか。
        base_url (str): PDSのベースURL。
        session_headers (dict): requestsセッションのヘッダー。
        
    Returns:
        int: 正常にダウンロード・変換されたファイルの数 (通常は0または1)。
    """
    # 各スレッド/プロセスで新しいrequestsセッションを作成
    # これにより、セッションがスレッドセーフでない問題やGILの問題を回避
    local_session = requests.Session()
    local_session.headers.update(session_headers)

    # MessengerDataDownloaderクラスのメソッドは直接呼び出せないため、
    # 必要なロジックをここで再実装するか、ヘルパー関数として渡す。
    # 今回は、MessengerDataDownloaderインスタンスのメソッドをここで利用するために、
    # そのロジックを独立した関数として定義し、ここで呼び出す形式を取る。
    
    # 日付からプロダクトIDを生成 (ヘルパー関数)
    def _date_to_product_id_local(date: datetime):
        year = date.year
        day_of_year = date.timetuple().tm_yday
        return f"magmsosci{year % 100:02d}{day_of_year:03d}"

    # ダウンロードURLの構築と存在チェック (ヘルパー関数)
    def _construct_download_url_from_date_local(date: datetime, session: requests.Session, base_url_local: str):
        product_id = _date_to_product_id_local(date)
        urn_id = f"urn:nasa:pds:mess-mag-calibrated:data-mso:{product_id}::1.0"
        
        year = date.year
        month = date.month
        month_ranges = {
            1: "001_031_JAN", 2: "032_060_FEB", 3: "061_090_MAR",
            4: "091_120_APR", 5: "121_151_MAY", 6: "152_181_JUN",
            7: "182_212_JUL", 8: "213_243_AUG", 9: "244_273_SEP",
            10: "274_304_OCT", 11: "305_334_NOV", 12: "335_365_DEC"
        }
        month_range = month_ranges.get(month, "UNKNOWN")
        if month == 2 and not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            month_range = "032_059_FEB"
        
        slot = f"/data/mess-mag-calibrated/data/mso/{year}/{month_range}"
        file_name_xml = f"MAGMSOSCI{product_id}_V08.xml" 
        data_file_tab = f"MAGMSOSCI{product_id}_V08.TAB" 
        
        url = f"{base_url_local}/ditdos/download?id={urn_id}&slot={slot}&file_name={file_name_xml}&data_file={data_file_tab}"
        
        try:
            head_response = session.head(url, timeout=10) 
            return url if head_response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None

    # ZIPファイルダウンロードと処理 (ヘルパー関数)
    def _download_zip_file_local(url: str, output_path_str: str, target_date_local: datetime, session: requests.Session, info_local: bool):
        temp_file_path = None
        renamed_tab_files = [] 
        output_path = Path(output_path_str)

        try:
            r = session.get(url, stream=True, timeout=60)
            r.raise_for_status()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk: temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            output_path.mkdir(parents=True, exist_ok=True) 

            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_contents = zip_ref.namelist()
                target_tab_member = None
                
                if not zip_contents:
                    if info_local: print(f"  [Worker] Warning: ZIP archive is empty for {url}.")
                    return [] 

                product_id = _date_to_product_id_local(target_date_local)
                expected_tab_file_in_zip = f"MAGMSOSCI{product_id}_V08.TAB"

                for member in zip_contents:
                    if (member.lower() == expected_tab_file_in_zip.lower()) and not member.endswith('/'):
                        target_tab_member = member
                        break
                    elif member.lower().endswith('.tab') and not member.endswith('/'):
                        if not target_tab_member: target_tab_member = member

                if not target_tab_member:
                    if info_local: print(f"  [Worker] Warning: No primary TAB file found in the ZIP archive for {url}.")
                    return []

                zip_ref.extractall(output_path)
            
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            processed_target_tab = False 

            for f_path in output_path.iterdir(): 
                if f_path.name.startswith('._') or f_path.name == '.DS_Store':
                    try:
                        if f_path.exists(): f_path.unlink()
                    except OSError as e:
                        if info_local and e.errno != 2: print(f"  [Worker] Could not delete macOS hidden file {f_path.name}: {e}")
                    continue 
                
                if f_path.is_file() and target_tab_member and f_path.name.lower() == target_tab_member.lower():
                    new_file_name = f"messenger_mag_mso_{target_date_local.strftime('%Y%m%d')}.tab"
                    new_file_path = f_path.parent / new_file_name
                    
                    try:
                        f_path.rename(new_file_path) 
                        renamed_tab_files.append(str(new_file_path.resolve()))
                        processed_target_tab = True
                    except OSError as e:
                        if info_local: print(f"  [Worker] Could not rename {f_path.name} to {new_file_name}: {e}")
                        renamed_tab_files.append(str(f_path.resolve())) 
                        processed_target_tab = True 
                elif f_path.is_file():
                    if not f_path.name.lower().endswith('.cdf'):
                        try:
                            f_path.unlink() 
                        except OSError as e:
                            if info_local: print(f"  [Worker] Could not delete {f_path.name}: {e}")
                            pass
                elif f_path.is_dir(): 
                    try:
                        if f_path.exists() and not any(f_path.iterdir()): 
                            f_path.rmdir()
                    except OSError as e:
                        if info_local: print(f"  [Worker] Could not remove directory {f_path.name}: {e}")
                        pass

            if not processed_target_tab and info_local: 
                print(f"  [Worker] Warning: Target TAB file '{target_tab_member}' not found or processed in '{output_path}'.")
            if not renamed_tab_files and info_local:
                print(f"  [Worker] No TAB files were successfully renamed in {output_path}.")
            
            return renamed_tab_files

        except requests.exceptions.RequestException as e:
            if info_local: print(f"  [Worker] Network or HTTP error during download for {target_date_local.strftime('%Y-%m-%d')}: {e}")
            return []
        except zipfile.BadZipFile as e:
            if info_local: print(f"  [Worker] Invalid ZIP file for {target_date_local.strftime('%Y-%m-%d')}: {e}")
            return []
        except Exception as e:
            if info_local: print(f"  [Worker] An unexpected error for {target_date_local.strftime('%Y-%m-%d')}: {e}")
            return []
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    if info_local: print(f"  [Worker] Error during temp file cleanup: {e}")

    # --- _process_single_day_taskの本体ロジック ---
    year_str = target_date.strftime('%Y')
    month_str = target_date.strftime('%m')
    date_dir = Path(output_root_dir) / "mag_mso" / year_str / month_str
    
    result_count = 0
    
    # CDFファイルが既に存在し、かつ更新が不要な場合はスキップ
    product_id_for_cdf = _date_to_product_id_local(target_date)
    expected_cdf_file_name = f"messenger_mag_mso_{target_date.strftime('%Y%m%d')}.cdf"
    expected_cdf_path = date_dir / expected_cdf_file_name

    if expected_cdf_path.exists() and not update_cdf:
        if info:
            print(f"  [Worker] CDF file for {target_date.strftime('%Y-%m-%d')} already exists: {expected_cdf_path.name}. Skipping download.")
        return 1 # 既に存在するので成功としてカウント
    
    # URLの存在チェックとダウンロードURLの構築
    download_url = _construct_download_url_from_date_local(target_date, local_session, base_url) 
    
    if download_url:
        # if info:
        #     display.current_time_comment(comment=f'  [Worker] Downloading {target_date.strftime('%Y-%m-%d')} ...')
        
        # ダウンロードとファイル処理
        # download_zip_file_local に target_date を渡す
        retained_tab_files_paths = _download_zip_file_local(download_url, str(date_dir), target_date, local_session, info)
        
        if retained_tab_files_paths:
            # 取得したTABファイルパスのリストをCDFに変換
            for tab_file_path_str in retained_tab_files_paths:
                # convert_tab_to_cdf はグローバル関数として定義されている
                # 引数に output_dir を渡し、update_cdf も渡す
                if convert_tab_to_cdf(tab_file_path_str, str(date_dir), info=info, update_cdf=update_cdf):
                    result_count += 1
                else:
                    # CDF変換が失敗した場合も、ダウンロードは成功しているため、ダウンロードカウントには含めないが、
                    # 失敗カウントを増やすロジックはメインスレッドで制御される。
                    pass 
                
                # CDF変換後に元のTABファイルを削除 (cleanup_downloaded_filesロジックの一部)
                try:
                    Path(tab_file_path_str).unlink(missing_ok=True)
                    # if info: print(f"  [Worker] Deleted temporary TAB file: {Path(tab_file_path_str).name}")
                except Exception as e:
                    if info: print(f"  [Worker] Error deleting TAB file {Path(tab_file_path_str).name}: {e}")

        else:
            if info:
                print(f"  [Worker] No TAB files retained from download for {target_date.strftime('%Y-%m-%d')}. Marking as failed.")
            # download_zip_fileが空のリストを返した場合 (ダウンロード失敗やデータなし)
            # ここでは0を返し、メインスレッドでfailed_countに加算される
    else:
        if info:
            print(f"  [Worker] Could not construct download URL for {target_date.strftime('%Y-%m-%d')}. Marking as failed.")
        # URLが見つからなかった場合
        # ここでは0を返し、メインスレッドでfailed_countに加算される

    return result_count # 正常にダウンロード・変換されたファイルの数を返す

# ---------------------------------
def old_download_zip_file01(self, url, output_path, show_progress=True, info=True):
    """
    ZIPファイルをダウンロードして展開し、TABファイルのみ残す（他は削除）
    """
    retained_tab_files = [] # 残ったTABファイルのリストを格納する

    try:
        r = self.session.get(url, stream=True, timeout=60)
        r.raise_for_status()

        # Content-Lengthが0の場合のチェック（念のため）
        if r.headers.get('Content-Length') == '0':
            if info:
                print(f"  Warning: Downloaded content length is 0 for {url}. Assuming no data.")
            return []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            for chunk in r.iter_content(chunk_size=32768):
                if chunk:
                    temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # ZIPファイルを展開
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist() # ZIPファイル内の全ファイル名リストを取得

            if not zip_contents:
                if info:
                    print(f"  Warning: ZIP archive is empty for {url}. No files to extract.")
                return []

            if info:
                print(f"  Extracting ZIP file contents to: {output_path}")
            zip_ref.extractall(output_path)
        Path(output_path).mkdir(parents=True, exist_ok=True)
        os.unlink(temp_file_path)
        # TABファイル以外を削除
        for f in Path(output_path).iterdir():
            if not (f.name.lower().endswith('.tab') or f.name.lower().endswith('.cdf')):
                try:
                    f.unlink()
                    if info:
                        print(f"Deleted: {f}")
                except Exception:
                    pass
        return True
    except Exception as e:
        if info:
            print(f"Download or extraction failed: {e}")
        return False

def old_download_zip_file(self, url, output_path, show_progress=True, info=True):
    """
    ZIPファイルをダウンロードして展開（高速化版）
    
    Parameters:
        url (str): ダウンロードURL
        output_path (str): 出力ディレクトリパス
        show_progress (bool): プログレスバーを表示するかどうか
        info (bool): クリーンアップメッセージを表示するかどうか
        
    Returns:
        bool: ダウンロード成功時True、失敗時False
    """
    try:
        if show_progress:
            print(f"  Downloading ZIP file from: {url}")
        
        response = self.session.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # ファイルサイズを取得（プログレスバー用）
        total_size = int(response.headers.get('content-length', 0))
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            if show_progress and total_size > 0:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                    for chunk in response.iter_content(chunk_size=32768):
                        if chunk:
                            temp_file.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        # ZIPファイルを展開
        if show_progress:
            print(f"  Extracting ZIP file to: {output_path}")
        
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_path)
        
        # ZIP展開が成功した場合のみディレクトリを作成
        Path(output_path).mkdir(parents=True, exist_ok=True)
        
        # 一時ファイルを削除
        os.unlink(temp_file_path)

        # TABファイルをCDFに変換（CDFがなければのみ）
        date_str = Path(output_path).parts[-1]  # 月ディレクトリの下が日付ディレクトリなら修正必要
        cdf_file_name = f"messenger_mag_mso_{date_str}.cdf"
        cdf_file_path = Path(output_path) / cdf_file_name
        tab_files = [f for f in Path(output_path).glob("*.TAB") if not f.name.startswith("._")]
        if not cdf_file_path.exists() and tab_files:
            for tab_file in tab_files:
                convert_tab_to_cdf(str(tab_file), output_path, info=info)
                try:
                    tab_file.unlink()
                    if info:
                        print(f"Deleted: {tab_file}")
                except FileNotFoundError:
                    pass
            # 変換後にのみcleanupを呼ぶ
            for ext in ["*.xml", "*.XML", "*.txt"]:
                for f in Path(output_path).glob(ext):
                    try:
                        f.unlink()
                        if info:
                            print(f"Deleted: {f}")
                    except FileNotFoundError:
                        pass
            cleanup_downloaded_files(output_path, info=info)

        # ここで cleanup_downloaded_files を呼び出す
        cleanup_downloaded_files(output_path, info=info)
        
        return True
    
    except Exception as e:
        return False


def old_download_data_for_period_serial(self, start_date, end_date, output_dir="messenger_data", info=True, update_cdf=True):
    """
    指定された期間のデータを1日ずつ逐次ダウンロード・変換・削除する（並列化なし）
    
    Parameters:
        start_date (datetime): 開始日
        end_date (datetime): 終了日
        output_dir (str): 出力ディレクトリ
        info (bool): メッセージ表示するかどうか
    Returns:
        bool: ダウンロード成功時True、失敗時False
    """
    print(f"=== MESSENGER Data Download (Serial) ===")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Output directory: {output_dir}")
    print("=" * 50)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    current_date = start_date
    downloaded_count = 0
    failed_count = 0
    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        year_str = current_date.strftime('%Y')
        month_str = current_date.strftime('%m')
        date_dir = Path(output_dir) / "mag_mso" / year_str / month_str
        cdf_file_name = f"messenger_mag_mso_{date_str}.cdf"
        cdf_file_path = date_dir / cdf_file_name
        if cdf_file_path.exists() and not update_cdf:
            if info:
                print(f"{current_date.strftime('%Y-%m-%d')}: CDF already exists, skipping...")
            current_date += timedelta(days=1)
            continue
        download_url = self.construct_download_url_from_date(current_date)
        if download_url:
            if info:
                display.current_time_comment(comment=f'Downloading {current_date.strftime('%Y-%m-%d')} ...')
                # print(f"{current_date.strftime('%Y-%m-%d')}: Downloading...")
            success = self.download_zip_file(download_url, str(date_dir), show_progress=False, info=info)
            if success:
                downloaded_count += 1
            else:
                failed_count += 1
        else:
            if info:
                print(f"Could not construct download URL for {current_date.strftime('%Y-%m-%d')}")
            failed_count += 1
        current_date += timedelta(days=1)
    print(f"\n=== Download Summary (Serial) ===")
    print(f"Total files downloaded: {downloaded_count}")
    print(f"Total files failed: {failed_count}")
    print(f"Output directory: {output_dir}")
    return downloaded_count > 0