import re
from datetime import datetime
from common import display, time, cdf


def convert_horizons_taa_txt_to_cdf(
        input_txt_filepath,
        output_cdf_filepath
):
    """
    JPL HorizonsのテキストデータからTrue Anomaly(TAA)を抽出し、CDFファイルを作成する。
    """
    times_datetime = []
    taa_values = []

    display.info(f"Reading: {input_txt_filepath}")
    
    with open(input_txt_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # $$SOE (Start of Ephemeris) と $$EOE (End of Ephemeris) の間を抽出
    data_section = re.search(r'\$\$SOE(.*?)\$\$EOE', content, re.DOTALL)
    if not data_section:
        print("Error: Data section ($$SOE - $$EOE) not found.")
        return

    lines = data_section.group(1).strip().split('\n')

    for line in lines:
        parts = line.split()
        if len(parts) < 3:
            continue
        
        # 時刻部分 (例: 2011-Mar-01 00:00) を datetime に変換
        # Horizonsの形式は YYYY-Mon-DD HH:MM
        time_str = f"{parts[0]} {parts[1]}"
        try:
            dt = datetime.strptime(time_str, "%Y-%b-%d %H:%M")
            times_datetime.append(dt)
            # TAA (Tru_Anom) を float に変換
            taa_values.append(float(parts[2]))
        except ValueError as e:
            print(f"Skipping invalid line: {line} ({e})")

    if not times_datetime:
        print("No data extracted.")
        return
    
    # output cdf
    times = time.convert(times_datetime, frm='datetime', into='unix')
    dict_return = {
        'times': times,
        'taa': taa_values
    }
    cdf.dict_to_cdffile(dict_return, output_cdf_filepath)
    return
