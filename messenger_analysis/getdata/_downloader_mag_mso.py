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
import tarfile
import struct
import zlib
from typing import Optional, List
import re

from common import display, util
import common.time as time_common


def _download_pds_tab_file(
    url: str, 
    output_dir: str = '', 
    max_retries: int = 5,
    info: bool = True
) -> Optional[str]:
    """
    指定されたPDSのダウンロードURLからファイルをダウンロードし、TABファイルとして保存します。

    Args:
        url (str): ダウンロードするファイルの完全なURL。
        output_dir (str): ダウンロードしたファイルを展開/保存するディレクトリ。
        max_retries (int): 最大再試行回数。
        info (bool): 処理の詳細を表示するかどうか。

    Returns:
        str or None: ダウンロードおよび保存に成功したTABファイルの完全なパス、または失敗した場合は None。
    """
    
    temp_file_path = None
    # Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/555.55 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/555.55',
        'Accept': 'application/zip, application/octet-stream' 
    }

    parsed_url = urlparse(url)
    query_params = dict(qc.split('=') for qc in parsed_url.query.split('&') if qc)
    expected_data_file_name = query_params.get('data_file', 'downloaded_file.tab')
    
    MIN_VALID_SIZE_BYTES = 500 # 正常なデータファイルとして期待される最小サイズ（ZIPヘッダーやエラーメッセージでないことの確認用）

    for attempt in range(max_retries):
        try:
            if info:
                print(f"Attempt {attempt + 1}/{max_retries}: Downloading from {url[:70]}...")

            # --- 1. ダウンロードの実行 ---
            r = requests.get(url, stream=True, timeout=90, headers=headers)
            r.raise_for_status() 

            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            
            # --- 2. ダウンロードと一時ファイル保存 ---
            with tempfile.NamedTemporaryFile(delete=False, suffix='.download') as temp_file:
                pbar_desc = "Downloading"
                pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=pbar_desc, disable=(total_size == 0 and info))
                
                try:
                    for chunk in r.iter_content(chunk_size=32768):
                        if chunk:
                            temp_file.write(chunk)
                            downloaded_size += len(chunk)
                            pbar.update(len(chunk))
                finally:
                    pbar.close()
                
                temp_file_path = temp_file.name

            # --- 2.1. ダウンロードの完全性とサイズチェック (追加) ---
            if total_size != 0 and downloaded_size != total_size:
                raise requests.exceptions.RequestException(
                    f"Download incomplete. Expected {total_size} bytes, got {downloaded_size} bytes."
                )

            # ダウンロードが成功した場合でも、サイズが小さすぎる場合はエラーと見なす
            if downloaded_size < MIN_VALID_SIZE_BYTES:
                if info:
                    print(f"Warning: Downloaded file size ({downloaded_size} bytes) is too small.")
                # Content-Lengthが0または小さすぎる場合、サーバーが空の応答を返したと見なし、リトライ
                raise requests.exceptions.RequestException(
                    f"Downloaded data is likely empty or an error response ({downloaded_size} bytes)."
                )

            if output_dir: # output_dirが空でないことを確認
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                if info:
                    print(f"Target directory created: {output_dir}")
            else:
                if info:
                    print("Warning: output_dir is empty. Saving to current directory.")
                

            # --- 3. ZIPファイルとしての展開を試みる ---
            
            # シグネチャチェック
            with open(temp_file_path, 'rb') as f:
                header = f.read(4)
                f.seek(0)
                is_recognized_zip = zipfile.is_zipfile(f)
            
            if info:
                print(f"File signature (first 4 bytes): {header!r} (Size: {downloaded_size} bytes)") 
                print(f"zipfile.is_zipfile check: {is_recognized_zip}")
            
            is_zip_file = (header == b'PK\x03\x04') # マジックナンバーによるチェック
            
            final_tab_path = None
            extracted_successfully = False

            # --- 3.1. 標準/準標準 ZIP展開を試行 ---
            if is_zip_file or is_recognized_zip:
                try:
                    # allowZip64=True で非標準的な中央ディレクトリ構造を許容
                    with zipfile.ZipFile(temp_file_path, 'r', allowZip64=True) as zip_ref:
                        tab_files_downloaded: List[str] = [
                            f for f in zip_ref.namelist() 
                            if f.lower().endswith('.tab') and not f.endswith('/')
                        ]
                        
                        if tab_files_downloaded:
                            for zip_filename in tab_files_downloaded:
                                target_path = Path(output_dir) / Path(zip_filename).name
                                with zip_ref.open(zip_filename) as source, open(target_path, 'wb') as target:
                                    target.write(source.read())
                                final_tab_path = target_path
                            
                            if info:
                                print(f"Success (ZIP): Extracted content. Saved as {final_tab_path.name}")
                            extracted_successfully = True

                except zipfile.BadZipFile as bad_zip_error:
                    if info:
                        print(f"Error: ZIP extraction failed (BadZipFile: {bad_zip_error}). Trying RAW ZIP extraction fallback...")
            
            
            # --- 3.2. RAW ZIPデータ抽出 (中央ディレクトリを無視) と解凍を試行 ---
            # ZIPアーカイブ全体をスキャンし、目的のTABファイルのみを強制抽出する
            if is_zip_file and not extracted_successfully:
                if info:
                    print("Starting advanced RAW ZIP file scanning for target .TAB file (Handling zero-size headers)...")
                
                try:
                    target_file_name_lower = expected_data_file_name.lower()
                    
                    with open(temp_file_path, 'rb') as f:
                        full_raw_zip_data = f.read()
                        current_offset = 0
                        
                        found_target_data = False
                        
                        while current_offset < len(full_raw_zip_data):
                            # ローカルファイルヘッダー (PK\x03\x04) を検索
                            header_signature = b'PK\x03\x04'
                            signature_index = full_raw_zip_data.find(header_signature, current_offset)
                            
                            if signature_index == -1:
                                break 

                            # ヘッダーが見つかった位置にオフセットを更新
                            current_offset = signature_index 
                            
                            LOCAL_FILE_HEADER_SIZE = 30
                            
                            if len(full_raw_zip_data) < current_offset + LOCAL_FILE_HEADER_SIZE:
                                if info: print("Warning: Incomplete header found at end of file.")
                                break
                                
                            header_bytes = full_raw_zip_data[current_offset : current_offset + LOCAL_FILE_HEADER_SIZE]
                            
                            # 必要なフィールドを抽出
                            # H: compression_method(2B), L: compressed_size(4B), L: uncompressed_size(4B), H: file_name_length(2B), H: extra_field_length(2B)
                            try:
                                # compressed_size (インデックス1) は、非標準ZIPでは 0 になる可能性がある
                                header_data = struct.unpack('<H L L H H', header_bytes[8:10] + header_bytes[18:30])
                            except struct.error:
                                if info: print("Warning: Failed to unpack header data. Skipping 1 byte and retrying search.")
                                current_offset += 1
                                continue
                            
                            compression_method = header_data[0] # 0=Stored, 8=Deflate
                            # header_compressed_size = header_data[1] # ヘッダーから読み取ったサイズ (0の可能性がある)
                            file_name_length = header_data[3]
                            extra_field_length = header_data[4]

                            # ファイル名とエクストラフィールドのオフセットを計算
                            data_block_start_offset = current_offset + LOCAL_FILE_HEADER_SIZE + file_name_length + extra_field_length
                            
                            if len(full_raw_zip_data) < data_block_start_offset:
                                if info: print("Warning: Incomplete file header/name/extra fields.")
                                current_offset += 1
                                continue
                            
                            # ファイル名を取得
                            file_name_bytes = full_raw_zip_data[
                                current_offset + LOCAL_FILE_HEADER_SIZE : 
                                current_offset + LOCAL_FILE_HEADER_SIZE + file_name_length
                            ]
                            file_name = file_name_bytes.decode('utf-8', errors='ignore')
                            
                            if info:
                                print(f"Found file header: '{file_name}' (Compression: {compression_method})") # header_compressed_sizeの表示を削除

                            # 目的のファイル名かチェック
                            if file_name.lower().endswith(target_file_name_lower):
                                
                                # --- データブロックのサイズを次のヘッダーから推測する (ストリームZIP対応) ---
                                
                                # 次のローカルファイルヘッダー (PK\x03\x04) を検索
                                next_signature_index = full_raw_zip_data.find(header_signature, data_block_start_offset)
                                
                                # データブロックの終端オフセットを決定
                                if next_signature_index == -1:
                                    # 次のヘッダーがなければ、データの終端はファイルの終端
                                    data_end_offset = len(full_raw_zip_data)
                                else:
                                    # データは次のヘッダーの直前で終わる
                                    data_end_offset = next_signature_index
                                    
                                actual_compressed_size = data_end_offset - data_block_start_offset
                                
                                if info:
                                    print(f"--> Inferred compressed size: {actual_compressed_size} bytes.")
                                
                                if actual_compressed_size <= 0:
                                    if info: print("Error: Inferred size is 0 or negative. Skipping.")
                                    # 次のファイルヘッダーから処理を再開
                                    current_offset = data_end_offset 
                                    continue
                                
                                # TABファイルのデータブロックを取得 (推測したサイズを使用)
                                raw_data_block = full_raw_zip_data[data_block_start_offset : data_block_start_offset + actual_compressed_size]
                                
                                extracted_data = raw_data_block
                                
                                # 圧縮方法に基づいて解凍処理を行う
                                if compression_method == 8: # Deflate圧縮
                                    if info:
                                        print("--> Decompressing target file (Deflate)...")
                                    try:
                                        # -zlib.MAX_WBITS を使用して、ZIPヘッダーがない生のDeflateストリームを処理
                                        extracted_data = zlib.decompress(raw_data_block, -zlib.MAX_WBITS) 
                                    except zlib.error as decompress_error:
                                        if info: print(f"Error: Decompression failed for {file_name} ({decompress_error}). Skipping.")
                                        current_offset = data_end_offset # 失敗した場合も次のヘッダーへ進む
                                        continue
                                        
                                elif compression_method == 0:
                                    if info: print("--> Target file is Stored (No decompression needed).")
                                else:
                                    if info: print(f"--> Compression method: Unknown/Unsupported (ID {compression_method}). Saving raw data.")
                                
                                # データの内容をそのまま保存
                                final_tab_path = Path(output_dir) / expected_data_file_name
                                
                                with open(final_tab_path, 'wb') as out_f:
                                    out_f.write(extracted_data)
                                
                                if info:
                                    print(f"Success (RAW ZIP Scan): Saved target content as {final_tab_path.name} (Size: {len(extracted_data)} bytes).")
                                
                                extracted_successfully = True
                                found_target_data = True
                                break # 目的のファイルが見つかったのでループを終了

                            # 目的のファイルでなかった場合、次のヘッダー検索に進むためにオフセットを更新
                            current_offset += 1 # 1バイトだけ進めて、次のシグネチャを再検索する (安全のため)
                            
                        if found_target_data:
                            # 抽出成功した場合、一時ファイルを削除してリターン
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)
                            return str(final_tab_path)
                        else:
                            if info:
                                print("Error: Target .TAB file not found during RAW ZIP scanning.")
                            
                        
                except Exception as raw_zip_error:
                    if info:
                        print(f"Error: Advanced RAW ZIP scanning failed ({raw_zip_error}). Trying TAR fallback...")
                        
            
            # --- 3.3. TAR展開を試行 (最終のアーカイブ展開オプション) ---
            if not extracted_successfully:
                try:
                    with tarfile.open(temp_file_path, 'r:*') as tar_ref:
                        tab_members = [
                            m for m in tar_ref.getmembers() 
                            if m.name.lower().endswith('.tab') and m.isfile()
                        ]

                        if tab_members:
                            for tar_member in tab_members:
                                target_name = Path(tar_member.name).name
                                target_path = Path(output_dir) / target_name
                                with tar_ref.extractfile(tar_member) as source, open(target_path, 'wb') as target:
                                    target.write(source.read())
                                final_tab_path = target_path

                            if info:
                                print(f"Success (TAR): Extracted content. Saved as {final_tab_path.name}")
                            extracted_successfully = True
                            
                        elif info:
                            print("Warning: TAR file opened successfully, but no .tab file found.")
                            
                except tarfile.TarError as tar_error:
                    if info:
                        print(f"Error: TAR extraction failed (TarError: {tar_error}).")
            
            
            # --- 4. 展開結果の処理（最終フォールバック） ---
            if extracted_successfully and final_tab_path:
                # 成功した場合
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                return str(final_tab_path)
            
            # *** CRITICAL FALLBACK (最終中の最終手段 - バイナリ保存) ***
            elif is_zip_file and not extracted_successfully:
                # ZIPシグネチャがあり、すべての解凍/抽出に失敗した場合
                if info:
                    print(f"CRITICAL FALLBACK: All extraction methods failed. Saving file as raw binary data {expected_data_file_name}")

                final_tab_path = Path(output_dir) / expected_data_file_name
                Path(temp_file_path).rename(final_tab_path)
                
                temp_file_path = None 
                return str(final_tab_path)

            elif not is_zip_file and not extracted_successfully:
                 # ZIPシグネチャがなく、ZIPでもTARでもない場合 (生のデータ)
                if info:
                    print(f"Warning: Not an archive. Assuming raw TAB data.")
                
                final_tab_path = Path(output_dir) / expected_data_file_name
                Path(temp_file_path).rename(final_tab_path)
                if info:
                    print(f"Success: Saved raw data as {final_tab_path.name}")
                return str(final_tab_path)
            else:
                # ダウンロードはできたが、ZIP/TAR展開に失敗し、フォールバックもできない場合
                if info:
                    print("Error: File is an archive but extraction failed. Giving up.")
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                return None


        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                if info:
                    print(f"Request failed: {e}. Retrying in {wait_time} seconds.")
                time.sleep(wait_time)
                # エラー発生時は、一時ファイルを確実に削除
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    temp_file_path = None
            else:
                if info:
                    print(f"Error: Download failed after {max_retries} attempts.")
                # 最終的に失敗した場合も、一時ファイルを削除
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                return None
        except Exception as e:
            if info:
                print(f"An unexpected error occurred: {e}")
            # エラー発生時は、一時ファイルを確実に削除
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return None
        finally:
            # 処理が成功してリターンされる場合以外で temp_file_path が残っている場合（例: 途中でcontinueされた場合など）を最終的に削除
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    return None

