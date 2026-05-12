import numpy as np
import os
from spacepy import pycdf
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from common import pytplot, display, path, util, time
from common.cdf.cdfdata import dict_to_cdf, dict_to_cdffile, cdffile_to_dict
from messenger_analysis import getdata
from messenger_analysis.analysis import mag_analysis, spec_analysis

def get_intensity_dist(
        varname_rmlatmlt,
        varname_spectrogram,
        info=True,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
):
    dat_rmlatmlt = pytplot.get_data(varname_rmlatmlt)
    dat_spec = pytplot.get_data(varname_spectrogram)
    if dat_rmlatmlt is None:
        raise ValueError('dat_rmlatmlt is None')
    if dat_spec is None:
        raise ValueError('dat_spec is None')
    
    times_rmlatmlt = dat_rmlatmlt.times
    rmlatmlt = dat_rmlatmlt.y
    times = dat_spec.times
    spectrogram = dat_spec.y

    if spectrogram.ndim != 2:
        raise ValueError('spectrogram must be 2D')
    
    # mean PSD in freq direction
    means_spectrogram = np.nanmean(spectrogram, axis=1)

    # グリッド設定
    if r_bins is None:
        r_bins = np.arange(1, 7.5 + 0.1, 0.5)  # 1～7まで0.5刻み
    if mlt_bins is None:
        mlt_bins = np.arange(0, 24 + 1, 1)  # 0～24まで1刻み
    if mlat_bins is None:
        mlat_bins = np.arange(-90, 90 + 5, 5)  # -90～90まで5刻み

    # カウント用配列
    rmlt_sum = np.zeros((len(r_bins) - 1, len(mlt_bins) - 1))  # (r, mlt)の2D
    rmlat_sum = np.zeros((len(r_bins) - 1, len(mlat_bins) - 1))  # (r, mlat)の2D

    rmlt_count = np.zeros((len(r_bins) - 1, len(mlt_bins) - 1), dtype=int)
    rmlat_count = np.zeros((len(r_bins) - 1, len(mlat_bins) - 1), dtype=int)

    for i, times_i in enumerate(times):
        mean_spectrogram = means_spectrogram[i]

        if np.isnan(mean_spectrogram):
            display.info('mean_spectrogram is nan')
            continue

        # get the nearest rmlatmlt
        idx_nearest = np.argmin(np.abs(times_rmlatmlt - times_i))
        r, mlat, mlt = rmlatmlt[idx_nearest]

        if mlt > 24:
            mlt = mlt % 24

        # それぞれbinに落とし込む
        r_idx = np.digitize(r, r_bins) - 1
        mlt_idx = np.digitize(mlt, mlt_bins) - 1
        mlat_idx = np.digitize(mlat, mlat_bins) - 1

        if (0 <= r_idx < len(r_bins) - 1) and (0 <= mlt_idx < len(mlt_bins) - 1):
            rmlt_sum[r_idx, mlt_idx] += mean_spectrogram
            rmlt_count[r_idx, mlt_idx] += 1
        if (0 <= r_idx < len(r_bins) - 1) and (0 <= mlat_idx < len(mlat_bins) - 1):
            rmlat_sum[r_idx, mlat_idx] += mean_spectrogram
            rmlat_count[r_idx, mlat_idx] += 1
    
    # sum / count
    rmlt_intensity_avg = np.zeros_like(rmlt_sum)
    non_zero_rmlt = rmlt_count > 0  # カウントが0より大きい場所
    rmlt_intensity_avg[non_zero_rmlt] = rmlt_sum[non_zero_rmlt] / rmlt_count[non_zero_rmlt]

    rmlat_intensity_avg = np.zeros_like(rmlat_sum)
    non_zero_rmlat = rmlat_count > 0  # カウントが0より大きい場所
    rmlat_intensity_avg[non_zero_rmlat] = rmlat_sum[non_zero_rmlat] / rmlat_count[non_zero_rmlat]
    
    return {
        'rmlt_intensity_avg': rmlt_intensity_avg,
        'rmlat_intensity_avg': rmlat_intensity_avg,
        'rmlt_count': rmlt_count,
        'rmlat_count': rmlat_count,
    }


