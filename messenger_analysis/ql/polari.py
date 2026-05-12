import os
from datetime import datetime
import matplotlib.pyplot as plt
from common import util, pytplot, display, time, gmail
from messenger_analysis import analysis, getdata


def polarization(
        trange,
        basedir_mag_mso,
        basedir_orb,
        basedir_savefig,
):
    time_list = time.make_time_list(trange, 2, 'hours')

    params = {
        'average_window_mfa_sec': 30,
        'spec_window_sec': 200,
        'spec_rate_overlap': .9,
        'average_window_sec': 10,
        'yrange_norm': [0, 1.1],
        'window': {'n_ffts': []}
    }

    loop_start_time = datetime.now()

    current_year = 0
    for i, trange_i in enumerate(time_list):
        pytplot.del_data(silent=True)
        print(f'Processing: {trange_i=}')
        
        try:
            display.progress_bar(i, len(time_list), loop_start_time)

            dt_start = time.convert(trange_i[0], frm='str', into='datetime')
            year = dt_start.year
            if current_year != year:
                current_year = year

            # get data
            getdata.messenger_mag(trange_i, basedir_cdf_files=basedir_mag_mso)
            getdata.messenger_orb(trange_i, basedir_orb=basedir_orb)

            # mag
            analysis.mag_analysis(
                average_window_mfa_sec=params['average_window_mfa_sec']
            )

            # spec
            dict_ret_spec = analysis.spec_analysis(
                spec_window_sec=params['spec_window_sec'],
                spec_rate_overlap=params['spec_rate_overlap'],
                average_window_sec=params['average_window_sec']
            )
            params.update(dict_ret_spec)

            # polarization
            analysis.pol_analysis()

            pytplot.copy_data('fcp', 'fcp_overplot')

            # print params
            display.print_dict(params)

            # plot options
            pytplot.options('sampling_rate', ylabel='sampling rate\n[Hz]')
            pytplot.options('mag', ylabel='Mag (MSO)\n[nT]', legend=True, legend_names=['Bx', 'By', 'Bz'])
            pytplot.options('mag_mfa', ylabel='Mag (MFA)\n[nT]')
            pytplot.options('mag_norm', ylabel='Mag norm\n[nT]')
            pytplot.options('fcp', ylabel='fcp [Hz]')
            pytplot.options('mag_mfa_x_dpwrspc_psd', zlabel='psd_perp1\n[$nT^2/Hz$]', ylabel='freq [Hz]')
            pytplot.options('mag_mfa_y_dpwrspc_psd', zlabel='psd_perp1\n[$nT^2/Hz$]', ylabel='freq [Hz]')
            pytplot.options('mag_mfa_z_dpwrspc_psd', zlabel='psd_perp1\n[$nT^2/Hz$]', ylabel='freq [Hz]')
            pytplot.options('mag_mfa_x_dpwrspc_psd_norm', zlabel='psd_perp1\n[$nT^2/Hz$]', ylabel='f/fcp')
            pytplot.options('mag_mfa_y_dpwrspc_psd_norm', zlabel='psd_perp2\n[$nT^2/Hz$]', ylabel='f/fcp')
            pytplot.options('mag_mfa_z_dpwrspc_psd_norm', zlabel='psd_para\n[$nT^2/Hz$]', ylabel='f/fcp')
            pytplot.options('polarization_norm', zlabel='polarization\nellipticity', ylabel='f/fcp')
            pytplot.options('wna_norm', zlabel='wna', ylabel='f/fcp')
            pytplot.options('planarity_norm', zlabel='planarity', ylabel='f/fcp')
            pytplot.options('fcp_overplot', color='white', linewidth=2, linestyle='dashed', ylabel='freq [Hz]')
            pytplot.options('mq1_norm', ylabel='f/fcp')

            # plot
            dt_start = time.convert(trange_i[0], 'str', 'datetime')
            str_start = f'{dt_start.year:04}{dt_start.month:02}{dt_start.day:02}{dt_start.hour:02}{dt_start.minute:02}'
            save_png = f'{basedir_savefig}/{dt_start.year:04}/{dt_start.month:02}/messenger_mag_mso_polarization_{str_start}.png'
            suptitle = f'{trange_i=}\n' + f'window MFA: {params['average_window_mfa_sec']} s, FFT window: {params['spec_window_sec']} s, Overlapping rate: {params['spec_rate_overlap']}, moving_sec for fcp: {params['average_window_sec']} s\n' + f'n_fft: {params['window']['n_ffts']}'
            pytplot.tplot(
                [
                    'sampling_rate',
                    'mag',
                    'mag_mfa',
                    'mag_norm',
                    'fcp',
                    ['mag_mfa_x_dpwrspc_psd', 'fcp_overplot'],
                    ['mag_mfa_y_dpwrspc_psd', 'fcp_overplot'],
                    ['mag_mfa_z_dpwrspc_psd', 'fcp_overplot'],
                    ['mag_mfa_x_dpwrspc_psd_norm', 'mq1_norm'],
                    ['mag_mfa_y_dpwrspc_psd_norm', 'mq1_norm'],
                    ['mag_mfa_z_dpwrspc_psd_norm', 'mq1_norm'],
                    ['polarization_norm', 'mq1_norm'],
                    ['wna_norm', 'mq1_norm'],
                    ['planarity_norm', 'mq1_norm']
                ],
                figsize=(12, 18),
                xlim=trange_i,
                delta_xticks=30,
                timeunit_xticks='minutes',
                save_png=save_png,
                var_orbit='orb_rmlatmlt',
                list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]'],
                suptitle=suptitle,
                height_ratios=[1, 8, 1]
            )

        except Exception as e:
            display.error(f'Eroor: {e}')
            continue
    return


