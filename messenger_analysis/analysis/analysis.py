import numpy as np
import os
from spacepy import pycdf
from common import pytplot, data_process, coordinate, spec, quant, orbit, display, mathpy, path
from messenger_analysis import getdata, event_search


# ---------------------------------------------------------------------------------------------------------------------------
# main analysis
# ---------------------------------------------------------------------------------------------------------------------------

def mag_analysis(
        average_window_mfa_sec=30,
        resampling_rate = None,
        force_upsampling=False,
        resampling=False,
):
    # mso -> rmlatmlt
    # dat_orb = pytplot.get_data('pos')
    # if dat_orb is None:
    #     return None
    # orb = dat_orb.y / 2439.7
    # pytplot.store_data('pos', {'x': dat_orb.times, 'y': orb}, replace=True)
    # orbit.xyz2polar('pos', to='polar')
    # orbit.rmlatmlt2polar('pos_polar', 'pos_rmlatmlt', to='rmlatmlt')

    dat_mag = pytplot.get_data('mag')
    if dat_mag is None or len(dat_mag.y) == 0:
        return
    times = dat_mag.times
    mag = dat_mag.y

    # sampling rate
    sampling_rates = 1 / np.diff(times)
    sampling_rates = np.append(sampling_rates, sampling_rates[-1])
    pytplot.store_data('sampling_rate', {'x': times, 'y': sampling_rates})

    # resampling
    if resampling:
        if resampling_rate is None:
            display.warning(f'resampling_rate must be given')
            return
        times_resampled, mag_resampled, dict_support_resampling = mathpy.resample_data(times, mag, target_sampling_rate=resampling_rate, force_upsampling=force_upsampling, get_support_data=True)
        pytplot.store_data('mag_resampled', {'x': times_resampled, 'y': mag_resampled})
        pytplot.options('mag_resampled', legend_names=['Bx', 'By', 'Bz'], legend=1, ylabel='mag_mso')
        dict_return = {'resampling_rate': dict_support_resampling['target_sampling_rate']}
    else:
        if resampling_rate is not None:
            display.warning('resampling_rate is ignored')
        times_resampled = times
        mag_resampled = mag
        dict_return = {'resampling_rate': resampling_rate}

    # -> mfa
    dat_orb = pytplot.get_data('orb_mso')
    # window_size_mfa = average_window_mfa_sec * resampling_rate
    dict_mfa = coordinate.convert_to_mfa(times_resampled, mag_resampled, dat_orb.times, dat_orb.y, window_mfa_sec=average_window_mfa_sec)
    pytplot.store_data('mag_mfa', {'x': times_resampled, 'y': dict_mfa['mag_mfa']})

    return dict_return