def old_download_pds_tab_file(
    url: str, 
    output_dir: str = '', 
    max_retries: int = 5, # リトライ回数を増やしました
    info: bool = True
) -> Optional[str]:
    """
    指定されたPDSのダウンロードURLからファイルをダウンロードし、TABファイルとして保存します。
    ダウンロードの完全性をContent-Lengthでチェックし、不完全な場合はリトライします。
    
    ZIP展開に失敗した場合、非標準ZIPまたはTARファイルとして処理を試みます。
    最終手段として、ZIPシグネチャがあるにもかかわらず展開できない場合、RAWデータとして強制保存します。

    Args:
        url (str): ダウンロードするファイルの完全なURL。
        output_dir (str): ダウンロードしたファイルを展開/保存するディレクトリ。
        max_retries (int): 最大再試行回数。
        info (bool): 処理の詳細を表示するかどうか。

    Returns:
        str or None: ダウンロードおよび保存に成功したTABファイルの完全なパス、または失敗した場合は None。
    """
    
    temp_file_path = None
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Accept: application/zip を追加し、ZIP形式を明示的に要求する
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/555.55 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/555.55',
        'Accept': 'application/zip, application/octet-stream' 
    }

    parsed_url = urlparse(url)
    query_params = dict(qc.split('=') for qc in parsed_url.query.split('&') if qc)
    expected_data_file_name = query_params.get('data_file', 'downloaded_file.tab')
    
    for attempt in range(max_retries):
        try:
            if info:
                print(f"Attempt {attempt + 1}/{max_retries}: Downloading from {url[:70]}...")

            # --- 1. ダウンロードの実行 ---
            r = requests.get(url, stream=True, timeout=90, headers=headers)
            r.raise_for_status() 

            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            
            # --- 2. ダウンロードと一時ファイル保存 ---
            with tempfile.NamedTemporaryFile(delete=False, suffix='.download') as temp_file:
                pbar_desc = "Downloading"
                pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=pbar_desc, disable=(total_size == 0 and info))
                
                try:
                    for chunk in r.iter_content(chunk_size=32768):
                        if chunk:
                            temp_file.write(chunk)
                            downloaded_size += len(chunk)
                            pbar.update(len(chunk))
                finally:
                    pbar.close()
                
                temp_file_path = temp_file.name

            # ダウンロードの完全性チェック
            if total_size != 0 and downloaded_size != total_size:
                raise requests.exceptions.RequestException(
                    f"Download incomplete. Expected {total_size} bytes, got {downloaded_size} bytes."
                )

            # --- 3. ZIPファイルとしての展開を試みる ---
            
            # シグネチャチェック
            with open(temp_file_path, 'rb') as f:
                header = f.read(4)
                f.seek(0)
                is_recognized_zip = zipfile.is_zipfile(f)
            
            if info:
                print(f"File signature (first 4 bytes): {header!r} (Size: {downloaded_size} bytes)") 
                print(f"zipfile.is_zipfile check: {is_recognized_zip}")
            
            is_zip_file = (header == b'PK\x03\x04') # マジックナンバーによるチェック
            
            final_tab_path = None
            extracted_successfully = False

            # --- 3.1. 標準/準標準 ZIP展開を試行 ---
            if is_zip_file or is_recognized_zip:
                try:
                    # allowZip64=True で非標準的な中央ディレクトリ構造を許容
                    with zipfile.ZipFile(temp_file_path, 'r', allowZip64=True) as zip_ref:
                        tab_files_downloaded: List[str] = [
                            f for f in zip_ref.namelist() 
                            if f.lower().endswith('.tab') and not f.endswith('/')
                        ]
                        
                        if tab_files_downloaded:
                            for zip_filename in tab_files_downloaded:
                                target_path = Path(output_dir) / Path(zip_filename).name
                                with zip_ref.open(zip_filename) as source, open(target_path, 'wb') as target:
                                    target.write(source.read())
                                final_tab_path = target_path
                            
                            if info:
                                print(f"Success (ZIP): Extracted content. Saved as {final_tab_path.name}")
                            extracted_successfully = True

                except zipfile.BadZipFile as bad_zip_error:
                    if info:
                        print(f"Error: ZIP extraction failed (BadZipFile: {bad_zip_error}). Trying RAW ZIP extraction fallback...")
            
            
            # --- 3.2. RAW ZIPデータ抽出 (中央ディレクトリを無視) と解凍を試行 ---
            # ZIPアーカイブ全体をスキャンし、目的のTABファイルのみを強制抽出する
            if is_zip_file and not extracted_successfully:
                if info:
                    print("Starting advanced RAW ZIP file scanning for target .TAB file (Handling zero-size headers)...")
                
                try:
                    target_file_name_lower = expected_data_file_name.lower()
                    
                    with open(temp_file_path, 'rb') as f:
                        full_raw_zip_data = f.read()
                        current_offset = 0
                        
                        found_target_data = False
                        
                        while current_offset < len(full_raw_zip_data):
                            # ローカルファイルヘッダー (PK\x03\x04) を検索
                            header_signature = b'PK\x03\x04'
                            signature_index = full_raw_zip_data.find(header_signature, current_offset)
                            
                            if signature_index == -1:
                                break 

                            # ヘッダーが見つかった位置にオフセットを更新
                            current_offset = signature_index 
                            
                            LOCAL_FILE_HEADER_SIZE = 30
                            
                            if len(full_raw_zip_data) < current_offset + LOCAL_FILE_HEADER_SIZE:
                                if info: print("Warning: Incomplete header found at end of file.")
                                break
                                
                            header_bytes = full_raw_zip_data[current_offset : current_offset + LOCAL_FILE_HEADER_SIZE]
                            
                            # 必要なフィールドを抽出
                            # H: compression_method(2B), L: compressed_size(4B), L: uncompressed_size(4B), H: file_name_length(2B), H: extra_field_length(2B)
                            try:
                                # compressed_size (インデックス1) は、非標準ZIPでは 0 になる可能性がある
                                header_data = struct.unpack('<H L L H H', header_bytes[8:10] + header_bytes[18:30])
                            except struct.error:
                                if info: print("Warning: Failed to unpack header data. Skipping 1 byte and retrying search.")
                                current_offset += 1
                                continue
                            
                            compression_method = header_data[0] # 0=Stored, 8=Deflate
                            # header_compressed_size = header_data[1] # ヘッダーから読み取ったサイズ (0の可能性がある)
                            file_name_length = header_data[3]
                            extra_field_length = header_data[4]

                            # ファイル名とエクストラフィールドのオフセットを計算
                            data_block_start_offset = current_offset + LOCAL_FILE_HEADER_SIZE + file_name_length + extra_field_length
                            
                            if len(full_raw_zip_data) < data_block_start_offset:
                                if info: print("Warning: Incomplete file header/name/extra fields.")
                                current_offset += 1
                                continue
                            
                            # ファイル名を取得
                            file_name_bytes = full_raw_zip_data[
                                current_offset + LOCAL_FILE_HEADER_SIZE : 
                                current_offset + LOCAL_FILE_HEADER_SIZE + file_name_length
                            ]
                            file_name = file_name_bytes.decode('utf-8', errors='ignore')
                            
                            if info:
                                print(f"Found file header: '{file_name}' (Compression: {compression_method})") # header_compressed_sizeの表示を削除

                            # 目的のファイル名かチェック
                            if file_name.lower().endswith(target_file_name_lower):
                                
                                # --- データブロックのサイズを次のヘッダーから推測する (ストリームZIP対応) ---
                                
                                # 次のローカルファイルヘッダー (PK\x03\x04) を検索
                                next_signature_index = full_raw_zip_data.find(header_signature, data_block_start_offset)
                                
                                # データブロックの終端オフセットを決定
                                if next_signature_index == -1:
                                    # 次のヘッダーがなければ、データの終端はファイルの終端
                                    data_end_offset = len(full_raw_zip_data)
                                else:
                                    # データは次のヘッダーの直前で終わる
                                    data_end_offset = next_signature_index
                                    
                                actual_compressed_size = data_end_offset - data_block_start_offset
                                
                                if info:
                                    print(f"--> Inferred compressed size: {actual_compressed_size} bytes.")
                                
                                if actual_compressed_size <= 0:
                                    if info: print("Error: Inferred size is 0 or negative. Skipping.")
                                    # 次のファイルヘッダーから処理を再開
                                    current_offset = data_end_offset 
                                    continue
                                
                                # TABファイルのデータブロックを取得 (推測したサイズを使用)
                                raw_data_block = full_raw_zip_data[data_block_start_offset : data_block_start_offset + actual_compressed_size]
                                
                                extracted_data = raw_data_block
                                
                                # 圧縮方法に基づいて解凍処理を行う
                                if compression_method == 8: # Deflate圧縮
                                    if info:
                                        print("--> Decompressing target file (Deflate)...")
                                    try:
                                        # -zlib.MAX_WBITS を使用して、ZIPヘッダーがない生のDeflateストリームを処理
                                        extracted_data = zlib.decompress(raw_data_block, -zlib.MAX_WBITS) 
                                    except zlib.error as decompress_error:
                                        if info: print(f"Error: Decompression failed for {file_name} ({decompress_error}). Skipping.")
                                        current_offset = data_end_offset # 失敗した場合も次のヘッダーへ進む
                                        continue
                                        
                                elif compression_method == 0:
                                    if info: print("--> Target file is Stored (No decompression needed).")
                                else:
                                    if info: print(f"--> Compression method: Unknown/Unsupported (ID {compression_method}). Saving raw data.")
                                
                                # データの内容をそのまま保存
                                final_tab_path = Path(output_dir) / expected_data_file_name
                                
                                with open(final_tab_path, 'wb') as out_f:
                                    out_f.write(extracted_data)
                                
                                if info:
                                    print(f"Success (RAW ZIP Scan): Saved target content as {final_tab_path.name} (Size: {len(extracted_data)} bytes).")
                                
                                extracted_successfully = True
                                found_target_data = True
                                break # 目的のファイルが見つかったのでループを終了

                            # 目的のファイルでなかった場合、次のヘッダー検索に進むためにオフセットを更新
                            # 次のヘッダーは、現在のヘッダーの開始位置からデータブロックの末尾の直後にあるはず
                            # ここではヘッダーから読み取ったサイズではなく、ヘッダーに記載の圧縮サイズ（0の可能性がある）と非圧縮サイズ、データ記述子の有無など複雑なため、
                            # シンプルに次のPK\x03\x04シグネチャの検索に頼るためにcurrent_offsetを更新せず、ループの先頭で次のシグネチャを検索し続ける
                            current_offset += 1 # 1バイトだけ進めて、次のシグネチャを再検索する (安全のため)
                            
                        if found_target_data:
                            temp_file_path = None
                            return str(final_tab_path)
                        else:
                            if info:
                                print("Error: Target .TAB file not found during RAW ZIP scanning.")
                            
                        
                except Exception as raw_zip_error:
                    if info:
                        print(f"Error: Advanced RAW ZIP scanning failed ({raw_zip_error}). Trying TAR fallback...")
                        
            
            # --- 3.3. TAR展開を試行 (最終のアーカイブ展開オプション) ---
            if not extracted_successfully:
                try:
                    with tarfile.open(temp_file_path, 'r:*') as tar_ref:
                        tab_members = [
                            m for m in tar_ref.getmembers() 
                            if m.name.lower().endswith('.tab') and m.isfile()
                        ]

                        if tab_members:
                            for tar_member in tab_members:
                                target_name = Path(tar_member.name).name
                                target_path = Path(output_dir) / target_name
                                with tar_ref.extractfile(tar_member) as source, open(target_path, 'wb') as target:
                                    target.write(source.read())
                                final_tab_path = target_path

                            if info:
                                print(f"Success (TAR): Extracted content. Saved as {final_tab_path.name}")
                            extracted_successfully = True
                            
                        elif info:
                            print("Warning: TAR file opened successfully, but no .tab file found.")
                            
                except tarfile.TarError as tar_error:
                    if info:
                        print(f"Error: TAR extraction failed (TarError: {tar_error}).")
            
            
            # --- 4. 展開結果の処理（最終フォールバック） ---
            if extracted_successfully and final_tab_path:
                # 成功した場合
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                return str(final_tab_path)
            
            # *** CRITICAL FALLBACK (最終中の最終手段 - バイナリ保存) ***
            # ZIPシグネチャがあり、すべての解凍/抽出に失敗した場合、ファイルをそのまま期待される.tab名で保存
            elif is_zip_file and not extracted_successfully:
                if info:
                    print(f"CRITICAL FALLBACK: All extraction methods failed. Saving file as raw binary data {expected_data_file_name}")

                final_tab_path = Path(output_dir) / expected_data_file_name
                # 一時ファイルをリネームして強制的に保存
                Path(temp_file_path).rename(final_tab_path)
                
                temp_file_path = None 
                return str(final_tab_path)

            elif not is_zip_file and not extracted_successfully:
                 # ZIPシグネチャがなく、ZIPでもTARでもない場合 (生のデータ)
                if info:
                    print(f"Warning: Not an archive. Assuming raw TAB data.")
                
                final_tab_path = Path(output_dir) / expected_data_file_name
                Path(temp_file_path).rename(final_tab_path)
                if info:
                    print(f"Success: Saved raw data as {final_tab_path.name}")
                return str(final_tab_path)
            else:
                # ダウンロードはできたが、ZIP/TAR展開に失敗し、フォールバックもできない場合（ほぼ発生しないはず）
                if info:
                    print("Error: File is an archive but extraction failed. Giving up.")
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                return None


        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                if info:
                    print(f"Request failed: {e}. Retrying in {wait_time} seconds.")
                time.sleep(wait_time)
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    temp_file_path = None
            else:
                if info:
                    print(f"Error: Download failed after {max_retries} attempts.")
                return None
        except Exception as e:
            if info:
                print(f"An unexpected error occurred: {e}")
            return None
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                # temp_file_path が None になっていない場合（つまりリネームされていない場合）のみ削除
                os.unlink(temp_file_path)
    
    return None


