import os
import re
from urllib.parse import urlparse
from datetime import datetime
from common import display
from ._downloader_mag_mso import _download_pds_tab_file, build_download_url_by_trange
from ._convert_tab_to_cdf import tab_to_cdf


def convert_tab_to_cdf_mag_mso(
        downloaded_tab_path,
        year=0,
        month=0
):
    output_dir = os.path.dirname(downloaded_tab_path)
    tab_filename = os.path.basename(downloaded_tab_path)
            
    match_yydoy = re.search(r'MAGMSOSCI(\d{5})', tab_filename)
    
    yyyymmdd_str = ""
    if match_yydoy:
        yydoy_str = match_yydoy.group(1) # '08012'
        
        # 2. YYDOYをYYYYMMDD形式に変換
        # %yは西暦下2桁、%jは通日（DOY）
        try:
            # '08012' -> 2008年1月12日
            date_obj = datetime.strptime(yydoy_str, '%y%j')
            yyyymmdd_str = date_obj.strftime('%Y%m%d') # '20080112'
        except ValueError:
            print(f"Warning: Failed to convert YYDOY {yydoy_str} to date.")
            # 変換失敗時のフォールバックとして、ディレクトリから取得した年と月を使用
            yyyymmdd_str = f"{year}{month:02}00" 
    else:
        print(f"Warning: Failed to extract YYDOY from filename: {tab_filename}. Using directory year/month.")
        yyyymmdd_str = f"{year}{month:02}00" # フォールバック
    
    # 3. 新しいファイル名を構築 (例: 'messenger_mag_mso_20080112.cdf')
    new_cdf_filename = f'messenger_mag_mso_{yyyymmdd_str}.cdf'
    
    # 4. output_cdfのパスを構築 (既存のディレクトリパス + 新しいファイル名)
    # Pathオブジェクトの親ディレクトリ (ダウンロードディレクトリ) と新しいファイル名を結合
    output_cdf = os.path.join(output_dir, new_cdf_filename) # tab_to_cdfに渡すためにstrに変換
    
    output_cdf_filepath = tab_to_cdf(
        downloaded_tab_path,
        output_cdf_path=output_cdf
    )
    return output_cdf_filepath


def download_mag_mso(
        trange,
        download_dir='',
        max_retries=3
):
    urls = build_download_url_by_trange(trange)

    if not urls:
        print("Error: No URL to download")
        return

    dict_month_abbr = {
        'JAN': 1,
        'FEB': 2,
        'MAR': 3,
        'APR': 4,
        'MAY': 5,
        'JUN': 6,
        'JUL': 7,
        'AUG': 8,
        'SEP': 9,
        'OCT': 10,
        'NOV': 11,
        'DEC': 12,
    }

    output_dir_base = os.path.join(
        download_dir,
        'messenger_data/mag_mso'
    )

    loop_start_time = datetime.now()
    for i, url in enumerate(urls):
        display.progress_bar(i, len(urls), loop_start_time)
        year = "unknown_year"
        month_abbr = "unknown_month"
        parsed_url = urlparse(url)
        query_params = dict(qc.split('=') for qc in parsed_url.query.split('&') if qc)
        slot_value = query_params.get('slot', '')
        
        # slot=/data/.../data/mso/2008/001_031_JAN の形式から抽出
        match = re.search(r'/data/mso/(\d{4})/\d{3}_\d{3}_([A-Z]{3})', slot_value)
        if match:
            year = match.group(1)   # 例: '2008'
            month_abbr = match.group(2) # 例: 'JAN'
        
        if month_abbr == 'unknown_month':
            month = 0
        else:
            month = dict_month_abbr[month_abbr]
            
        # 最終的な出力ディレクトリを構築
        output_dir = os.path.join(output_dir_base, year, f'{month:02}')

        file_name_match = re.search(r'data_file=([^&]+)', url)
        file_name = file_name_match.group(1) if file_name_match else "unknown_file.tab"
        
        downloaded_tab_path = _download_pds_tab_file(
            url,
            output_dir=output_dir, # 構築済みのPathオブジェクトを渡す
            max_retries=max_retries,
            info=True
        )
        
        if downloaded_tab_path:
            display.current_time_comment(comment=f"Downloaded: {downloaded_tab_path}")
            display.current_time_comment(comment='Converting tab to cdf...')

            output_cdf_filepath = convert_tab_to_cdf_mag_mso(
                downloaded_tab_path,
                year,
                month
            )
            
            # tab_filename = os.path.basename(downloaded_tab_path)
            
            # match_yydoy = re.search(r'MAGMSOSCI(\d{5})', tab_filename)
            
            # yyyymmdd_str = ""
            # if match_yydoy:
            #     yydoy_str = match_yydoy.group(1) # '08012'
                
            #     # 2. YYDOYをYYYYMMDD形式に変換
            #     # %yは西暦下2桁、%jは通日（DOY）
            #     try:
            #         # '08012' -> 2008年1月12日
            #         date_obj = datetime.strptime(yydoy_str, '%y%j')
            #         yyyymmdd_str = date_obj.strftime('%Y%m%d') # '20080112'
            #     except ValueError:
            #         print(f"Warning: Failed to convert YYDOY {yydoy_str} to date.")
            #         # 変換失敗時のフォールバックとして、ディレクトリから取得した年と月を使用
            #         yyyymmdd_str = f"{year}{month:02}00" 
            # else:
            #     print(f"Warning: Failed to extract YYDOY from filename: {tab_filename}. Using directory year/month.")
            #     yyyymmdd_str = f"{year}{month:02}00" # フォールバック
            
            # # 3. 新しいファイル名を構築 (例: 'messenger_mag_mso_20080112.cdf')
            # new_cdf_filename = f'messenger_mag_mso_{yyyymmdd_str}.cdf'
            
            # # 4. output_cdfのパスを構築 (既存のディレクトリパス + 新しいファイル名)
            # # Pathオブジェクトの親ディレクトリ (ダウンロードディレクトリ) と新しいファイル名を結合
            # output_cdf = os.path.join(output_dir, new_cdf_filename) # tab_to_cdfに渡すためにstrに変換
            
            # output_cdf_filepath = tab_to_cdf(
            #     downloaded_tab_path,
            #     output_cdf_path=output_cdf
            # )

            if output_cdf_filepath:
                display.current_time_comment(comment=f'Saved cdf: {output_cdf_filepath}')
                os.remove(downloaded_tab_path)
                display.current_time_comment(comment=f'Removed: {downloaded_tab_path}')
            
        else:
            print(f"Error: {url}")


    return

