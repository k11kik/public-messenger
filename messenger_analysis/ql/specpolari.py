import os
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed # 並列処理に必要
import matplotlib.pyplot as plt

from common import util, pytplot, display, time, gmail
from messenger_analysis import analysis, getdata
from ._loop_body_specpolari import _run_specpolari


def specpolari_serial(
        trange,
        parent_dir_save_png: str = '',
):
    display.current_time_comment(comment=f'QL: specpolari: {trange}')
    output_dir = os.path.join(parent_dir_save_png, 'ql/mag/2h/specpolari_norm')
    time_list = util.make_time_list(trange, 2, 'hours')

    resampling_rate = 20
    average_window_mfa_sec = 30
    spec_window_size = 1024
    spec_rate_overlap = .9
    average_window_sec = 10

    loop_start_time = datetime.now()

    current_year = 0
    for i, trange_i in enumerate(time_list):
        pytplot.del_data(silent=True)
        print(f'Processing: {trange_i=}')
        
        try:
            dict_prog = display.progress_bar(i, len(time_list), loop_start_time)

            dt_start = time.convert(trange_i[0], frm='str', into='datetime')
            year = dt_start.year
            if current_year != year:
                current_year = year
                # gmail
                subject = f'[Messenger Analysis] specpolari: Processing {year}'
                gmail.send_progress_message(subject, 'specpolari.py', dict_prog, comment=f'{trange=}, {trange_i=}')

            # get data
            getdata.messenger_mag(trange_i)
            getdata.messenger_orb(trange_i)

            # mag
            analysis.mag_analysis(
                resampling_rate=resampling_rate,
                average_window_mfa_sec=average_window_mfa_sec
            )

            # spec
            analysis.spec_analysis(
                resampling_rate=resampling_rate,
                spec_window_size=spec_window_size,
                spec_rate_overlap=spec_rate_overlap,
                average_window_sec=average_window_sec
            )

            # polarization
            analysis.pol_analysis(
                resampling_rate=resampling_rate
            )


            # plot options
            pytplot.options('mag_mfa_x_dpwrspc_psd_norm', zlabel='psd_perp1', ylabel='f/fcp')
            pytplot.options('mag_mfa_y_dpwrspc_psd_norm', zlabel='psd_perp2', ylabel='f/fcp')
            pytplot.options('mag_mfa_z_dpwrspc_psd_norm', zlabel='psd_para', ylabel='f/fcp')
            pytplot.options('polarization_norm', zlabel='polarization', ylabel='f/fcp')
            pytplot.options('wna_norm', zlabel='wna', ylabel='f/fcp')
            pytplot.options('planarity_norm', zlabel='planarity', ylabel='f/fcp')

            # plot
            dt_start = time.convert(trange_i[0], 'str', 'datetime')
            str_start = f'{dt_start.year:04}{dt_start.month:02}{dt_start.day:02}{dt_start.hour:02}{dt_start.minute:02}'
            save_png = f'{output_dir}/{dt_start.year:04}/{dt_start.month:02}/messenger_mag_mso_specpolari_{str_start}.png'
            suptitle = f'{trange_i=}\n' + f'{resampling_rate=} Hz, {average_window_mfa_sec=} s\n' + f'{spec_window_size=}, {spec_rate_overlap=}, fcp_moving_sec={average_window_sec} s'
            pytplot.tplot(
                [
                    'mag_mfa_x_dpwrspc_psd_norm',
                    'mag_mfa_y_dpwrspc_psd_norm',
                    'mag_mfa_z_dpwrspc_psd_norm',
                    'polarization_norm',
                    'wna_norm',
                    'planarity_norm',
                ],
                figsize=(12, 8),
                xlim=trange_i,
                delta_xticks=30,
                timeunit_xticks='minutes',
                save_png=save_png,
                var_orbit='pos_rmlatmlt',
                list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]'],
                suptitle=suptitle
            )

            plt.close('all')

        except Exception as e:
            print(f'Eroor: {e}')
            try:
                plt.close('all')
            except:
                pass
            continue
        
    return

def specpolari_parallel(
        trange,
        parent_dir_save_png: str = '',
        max_workers: int = 4 # 新しい引数: 並列実行する最大プロセス数
):
    display.current_time_comment(comment=f'QL: specpolari: {trange}')
    output_dir = os.path.join(parent_dir_save_png, 'ql/mag/2h/specpolari_norm')
    time_list = util.make_time_list(trange, 2, 'hours')

    # 定数を定義
    resampling_rate = 20
    average_window_mfa_sec = 30
    spec_window_size = 1024
    spec_rate_overlap = .9
    average_window_sec = 10

    loop_start_time = datetime.now()
    total_len = len(time_list)
    
    # --- 並列実行 ---
    # ProcessPoolExecutorを使用して、CPUコア数に応じたプロセスで並列実行する
    # max_workers は環境のCPUコア数を目安に設定する（例: 4や8など）
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, trange_i in enumerate(time_list):
            
            # 各イテレーションを新しいプロセスで実行するためにキューに入れる
            future = executor.submit(
                _run_specpolari,
                trange_i,
                output_dir,
                resampling_rate,
                average_window_mfa_sec,
                spec_window_size,
                spec_rate_overlap,
                average_window_sec,
            )
            futures.append(future)

        current_year = 0

        # 結果を待機し、進行状況を表示
        for i, future in enumerate(as_completed(futures)):
            trange_i = time_list[i]
            dt_start = time.convert(trange_i[0], frm='str', into='datetime')
            year = dt_start.year
            # 進行状況表示
            dict_prog = display.progress_bar(i, total_len, loop_start_time)

            if current_year != year:
                current_year = year
                # gmail
                subject = f'[Messenger Analysis] specpolari: Processing {year}'
                gmail.send_progress_message(subject, 'specpolari.py', dict_prog)
            
            # 結果を取得 (ここでは True/False)
            success = future.result()
            if not success:
                print(f"One time interval failed to process.")

    return


def specpolari(
        trange,
        parent_dir_save_png: str = '',
        use_parallel=False
):
    if use_parallel:
        specpolari_parallel(
            trange,
            parent_dir_save_png=parent_dir_save_png,
            max_workers=4
        )
    else:
        specpolari_serial(
            trange,
            parent_dir_save_png=parent_dir_save_png
        )
    