def get_intensity_dist_trange(
        trange,
        parent_dir_messenger_data='',
        resampling_rate=20,
        average_window_mfa_sec=30,
        spec_window_size=1024,
        spec_rate_overlap=.9,
        average_window_sec=10,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
):
    if r_bins is None:
        r_bins = np.arange(1, 7+.5, .5)
    if mlt_bins is None:
        mlt_bins = np.arange(0, 24+1, 1)
    if mlat_bins is None:
        mlat_bins = np.arange(-90, 90+5, 5)
    
    # meshgrid
    # (r, mlt)
    theta_mlt = (mlt_bins / 24) * 2 * np.pi
    mesh_theta_rmlt, mesh_r_rmlt = np.meshgrid(theta_mlt, r_bins)
    # (r, mlat)
    theta_mlat = np.deg2rad(mlat_bins)  # -90度～90度 → -π/2～π/2ラジアン
    mesh_theta_rmlat, mesh_r_rmlat = np.meshgrid(theta_mlat, r_bins)

    # getdata
    getdata.messenger_mag(trange, parent_dir_cdf_files=parent_dir_messenger_data)
    getdata.messenger_orb(trange, parent_dir_cdf_files=parent_dir_messenger_data)

    mag_analysis(
        resampling_rate=resampling_rate,
        average_window_mfa_sec=average_window_mfa_sec
    )

    spec_analysis(
        resampling_rate=resampling_rate,
        spec_window_size=spec_window_size,
        spec_rate_overlap=spec_rate_overlap,
        average_window_sec=average_window_sec
    )


    dict_intenstiy_dist = get_intensity_dist(
        'pos_rmlatmlt',
        'mag_mfa_x_dpwrspc_psd',
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
    )
    dict_intenstiy_dist['mesh_theta_rmlt'] = mesh_theta_rmlt
    dict_intenstiy_dist['mesh_r_rmlt'] = mesh_r_rmlt
    dict_intenstiy_dist['mesh_theta_rmlat'] = mesh_theta_rmlat
    dict_intenstiy_dist['mesh_r_rmlat'] = mesh_r_rmlat
    dict_intenstiy_dist['r_bins'] = r_bins
    dict_intenstiy_dist['mlt_bins'] = mlt_bins
    dict_intenstiy_dist['mlat_bins'] = mlat_bins

    return dict_intenstiy_dist