# ----------------------------------------------------------
# Build download URL
# ----------------------------------------------------------
def old_build_download_url_trange(
        trange
):
    """
    /2008/001_031_JAN&file_name=MAGMSOSCI08012_V08.xml&data_file=MAGMSOSCI08012_V08.TAB
    """
    base_url = 'https://pds-ppi.igpp.ucla.edu/ditdos/download?id=urn:nasa:pds:mess-mag-calibrated:data-mso:magmsosci08012::1.0&slot=/data/mess-mag-calibrated/data/mso'
    
    time_list = util.make_time_list(trange, 1, 'days')
    for i, trange_i in enumerate(time_list):
        dt_start = time_common.convert(trange_i[0], 'str', 'datetime')

    return





def date_to_product_id(date: datetime) -> str:
    """
    日付に対応するPDSの製品IDの一部 (YYDOY) を構築する。
    ファイル名は日単位 (YY + DOY) であると仮定する。

    Args:
        date (datetime): 対象日付

    Returns:
        str: 年下2桁とDOYの3桁 (例: 2008年1月1日 -> '08001')
    """
    year_abbr = str(date.year)[-2:]
    
    # 渡された日付の DOY をそのまま使用する
    doy = date.timetuple().tm_yday
    return f"{year_abbr}{doy:03d}"

