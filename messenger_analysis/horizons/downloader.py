import os
from datetime import datetime
from astroquery.jplhorizons import Horizons
from common import display, path


def download_horizons_data(
        target_id, 
        location, 
        start_time, 
        stop_time, 
        time_step,
        savecsv='horizons_data/horizons_data.csv',
    ):
    """
    JPL Horizonsからデータを取得する。
    エラーが発生した場合（名前の重複など）、詳細なメッセージを表示する。
    """
    print("\n" + "="*40)
    print("--- JPL Horizons Data Downloader ---")
    print("="*40)

    try:
        print(f"Target  : {target_id}")
        print(f"Location: {location}")
        print(f"Period  : {start_time} to {stop_time}")
        print(f"Step    : {time_step}")
        print("-" * 40)

        # 2. Horizonsオブジェクトの作成
        # 名前でエラーが出る場合は ID (水星なら '199') を直接指定するのがベスト
        obj = Horizons(
            id=target_id,
            location=location,
            epochs={'start': start_time, 'stop': stop_time, 'step': time_step}
        )

        # 3. エフェメリスデータの取得
        # 注意: 名前が重複しているとここで例外が発生する
        eph = obj.ephemerides()

        # 4. Pandas DataFrameに変換
        df = eph.to_pandas()

        # 5. ファイル保存
        path.make_directory(savecsv)
        df.to_csv(savecsv, index=False)

        print(f"\n[SUCCESS] データを取得・保存しました。")
        display.info(f'Saved: {savecsv}')
        print("\n--- Data Preview (First 5 rows) ---")
        print(df)

    except Exception as e:
        print(f"\n[ERROR] データの取得に失敗しました。")
        print(f"理由: {e}")
        print("-" * 40)
        if "Ambiguous target name" in str(e):
            print("【解決策】")
            print("ターゲット名が重複しています。名前に代わって以下のIDを指定してください。")
            print("  - 水星(本体)を指定する場合: '199'")
            print("  - 水星系重心を指定する場合: '1'")
            print("  - 金星なら '299', 火星なら '499', 木星なら '599'")
        elif "Location" in str(e) or "location" in str(e):
            print("【解決策】")
            print("観測場所の指定を確認してください。太陽中心なら '@sun'、地球中心なら '500@体番号' などが必要です。")
    return savecsv