def get_intensity_dist_trange_list(
        trange_list,
        parent_dir_messenger_data='messenger_data',
        resampling_rate=20,
        average_window_mfa_sec=30,
        spec_window_size=1024,
        spec_rate_overlap=.9,
        average_window_sec=10,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
        savecdf='dist_intensity_trange_list.cdf'
):
    """
    Return
    -----
    dict: 
    * 'mesh_theta_rmlt'
    * 'mesh_r_rmlt'
    * 'rmlt_intensity_avg'
    * 'rmlt_count'
    * 'mesh_theta_rmlat'
    * 'mesh_r_rmlat'
    * 'rmlat_intensity_avg'
    * 'rmlat_count'
    """
    dict_intensity_meshgrid = {}
    
    start_loop_time = datetime.now()
    for i, trange_i in enumerate(trange_list):
        try:
            display.progress_bar(i, len(trange_list), start_loop_time)
            display.current_time_comment('#', comment=f'{trange_i=}')
            pytplot.del_data()
            # 個別の期間の滞在時間を計算
            dict_intensity_meshgrid_i = get_intensity_dist_trange(
                trange_i,
                parent_dir_messenger_data=parent_dir_messenger_data,
                r_bins=r_bins,
                mlt_bins=mlt_bins,
                mlat_bins=mlat_bins,
                resampling_rate=resampling_rate,
                average_window_mfa_sec=average_window_mfa_sec,
                spec_window_size=spec_window_size,
                spec_rate_overlap=spec_rate_overlap,
                average_window_sec=average_window_sec,
            )

            if len(dict_intensity_meshgrid_i) == 0:
                print(f"Warning: Skipping time range {i+1} ({trange_i[0]} to {trange_i[1]}) due to error in get_dwell_time.")
                continue
            
            if len(dict_intensity_meshgrid) == 0:
                # 最初の期間: 全期間合計用の辞書を初期化
                dict_intensity_meshgrid['trange_i_first'] = trange_i
                dict_intensity_meshgrid = dict_intensity_meshgrid_i
            else:
                # rmlt
                total_intentisy_rmlt = dict_intensity_meshgrid['rmlt_intensity_avg'] * dict_intensity_meshgrid['rmlt_count'] + dict_intensity_meshgrid_i['rmlt_intensity_avg'] * dict_intensity_meshgrid_i['rmlt_count']
                total_count_rmlt = dict_intensity_meshgrid['rmlt_count'] + dict_intensity_meshgrid_i['rmlt_count']
                non_zero_rmlt = total_count_rmlt > 0  # カウントが0より大きい場所
                dict_intensity_meshgrid['rmlt_intensity_avg'][non_zero_rmlt] = total_intentisy_rmlt[non_zero_rmlt] / total_count_rmlt[non_zero_rmlt]
                dict_intensity_meshgrid['rmlt_count'] = total_count_rmlt

                # rmlat
                total_intentisy_rmlat = dict_intensity_meshgrid['rmlat_intensity_avg'] * dict_intensity_meshgrid['rmlat_count'] + dict_intensity_meshgrid_i['rmlat_intensity_avg'] * dict_intensity_meshgrid_i['rmlat_count']
                total_count_rmlat = dict_intensity_meshgrid['rmlat_count'] + dict_intensity_meshgrid_i['rmlat_count']
                non_zero_rmlat = total_count_rmlat > 0  # カウントが0より大きい場所
                dict_intensity_meshgrid['rmlat_intensity_avg'][non_zero_rmlat] = total_intentisy_rmlat[non_zero_rmlat] / total_count_rmlat[non_zero_rmlat]
                dict_intensity_meshgrid['rmlat_count'] = total_count_rmlat

                # trange_i
                dict_intensity_meshgrid['trange_i'] = trange_i
            
            # cdf file
            dict_to_cdffile(
                dict_intensity_meshgrid,
                savecdf=savecdf
            )

        except Exception as e:
            print(f"Error in processing {trange_i}: {e}")
                
    return dict_intensity_meshgrid


def update_intensity_dist(
        dict_intensity_meshgrid,
        dict_intensity_meshgrid_i,
):
    # rmlt
    total_intentisy_rmlt = dict_intensity_meshgrid['rmlt_intensity_avg'] * dict_intensity_meshgrid['rmlt_count'] + dict_intensity_meshgrid_i['rmlt_intensity_avg'] * dict_intensity_meshgrid_i['rmlt_count']
    total_count_rmlt = dict_intensity_meshgrid['rmlt_count'] + dict_intensity_meshgrid_i['rmlt_count']
    non_zero_rmlt = total_count_rmlt > 0  # カウントが0より大きい場所
    dict_intensity_meshgrid['rmlt_intensity_avg'][non_zero_rmlt] = total_intentisy_rmlt[non_zero_rmlt] / total_count_rmlt[non_zero_rmlt]
    dict_intensity_meshgrid['rmlt_count'] = total_count_rmlt

    # rmlat
    total_intentisy_rmlat = dict_intensity_meshgrid['rmlat_intensity_avg'] * dict_intensity_meshgrid['rmlat_count'] + dict_intensity_meshgrid_i['rmlat_intensity_avg'] * dict_intensity_meshgrid_i['rmlat_count']
    total_count_rmlat = dict_intensity_meshgrid['rmlat_count'] + dict_intensity_meshgrid_i['rmlat_count']
    non_zero_rmlat = total_count_rmlat > 0  # カウントが0より大きい場所
    dict_intensity_meshgrid['rmlat_intensity_avg'][non_zero_rmlat] = total_intentisy_rmlat[non_zero_rmlat] / total_count_rmlat[non_zero_rmlat]
    dict_intensity_meshgrid['rmlat_count'] = total_count_rmlat

    if np.any(np.isnan(dict_intensity_meshgrid['rmlt_intensity_avg'])):
        display.warning('rmlt_intensity_avg includes nan')
    if np.any(np.isnan(dict_intensity_meshgrid['rmlat_intensity_avg'])):
        display.warning('rmlat_intensity_avg includes nan')

    return dict_intensity_meshgrid


