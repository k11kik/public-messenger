import pandas as pd
import os
from datetime import datetime
from common import display, util, path, pytplot, gmail
from messenger_analysis import getdata, event_search
from .analysis import mag_analysis, spec_analysis, pol_analysis


def _search_emic_events_trange(
        trange,
        threshold_psd=1e3,
        threshold_ratio=1,
        threshold_polari=-.5,
        min_event_delta_time=60,
        min_event_delta_freq=.1,
        merge_timespan=300, # timespan to merge events [s]
):
    resampling_rate = 20
    average_window_mfa_sec=30
    spec_window_size=1024
    spec_rate_overlap=.9
    average_window_sec = 10

    display.current_time_comment(comment=f'analysis: {trange=}')
    # get data
    # display.current_time_comment(comment='get data')
    getdata.messenger_mag(trange)
    getdata.messenger_orb(trange)

    # mag
    # display.current_time_comment(comment='mag analysis')
    mag_analysis(
        resampling_rate=resampling_rate,
        average_window_mfa_sec=average_window_mfa_sec
    )
    # if result_mag_ana is None:
    #     return pd.DataFrame({})

    # spec
    # display.current_time_comment(comment='spec analysis')
    spec_analysis(
        resampling_rate=resampling_rate,
        spec_window_size=spec_window_size,
        spec_rate_overlap=spec_rate_overlap,
        average_window_sec=average_window_sec
    )

    # polarization
    # display.current_time_comment(comment='polari analysis')
    pol_analysis(
        resampling_rate=resampling_rate
    )

    # event search
    event_df = event_search.search_emic(
        'mag_mfa_x_dpwrspc_psd_norm',
        'mag_mfa_y_dpwrspc_psd_norm',
        'mag_mfa_z_dpwrspc_psd_norm',
        'polarization_norm',
        threshold_psd=threshold_psd,
        threshold_ratio=threshold_ratio,
        threshold_polari=threshold_polari,
        min_event_delta_time=min_event_delta_time,
        min_event_delta_freq=min_event_delta_freq,
        merge_timespan=merge_timespan
    )

    return event_df



def _save_monthly_events(df_list, year_month, output_dir):
    """
    リスト内のDataFrameを結合し、月別ファイルとしてCSVに出力する補助関数。
    """
    if not df_list:
        return
        
    year = year_month[:4]
    # month = year_month[4:] # year_monthは'YYYYMM'形式を想定

    # リスト内のすべてのDataFrameを結合
    final_df = pd.concat(df_list, ignore_index=True)
    
    # ファイルパスの作成 (例: ./emic_event/2015/emic_event_201501.csv)
    # path.savecsvが年ディレクトリの作成を担うと仮定
    filepath = os.path.join(output_dir, 'emic_event', year, f'emic_event_{year_month}.csv')
    
    path.savecsv(final_df, filepath, index=False)
    return filepath


def search_emic_events(
        trange,
        threshold_psd=1e3,
        threshold_ratio=1,
        threshold_polari=-.5,
        min_event_delta_time=60,
        min_event_delta_freq=.1,
        merge_timespan=300, # timespan to merge events [s]
        output_dir='',
        send_gmail=False
):
    """
    savepath: {output_dir}/emic_event/...
    """
    time_list = util.make_time_list(trange, 2, 'hours')

    # 月ごとに DataFrame を格納する辞書
    current_month_df_list = []
    

    loop_start_time = datetime.now()
    current_year_month = ''
    for i, trange_i in enumerate(time_list):
        try:
            dict_prog = display.progress_bar(i, len(time_list), loop_start_time)
            pytplot.del_data()
            event_df_i = _search_emic_events_trange(
                trange_i,
                threshold_psd=threshold_psd,
                threshold_ratio=threshold_ratio,
                threshold_polari=threshold_polari,
                min_event_delta_time=min_event_delta_time,
                min_event_delta_freq=min_event_delta_freq,
                merge_timespan=merge_timespan
            )
            
            # イベントが検出された場合のみ処理
            if not event_df_i.empty:
                print(event_df_i)
                # 'start'カラムから年と月を抽出
                # 'start'は文字列 ('YYYY-MM-DD/hh:mm:ss') のため、年と月を抽出

                # 最初のイベントの開始時間から年月を取得
                start_time_str = event_df_i['start'].iloc[0]
                # ここでは time.convert の出力形式 ('YYYY-MM-DD/hh:mm:ss') を仮定して処理
                year_month = start_time_str.split('/')[0][:7].replace('-', '') # 例: '201501'

                if current_year_month != '' and current_year_month != year_month:
                    # 月が切り替わったため、前の月のデータをまとめてCSV出力する
                    saved_csv = _save_monthly_events(current_month_df_list, current_year_month, output_dir)

                    # send message
                    if send_gmail:
                        subject = f'[Messenger Analysis] searching emic events: {year_month}'
                        gmail.send_progress_message(subject, 'search_emic_events.py/search_emic_events', dict_prog, comment=f'{trange_i=}\nSaved csv: {saved_csv}')

                    # 次の月の処理のためにリストをクリア
                    current_month_df_list = []
                    
                # 現在の月のデータをリストに追加
                current_month_df_list.append(event_df_i)
                current_year_month = year_month # 月情報を更新

        except Exception as e:
            display.error('search_emic_events/search_emic_events', f"Error parsing time string: {e}")
            continue



    if current_month_df_list:
        _save_monthly_events(current_month_df_list, current_year_month, output_dir)
    
    # send message
    if send_gmail:
        subject = f'[Messenger Analysis] searching emic events: Finished'
        body = 'search_emic_events.py/search_emic_events\n' + 'Successfully fineshed'
        gmail.send_message(subject, body)
    return