def get_doy_range(dt: datetime) -> str:
    """
    日付に対応するPDSのDOY範囲と月略称を取得する (例: '001_031_JAN')
    """
    DOY_RANGES = {
    1: "001_031_JAN", 2: "032_060_FEB", 3: "061_090_MAR", 
    4: "091_120_APR", 5: "121_151_MAY", 6: "152_181_JUN", 
    7: "182_212_JUL", 8: "213_243_AUG", 9: "244_273_SEP", 
    10: "274_304_OCT", 11: "305_334_NOV", 12: "335_365_DEC"
}

    return DOY_RANGES.get(dt.month, f"{dt.year} Unknown Month {dt.month}")


def build_download_url_by_trange(trange: List[str]) -> Optional[List[str]]:
    """
    指定された期間 [start_time, end_time] に対応するMESSENGER MAGデータの
    ダウンロードURLリストを構築する。
    ファイルは日単位 (MAGMSOSCIYYDOY_V08.TAB) で存在するが、ディレクトリ構造は月単位
    (001_031_JAN) であるという前提で、期間内のすべての日に対してURLを生成する。

    Args:
        trange (List[str]): 期間を表す文字列のリスト。
                            例: ['2008-01-01 00:00:00', '2008-01-10 00:00:00']

    Returns:
        Optional[List[str]]: 構築されたダウンロードURLのリスト。期間形式が無効な場合はNone。
    """
    if len(trange) != 2:
        print("Error: trange must contain exactly two time strings: [start_time, end_time].")
        return None
        
    start_time_str, end_time_str = trange
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    try:
        start_dt = datetime.strptime(start_time_str, TIME_FORMAT)
        # ダウンロードするファイルは、終了日 (end_dt) の前日までをカバーする
        end_dt = datetime.strptime(end_time_str, TIME_FORMAT)
    except ValueError:
        print(f"Error: Invalid time format. Use '{TIME_FORMAT}'.")
        return None

    if start_dt >= end_dt:
        print("Error: Start time must be strictly before end time.")
        return None
        
    # --- 期間内のすべての日を特定し、各日の情報 (YYYY-MM-DD) を収集 ---
    
    # ダウンロード対象は、開始日から終了日の前日までの日付 (日単位ファイルのため)
    current_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    # end_dt の日付は含まない (ex: 1/1 -> 1/10 は 1/1, 1/2, ..., 1/9 の9ファイル)
    end_dt_day = end_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    unique_dates = [] # 各ファイルの代表日 (YYYY-MM-DD 00:00:00)
    
    while current_dt < end_dt_day:
        unique_dates.append(current_dt)
        current_dt += timedelta(days=1)
            
    if not unique_dates:
        return None

    # --- URLの構築 ---

    BASE_URL = 'https://pds-ppi.igpp.ucla.edu/ditdos/download'
    DYNAMIC_ID_PREFIX = 'urn:nasa:pds:mess-mag-calibrated:data-mso:magmsosci'
    DYNAMIC_ID_SUFFIX = '::1.0'
    
    download_urls = []
    
    # URLの重複を避けるためにセットを使用（このデータセットでは通常発生しないが安全のため）
    generated_urls = set()

    for date_to_download in unique_dates:
        
        # 1. Product ID (YYDOY) を構築 (例: '08001', '08002', ...)
        product_id = date_to_product_id(date_to_download)
        
        # 2. URN ID を構築
        urn_id = f"{DYNAMIC_ID_PREFIX}{product_id}{DYNAMIC_ID_SUFFIX}"
        
        # 3. Slot Path (ディレクトリ) を構築 (月単位のパス)
        year = date_to_download.year
        month_range = get_doy_range(date_to_download)
        slot = f"/data/mess-mag-calibrated/data/mso/{year}/{month_range}"
        
        # 4. File Names を構築 (日単位のファイル名)
        file_name = f"MAGMSOSCI{product_id}_V08.xml"
        data_file = f"MAGMSOSCI{product_id}_V08.TAB"

        # 5. URLの組み立て
        url = (
            f"{BASE_URL}?id={urn_id}"
            f"&slot={slot}"
            f"&file_name={file_name}"
            f"&data_file={data_file}"
        )
        
        if url not in generated_urls:
            download_urls.append(url)
            generated_urls.add(url)
        
    return download_urls