def polari(
        trange,
        basedir_savefig='',
):
    # Win
    basedir_cdf_files = r"E:\messenger\messenger_data\mag_mso"
    basedir_orb = r"E:\messenger\messenger_data\orb"
    # Mac
    # basedir_cdf_files = '/Volumes/SSD4T/messenger/messenger_data/mag_mso'
    # basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/orb'
    # -------------
    display.current_time_comment(comment=f'QL: Polari: {trange}')
    output_dir = basedir_savefig
    time_list = time.make_time_list(trange, 2, 'hours')

    resampling_rate = 20
    average_window_mfa_sec = 30
    spec_window_size = 4096
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
                # gmail.send_progress_message(subject, 'specpolari.py', dict_prog, comment=f'{trange=}, {trange_i=}')

            # get data
            getdata.messenger_mag(trange_i, basedir_cdf_files=basedir_cdf_files)
            getdata.messenger_orb(trange_i, basedir_orb=basedir_orb)

            # mag
            analysis.mag_analysis(
                resampling=False,
                average_window_mfa_sec=average_window_mfa_sec
            )

            # spec
            analysis.spec_analysis(
                resampling_rate=resampling_rate,
                spec_window_size=spec_window_size,
                spec_rate_overlap=spec_rate_overlap,
                average_window_sec=average_window_sec,
                resample=False
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
            pytplot.options('mag', ylabel='MAG (MSO)\n[nT]', legend=True, legend_names=['Bx', 'By', 'Bz'])
            pytplot.options('mag_mfa', ylabel='MAG (MFA)\n[nT]', legend=True, legend_names=['Bx', 'By', 'Bz'])

            # plot
            dt_start = time.convert(trange_i[0], 'str', 'datetime')
            str_start = f'{dt_start.year:04}{dt_start.month:02}{dt_start.day:02}{dt_start.hour:02}{dt_start.minute:02}'
            save_png = f'{output_dir}/{dt_start.year:04}/{dt_start.month:02}/messenger_mag_mso_polarization_{str_start}.png'
            suptitle = f'{trange_i=}\n' + f'{average_window_mfa_sec=} s, {spec_window_size=}, {spec_rate_overlap=}, fcp_moving_sec={average_window_sec} s'
            pytplot.tplot(
                [
                    'mag',
                    'mag_mfa',
                    'mag_mfa_x_dpwrspc_psd_norm',
                    'mag_mfa_y_dpwrspc_psd_norm',
                    'mag_mfa_z_dpwrspc_psd_norm',
                    'polarization_norm',
                    'wna_norm',
                    'planarity_norm',
                ],
                figsize=(12, 16),
                xlim=trange_i,
                delta_xticks=30,
                timeunit_xticks='minutes',
                save_png=save_png,
                var_orbit='orb_rmlatmlt',
                list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]'],
                suptitle=suptitle
            )

            plt.close('all')

        except Exception as e:
            display.error(f'Eroor: {e}')
            try:
                plt.close('all')
            except:
                pass
            continue
        
    return