def spec_analysis(
        spec_window_sec=200,
        spec_rate_overlap=.9,
        average_window_sec = 10,
        resampling_rate=None,
        force_upsampling=False,
        resample=False
):
    dict_return = {}
    yrange = [0, 1.1]
    
    # spectrogram
    var_mag_for_spectrogram = 'mag_mfa'
    dat_mag_for_spectrogram = pytplot.get_data(var_mag_for_spectrogram)
    if dat_mag_for_spectrogram is None:
        return
    if resample:
        nyquist_freq = resampling_rate/2
    else:
        nyquist_freq = None
    dict_support = spec.spectrogram_vec(var_mag_for_spectrogram, window_second=spec_window_sec, rate_overlap=spec_rate_overlap, nyquist_freq=nyquist_freq)
    dict_return.update(dict_support)
    pytplot.options(f'{var_mag_for_spectrogram}_x_dpwrspc_psd', zlog=True, zrange=[5, 5e3], ylog=True, yrange=[5e-2, 10], colormap='jet')
    pytplot.options(f'{var_mag_for_spectrogram}_y_dpwrspc_psd', zlog=True, zrange=[5, 5e3], ylog=True, yrange=[5e-2, 10], colormap='jet')
    pytplot.options(f'{var_mag_for_spectrogram}_z_dpwrspc_psd', zlog=True, zrange=[5, 5e3], ylog=True, yrange=[5e-2, 10], colormap='jet')


    # fcp
    dat_psd_abs = pytplot.get_data(f'{var_mag_for_spectrogram}_psd_abs')
    dat_mag_norm = pytplot.get_data('mag_norm')
    times = dat_mag_norm.times
    if resample:
        times_resampled, mag_norm_resampled = mathpy.resample_data(times, dat_mag_norm.y, target_sampling_rate=resampling_rate, force_upsampling=force_upsampling)
    else:
        times_resampled = times
        mag_norm_resampled = dat_mag_norm.y

    # average window
    # window_ave = int(20 * average_window_sec)
    # mag_norm_ave = mathpy.moving_average_vec(mag_norm_resampled, window_size=window_ave)
    mag_norm_ave = mathpy.moving_average_by_time(times, mag_norm_resampled, average_window_sec)

    fcp = quant.cyclotron_frequency(1, mag_norm_ave * 1e-9)
    fcp = np.interp(dat_psd_abs.times, times_resampled, fcp)
    pytplot.store_data('fcp', {'x': dat_psd_abs.times, 'y': fcp})
    # pytplot.options('fcp', color='white', linestyle='dashed')

    # normalize by fcp
    spec.normalize_by_fcp(f'{var_mag_for_spectrogram}_x_dpwrspc_psd', 'fcp')
    spec.normalize_by_fcp(f'{var_mag_for_spectrogram}_y_dpwrspc_psd', 'fcp')
    spec.normalize_by_fcp(f'{var_mag_for_spectrogram}_z_dpwrspc_psd', 'fcp')
    pytplot.options(f'{var_mag_for_spectrogram}_x_dpwrspc_psd_norm', zlog=True, zrange=[5, 5e3], yrange=yrange, colormap='jet')
    pytplot.options(f'{var_mag_for_spectrogram}_y_dpwrspc_psd_norm', zlog=True, zrange=[5, 5e3], yrange=yrange, colormap='jet')
    pytplot.options(f'{var_mag_for_spectrogram}_z_dpwrspc_psd_norm', zlog=True, zrange=[5, 5e3], yrange=yrange, colormap='jet')

    # M/Q lines
    mag_for_spectrogram = dat_mag_for_spectrogram.y
    mq1_norm = np.ones(len(mag_for_spectrogram))
    mq7_norm = 1/7 * mq1_norm
    mq16_norm = 1/16 * mq1_norm
    mq23_norm = 1/23 * mq1_norm
    pytplot.store_data('mq1_norm', {'x': dat_mag_for_spectrogram.times, 'y': mq1_norm})
    pytplot.store_data('mq7_norm', {'x': dat_mag_for_spectrogram.times, 'y': mq7_norm})
    pytplot.store_data('mq16_norm', {'x': dat_mag_for_spectrogram.times, 'y': mq16_norm})
    pytplot.store_data('mq23_norm', {'x': dat_mag_for_spectrogram.times, 'y': mq23_norm})
    pytplot.options('mq1_norm', color='black', linewidth=[2], linestyle='dashed')
    pytplot.options('mq7_norm', color='black', linewidth=[1], linestyle='dashed')
    pytplot.options('mq16_norm', color='black', linewidth=[1], linestyle='dashed')
    pytplot.options('mq23_norm', color='black', linewidth=[1], linestyle='dashed')

    return dict_return