# ----------------------------------------------------------
# URL存在チェック関数
# ----------------------------------------------------------

def check_url_existence(url: str, info: bool = False) -> Optional[str]:
    """
    単一のURLに対してHTTPリクエストを実行し、有効なデータ応答 (200 OK) があるかを確認します。
    Content-Lengthが動的に生成されるPDSサーバーに対応するため、サイズチェックは行いません。
    """
    try:
        # HEADリクエストではなくGETリクエストを使用することで、PDSサーバーの動的処理に対応します
        # stream=Trueで、データ全体をダウンロードせずにヘッダーとステータスをチェック
        response = requests.get(url, stream=True, timeout=10)
        
        # 200 OK でない場合はここで例外発生
        response.raise_for_status() 
        
        # NOTE: Content-Lengthのチェック（<=500バイトで無効とするロジック）を削除しました。
        # 200 OKが返却されれば、有効なURLであると判断します。
        
        if info:
            total_size = int(response.headers.get('content-length', 0))
            print(f"-> Valid: {url[:40]}... (Status: 200, Content-Length: {total_size} bytes)")
        
        return url
        
    except requests.exceptions.RequestException as e:
        status_code = getattr(e.response, 'status_code', 'N/A')
        if info:
            print(f"-> Invalid: {url[:40]}... (Status: {status_code} or Connection Error)")
        return None
    except Exception:
        if info:
            print(f"-> Invalid: {url[:40]}... (Unexpected Error)")
        return None

def check_valid_urls(urls: List[str], max_workers: int = 10, info: bool = True) -> List[str]:
    """
    構築されたURLリストを並列でチェックし、有効なURLのみをフィルタリングして返します。

    Args:
        urls (List[str]): チェックするURLのリスト。
        max_workers (int): 並列実行するスレッドの最大数。
        info (bool): 処理の詳細を表示するかどうか。

    Returns:
        List[str]: 存在するファイルに対応する有効なURLのリスト。
    """
    if info:
        print(f"Starting concurrent validity check for {len(urls)} URLs...")
        
    valid_urls = []
    
    # ThreadPoolExecutorを使用して並列でURLをチェック
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 全てのURLチェックを提出
        future_to_url = {executor.submit(check_url_existence, url, False): url for url in urls}
        
        # tqdmで進捗を表示
        for future in tqdm(
            concurrent.futures.as_completed(future_to_url), 
            total=len(urls), 
            desc="Checking URL Existence",
            disable=not info
        ):
            valid_url = future.result()
            if valid_url:
                valid_urls.append(valid_url)
                
    if info:
        print(f"Validity check complete. Found {len(valid_urls)} valid URL(s) out of {len(urls)}.")
        
    return sorted(valid_urls)