def create_ref_intensity_dist_cdf(
        trange,
        parent_dir_messenger_data='messenger_data',
        parent_dir_save_cdf='dist/intensity/ref_intensity/1month',
        basename_cdf='messenger_dist_intensity_ref',
        resampling_rate=20,
        average_window_mfa_sec=30,
        spec_window_size=1024,
        spec_rate_overlap=.9,
        average_window_sec=10,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
        force_create=True,
):
    time_list_month = util.make_time_list(trange, 1, 'months')
    dir_savecdf = os.path.join(parent_dir_save_cdf)

    loop_start_time = datetime.now()
    for i, trange_month_i in enumerate(time_list_month):
        display.current_time_comment('#', comment=f'{trange_month_i=}')
        display.progress_bar(i, len(time_list_month), loop_start_time, color='yellow')
        time_list = util.make_time_list(trange_month_i, 2, 'hours')
        dict_intensity_meshgrid = {}

        dt_start = time.convert(trange_month_i[0], frm='str', into='datetime')
        savecdf = os.path.join(dir_savecdf, f'{dt_start.year:04}/{basename_cdf}_{dt_start.year:04}{dt_start.month:02}.cdf')

        if os.path.exists(savecdf) and not force_create: # continue
            dict_cdffile = cdffile_to_dict(savecdf)
            trange_i_cdffile = dict_cdffile['trange_i']
            display.info(f'Starting from {trange_i_cdffile[1]}')
            time_list = util.make_time_list([trange_i_cdffile[1], trange_month_i[1]], 2, 'hours')

        loop_start_time_j = datetime.now()
        for j, trange_i in enumerate(time_list):
            try:
                pytplot.del_data()
                display.current_time_comment('#', comment=f'{trange_i=}')
                display.progress_bar(j, len(time_list), loop_start_time_j)
                dt_start = time.convert(trange_i[0], frm='str', into='datetime')

                dict_intensity_meshgrid_i = get_intensity_dist_trange(
                    trange_i,
                    parent_dir_messenger_data=parent_dir_messenger_data,
                    r_bins=r_bins,
                    mlt_bins=mlt_bins,
                    mlat_bins=mlat_bins,
                    resampling_rate=resampling_rate,
                    average_window_mfa_sec=average_window_mfa_sec,
                    spec_window_size=spec_window_size,
                    spec_rate_overlap=spec_rate_overlap,
                    average_window_sec=average_window_sec,
                )

                if len(dict_intensity_meshgrid_i) == 0:
                    print(f"Warning: Skipping time range {i+1} ({trange_i[0]} to {trange_i[1]}) due to error in get_dwell_time.")
                    continue
                
                if len(dict_intensity_meshgrid) == 0:
                    # 最初の期間: 全期間合計用の辞書を初期化
                    dict_intensity_meshgrid['trange_i_first'] = trange_i
                    dict_intensity_meshgrid = dict_intensity_meshgrid_i
                else:
                    dict_intensity_meshgrid = update_intensity_dist(dict_intensity_meshgrid, dict_intensity_meshgrid_i)
                    # trange_i
                    dict_intensity_meshgrid['trange_i'] = trange_i
                
                # cdf file
                dict_to_cdffile(
                    dict_intensity_meshgrid,
                    savecdf=savecdf
                )

            except Exception as e:
                print(f"Error in processing {trange_i}: {e}")

    return