def pol_analysis(
        resampling_rate = None,
        info=True
):
    yrange = [0, 1.1]

    dat_mag_mfa_x_dpwrspc = pytplot.get_data('mag_mfa_x_dpwrspc')
    if dat_mag_mfa_x_dpwrspc is None:
        return None
    spec.polarization_from_spectrogram(
        'mag_mfa_x_dpwrspc',
        'mag_mfa_y_dpwrspc',
        'mag_mfa_z_dpwrspc',
        quiet=not info
    )
    pytplot.options('polarization', zrange=[-1, 1], ylog=True, yrange=[5e-2, 10], colormap='jet')
    pytplot.options('wna', zrange=[0, 90], ylog=True, yrange=[5e-2, 10], colormap='jet')
    pytplot.options('planarity', zrange=[0, 1], ylog=True, yrange=[5e-2, 10], colormap='jet')

    # normalize by fcp
    spec.normalize_by_fcp('polarization', 'fcp')
    spec.normalize_by_fcp('wna', 'fcp')
    spec.normalize_by_fcp('planarity', 'fcp')
    pytplot.options('polarization_norm', zrange=[-1, 1], yrange=yrange, colormap='jet')
    pytplot.options('wna_norm', zrange=[0, 90], yrange=yrange, colormap='jet')
    pytplot.options('planarity_norm', zrange=[0, 1], yrange=yrange, colormap='jet')

    return


def output_to_cdf(
        savepath
):
    path.make_directory(savepath)
    if os.path.exists(savepath):
        os.remove(savepath)
    with pycdf.CDF(savepath, '') as cdf:
        dat_psd_abs_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
        cdf['times'] = dat_psd_abs_norm_x.times
        cdf['freqs_norm'] = dat_psd_abs_norm_x.v
        cdf['psd_norm_x'] = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm').y
        cdf['psd_norm_y'] = pytplot.get_data('mag_mfa_y_dpwrspc_psd_norm').y
        cdf['psd_norm_z'] = pytplot.get_data('mag_mfa_z_dpwrspc_psd_norm').y
        cdf['polarization_norm'] = pytplot.get_data('polarization_norm').y
    
    display.current_time_comment(comment=f'saved cdf: {savepath}')
    return


