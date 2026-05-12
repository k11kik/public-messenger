import os
from datetime import datetime
from common import util, pytplot, display, time
from messenger_analysis import analysis, getdata

def spectrogram(
        trange,
        parent_dir_save_png: str = '',
):
    output_dir = os.path.join(parent_dir_save_png, 'ql/mag/2h/spectrogram_norm')
    time_list = util.make_time_list(trange, 2, 'hours')

    resampling_rate = 20
    spec_window_size = 1024
    spec_rate_overlap = .9
    average_window_sec = 10

    loop_start_time = datetime.now()
    for i, trange_i in enumerate(time_list):
        pytplot.del_data(silent=True)
        print(f'Processing: {trange_i=}')
        
        try:
            display.progress_bar(i, len(time_list), loop_start_time)

            # get data
            getdata.messenger_mag(trange_i)
            getdata.messenger_orb(trange_i)

            # mag
            analysis.mag_analysis(
                resampling_rate=resampling_rate
            )

            # spec
            analysis.spec_analysis(
                resampling_rate=resampling_rate,
                spec_windwo_size=spec_window_size,
                spec_rate_overlap=spec_rate_overlap,
                average_window_sec=average_window_sec
            )

            # plot options
            pytplot.options('mag_mfa_x_dpwrspc_psd_norm', zlabel='psd_x')
            pytplot.options('mag_mfa_y_dpwrspc_psd_norm', zlabel='psd_y')
            pytplot.options('mag_mfa_z_dpwrspc_psd_norm', zlabel='psd_z')

            # plot
            dt_start = time.convert(trange_i[0], 'str', 'datetime')
            str_start = f'{dt_start.year:04}{dt_start.month:02}{dt_start.day:02}{dt_start.hour:02}{dt_start.minute:02}'
            save_png = f'{output_dir}/{dt_start.year:04}/{dt_start.month:02}/messenger_mag_mso_spectrogram_{str_start}.png'
            suptitile = f'{trange_i=}\n{resampling_rate=} Hz, {spec_window_size=}, {spec_rate_overlap=}, fcp_moving_sec={average_window_sec} s'
            pytplot.tplot(
                [
                    'mag_mfa_x_dpwrspc_psd_norm',
                    'mag_mfa_y_dpwrspc_psd_norm',
                    'mag_mfa_z_dpwrspc_psd_norm',
                ],
                xlim=trange_i,
                delta_xticks=30,
                timeunit_xticks='minutes',
                save_png=save_png,
                var_orbit='pos_rmlatmlt',
                list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]'],
                suptitle=suptitile
            )
        except Exception as e:
            print(f'Eroor: {e}')
            continue
        
    return