def get_intensity_dist_trange_with_ref(
        trange,
        parent_dir_ref='messenger/messenger_data_analysis/dist/intensity/ref_intensity/1month',
        resampling_rate=20,
        average_window_mfa_sec=30,
        spec_window_size=1024,
        spec_rate_overlap=.9,
        average_window_sec=10,
        r_bins=None,
        mlt_bins=None,
        mlat_bins=None,
):
    dt_start, dt_end = time.convert(trange, frm='str', into='datetime')
    if dt_start.hour == 0:
        dt_start_ref = datetime(dt_start.year, dt_start.month , 1, 0, 0, 0).replace(tzinfo=timezone.utc)
    else:
        dt_start_ref = datetime(dt_start.year, dt_start.month + 1, 1, 0, 0, 0).replace(tzinfo=timezone.utc)
    dt_end_ref = datetime(dt_end.year, dt_end.month + 1, 1, 0, 0, 0).replace(tzinfo=timezone.utc)

    ref_cdf_filepaths = []
    current_dt_start_ref = dt_start_ref
    while current_dt_start_ref < dt_end_ref:
        year = current_dt_start_ref.year
        month = current_dt_start_ref.month
        cdf_filepath = os.path.join(
            parent_dir_ref,
            f'{year:04}/messenger_dist_intensity_ref_{year:04}{month:02}.cdf'
        )
        ref_cdf_filepaths.append(cdf_filepath)
        current_dt_start_ref += relativedelta(months=1)
    
    ref_cdf_filepaths_exist = []
    for ref_cdffile in ref_cdf_filepaths:
        if os.path.exists(ref_cdffile):
            ref_cdf_filepaths_exist.append(ref_cdffile)
        else:
            display.warning(f'No such a cdf file: {ref_cdffile}')
    
    if ref_cdf_filepaths_exist:
        dict_intensity_meshgrid = {}
        for ref_cdffile in ref_cdf_filepaths_exist:
            dict_intensity_meshgrid_i = cdffile_to_dict(ref_cdffile)
            if len(dict_intensity_meshgrid) == 0:
                # 最初の期間: 全期間合計用の辞書を初期化
                dict_intensity_meshgrid = dict_intensity_meshgrid_i
            else:
                dict_intensity_meshgrid = update_intensity_dist(dict_intensity_meshgrid, dict_intensity_meshgrid_i)
            
            if np.any(np.isnan(dict_intensity_meshgrid['rmlt_intensity_avg'])):
                display.warning('rmlt_intensity_avg includes nan')
                display.debug(f'{dict_intensity_meshgrid['rmlt_intensity_avg']}')
            if np.any(np.isnan(dict_intensity_meshgrid['rmlat_intensity_avg'])):
                display.warning('rmlat_intensity_avg includes nan')
                display.debug(f'{dict_intensity_meshgrid['rmlat_intensity_avg']}')
            
                
    else:
        dict_intensity_meshgrid = {}
    
    # former: [dt_start, dt_start_ref]
    if dt_start < dt_start_ref:
        pytplot.del_data()
        start_former = time.convert(dt_start, frm='datetime', into='str')
        end_former = time.convert(dt_start_ref, frm='datetime', into='str')
        dict_intensity_meshgrid_former = get_intensity_dist_trange(
            [start_former, end_former],
            resampling_rate=resampling_rate,
            average_window_mfa_sec=average_window_mfa_sec,
            spec_window_size=spec_window_size,
            spec_rate_overlap=spec_rate_overlap,
            average_window_sec=average_window_sec,
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins,
        )

    else:
        dict_intensity_meshgrid_former = {}
    
    # latter: [dt_end_ref, dt_end]
    if dt_end_ref < dt_end:
        pytplot.del_data()
        start_latter = time.convert(dt_end_ref, frm='datetime', into='str')
        end_latter = time.convert(dt_end, frm='datetime', into='str')
        dict_intensity_meshgrid_latter = get_intensity_dist_trange(
            [start_latter, end_latter],
            resampling_rate=resampling_rate,
            average_window_mfa_sec=average_window_mfa_sec,
            spec_window_size=spec_window_size,
            spec_rate_overlap=spec_rate_overlap,
            average_window_sec=average_window_sec,
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins
        )
    else:
        dict_intensity_meshgrid_latter = {}

    if len(dict_intensity_meshgrid) == 0 and len(dict_intensity_meshgrid_former) == 0 and len(dict_intensity_meshgrid_latter) == 0:
        display.warning('No distribution data')
        return
    else:
        if len(dict_intensity_meshgrid) != 0:
            if len(dict_intensity_meshgrid_former) != 0:
                dict_intensity_meshgrid = update_intensity_dist(dict_intensity_meshgrid, dict_intensity_meshgrid_former)
            if len(dict_intensity_meshgrid_latter) != 0:
                dict_intensity_meshgrid = update_intensity_dist(dict_intensity_meshgrid, dict_intensity_meshgrid_latter)
        else:
            if len(dict_intensity_meshgrid_former) == 0:
                dict_intensity_meshgrid = dict_intensity_meshgrid_latter
            else:
                dict_intensity_meshgrid = dict_intensity_meshgrid_former

    return dict_intensity_meshgrid