def analysis(
        trange,
        info=True,
        outcdf=False,
        savecdf='test.cdf',
        basedir_cdf_files=None,
        basedir_orb='',
        resampling_rate=None,
        spec_window_sec=200,
        mask=True,
        threshold_psd_abs_mask=10,
        spec_window_size=None,
):
    params = {
        'resampling_rate': resampling_rate,
        'average_window_mfa_sec': 30,
        'spec_window_sec': spec_window_sec,
        'spec_rate_overlap': .9,
        'average_window_sec': 10,
        'yrange_norm': [0, 1.1],
    }

    if info:
        display.current_time_comment(comment=f'analysis: {trange=}')
    # get data
    if info:
        display.current_time_comment(comment='get data')
    getdata.messenger_mag(trange, basedir_cdf_files=basedir_cdf_files)
    getdata.messenger_orb(trange, basedir_orb=basedir_orb)

    # mag
    if info:
        display.current_time_comment(comment='mag analysis')
    dict_ret_mag = mag_analysis(
        resampling=False,
        resampling_rate=params['resampling_rate'],
        average_window_mfa_sec=params['average_window_mfa_sec']
    )
    resampling_rate = dict_ret_mag['resampling_rate']

    # spec
    if info:
        display.current_time_comment(comment='spec analysis')
    dict_ret_spec = spec_analysis(
        resample=False,
        resampling_rate=resampling_rate,
        spec_window_sec=params['spec_window_sec'],
        spec_rate_overlap=params['spec_rate_overlap'],
        average_window_sec=params['average_window_sec']
    )
    params.update(dict_ret_spec)

    dat_psd_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd')
    # dat_psd_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
    times = dat_psd_x.times
    freqs = dat_psd_x.v
    # freqs_norm = dat_psd_norm_x.v
    dt = np.mean(np.diff(times))
    df = np.mean(np.diff(freqs))
    # df_norm = np.mean(np.diff(freqs_norm))
    params['dt'] = dt
    params['df'] = df
    # params['df_norm'] = df_norm

    # polarization
    if info:
        display.current_time_comment(comment='polari analysis')
    pol_analysis(
        resampling_rate=resampling_rate
    )

    # pytplot settings
    pytplot.options('mag_mfa_x_dpwrspc_psd_norm', yrange=params['yrange_norm'])
    pytplot.options('mag_mfa_y_dpwrspc_psd_norm', yrange=params['yrange_norm'])
    pytplot.options('mag_mfa_z_dpwrspc_psd_norm', yrange=params['yrange_norm'])
    pytplot.options('polarization_norm', yrange=params['yrange_norm'])
    pytplot.options('wna_norm', yrange=params['yrange_norm'])
    pytplot.options('planarity_norm', yrange=params['yrange_norm'])

    # mask
    if mask:
        dat_psd_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
        times = dat_psd_norm_x.times
        freqs_norm = dat_psd_norm_x.v
        psd_norm_x = dat_psd_norm_x.y
        psd_norm_y = pytplot.get_data('mag_mfa_y_dpwrspc_psd_norm').y
        psd_norm_z = pytplot.get_data('mag_mfa_z_dpwrspc_psd_norm').y
        psd_norm_abs = np.sqrt(psd_norm_x ** 2 + psd_norm_y ** 2 + psd_norm_z ** 2)
        pytplot.store_data('psd_norm_abs', {'x': times, 'y': psd_norm_abs, 'v': freqs_norm})
        polarization_norm = pytplot.get_data('polarization_norm').y
        wna_norm = pytplot.get_data('wna_norm').y
        planarity_norm = pytplot.get_data('planarity_norm').y

        mask_indices = psd_norm_abs > threshold_psd_abs_mask
        psd_norm_x_mask = np.where(mask_indices, psd_norm_x, np.nan)
        psd_norm_y_mask = np.where(mask_indices, psd_norm_y, np.nan)
        psd_norm_z_mask = np.where(mask_indices, psd_norm_z, np.nan)
        polarization_norm_mask = np.where(mask_indices, polarization_norm, np.nan)
        wna_norm_mask = np.where(mask_indices, wna_norm, np.nan)
        planarity_norm_mask = np.where(mask_indices, planarity_norm, np.nan)
        
        # store
        pytplot.store_data('psd_norm_x_mask', {'x': times, 'y': psd_norm_x_mask, 'v': freqs_norm})
        pytplot.store_data('psd_norm_y_mask', {'x': times, 'y': psd_norm_y_mask, 'v': freqs_norm})
        pytplot.store_data('psd_norm_z_mask', {'x': times, 'y': psd_norm_z_mask, 'v': freqs_norm})
        pytplot.store_data('polarization_norm_mask', {'x': times, 'y': polarization_norm_mask, 'v': freqs_norm})
        pytplot.store_data('wna_norm_mask', {'x': times, 'y': wna_norm_mask, 'v': freqs_norm})
        pytplot.store_data('planarity_norm_mask', {'x': times, 'y': planarity_norm_mask, 'v': freqs_norm})
        pytplot.options('psd_norm_abs', zlog=True, zrange=[5, 5e3], yrange=params['yrange_norm'], colormap='jet', zlabel='psd_abs')
        pytplot.options('psd_norm_x_mask', zlog=True, zrange=[5, 5e3], yrange=params['yrange_norm'], colormap='jet', zlabel='psd_perp1')
        pytplot.options('psd_norm_y_mask', zlog=True, zrange=[5, 5e3], yrange=params['yrange_norm'], colormap='jet', zlabel='psd_perp2')
        pytplot.options('psd_norm_z_mask', zlog=True, zrange=[5, 5e3], yrange=params['yrange_norm'], colormap='jet', zlabel='psd_para')
        pytplot.options('polarization_norm_mask', zrange=[-1, 1], yrange=params['yrange_norm'], colormap='jet', zlabel='polarization\nellipticity')
        pytplot.options('wna_norm_mask', zrange=[0, 90], yrange=params['yrange_norm'], colormap='jet', zlabel='wna')
        pytplot.options('planarity_norm_mask', zrange=[0, 1], yrange=params['yrange_norm'], colormap='jet', zlabel='planarity')
        

    # output to cdf file
    if outcdf:
        output_to_cdf(savecdf)

    return params



