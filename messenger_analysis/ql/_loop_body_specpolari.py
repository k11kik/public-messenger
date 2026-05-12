# 必要なインポートをここに移動
import os
from datetime import datetime
import matplotlib.pyplot as plt
from common import util, pytplot, display, time
from messenger_analysis import analysis, getdata

def _run_specpolari(
    trange_i,
    output_dir,
    resampling_rate,
    average_window_mfa_sec,
    spec_window_size,
    spec_rate_overlap,
    average_window_sec,
):
    """
    specpolariのループ内部処理を実行する関数。
    並列処理のプロセス単位で実行されます。
    """
    
    # pytplot.del_data は、各プロセス内で独立したデータ空間に対して実行される
    pytplot.del_data(silent=True)
    
    # 進行状況の表示 (ここでは簡易版)
    print(f'Processing: {trange_i=}')

    try:
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
            resampling_rate=resampling_rate,
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
        save_dir = os.path.join(output_dir, f'{dt_start.year:04}', f'{dt_start.month:02}')
        save_png = os.path.join(save_dir, f'messenger_mag_mso_specpolari_{str_start}.png')
        
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
        return True # 成功を返す
        
    except Exception as e:
        print(f'Error processing {trange_i}: {e}')
        try:
                plt.close('all')
        except:
            pass
        return False # 失敗を返す