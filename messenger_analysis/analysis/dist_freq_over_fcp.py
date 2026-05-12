import numpy as np
import os
from glob import glob
from datetime import datetime
from common import pytplot, util, display, distribution, mathpy, time, cdf
from messenger_analysis import getdata
from .analysis import mag_analysis, spec_analysis
from messenger_analysis.distribution.freq_over_fcp import get_representative_freqs_norm_from_spectrogram

def get_rmlatmlt_meshgrid_single_step(
        trange,
        basedir_savecdf='',
):
    resampling_rate = 20
    average_window_mfa_sec = 30
    spec_window_size = 1024
    spec_rate_overlap = .9
    average_window_sec = 10
    threshold_mean_intensity = 100
    r_bins = np.arange(1, 7+.5, .5)
    mlt_bins = np.arange(0, 24+1, 1)
    mlat_bins = np.arange(-90, 90+5, 5)

    getdata.messenger_mag(trange)
    getdata.messenger_orb(trange)

    display.info('mag_analysis')
    mag_analysis(
        resampling_rate=resampling_rate,
        average_window_mfa_sec=average_window_mfa_sec
    )
    display.info('spec_analysis')
    spec_analysis(
        resampling_rate=resampling_rate,
        spec_window_size=spec_window_size,
        spec_rate_overlap=spec_rate_overlap,
        average_window_sec=average_window_sec
    )

    # spectrogram below fcp
    dat_psd_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
    dat_psd_norm_y = pytplot.get_data('mag_mfa_y_dpwrspc_psd_norm')
    dat_psd_norm_z = pytplot.get_data('mag_mfa_z_dpwrspc_psd_norm')
    times = dat_psd_norm_x.times
    freqs_norm = dat_psd_norm_x.v
    psd_norm_x = dat_psd_norm_x.y
    psd_norm_y = dat_psd_norm_y.y
    psd_norm_z = dat_psd_norm_z.y
    psd_norm_xy = (psd_norm_x + psd_norm_y) / 2

    idx_fcp = util.get_closest_idx(freqs_norm, 1, mode='over')

    freqs_norm_below_fcp = freqs_norm[:idx_fcp]
    psd_norm_xy_below_fcp = psd_norm_xy[:, :idx_fcp]
    psd_norm_z_below_fcp = psd_norm_z[:, :idx_fcp]

    pytplot.store_data('psd_norm_xy_below_fcp', {'x': times, 'y': psd_norm_xy_below_fcp, 'v': freqs_norm_below_fcp})
    pytplot.store_data('psd_norm_z_below_fcp', {'x': times, 'y': psd_norm_z_below_fcp, 'v': freqs_norm_below_fcp})
    pytplot.options('psd_norm_xy_below_fcp', zlog=True, zrange=[5, 5e3], yrange=[0, 1.1], colormap='jet')
    pytplot.options('psd_norm_z_below_fcp', zlog=True, zrange=[5, 5e3], yrange=[0, 1.1], colormap='jet')

    # representative freqs_norm
    freqs_norm_representative_xy = get_representative_freqs_norm_from_spectrogram(times, freqs_norm_below_fcp, psd_norm_xy_below_fcp, threshold_mean_intensity=threshold_mean_intensity, n_mode=2, percentile_value=90)
    freqs_norm_representative_z = get_representative_freqs_norm_from_spectrogram(times, freqs_norm_below_fcp, psd_norm_z_below_fcp, threshold_mean_intensity=threshold_mean_intensity, n_mode=2, percentile_value=90)

    pytplot.store_data('freqs_norm_representative_xy', {'x': times, 'y': freqs_norm_representative_xy})
    pytplot.store_data('freqs_norm_representative_z', {'x': times, 'y': freqs_norm_representative_z})

    # interpolate pos_rmlatmlt with times
    dat_pos_rmlatmlt = pytplot.get_data('pos_rmlatmlt')
    times_pos = dat_pos_rmlatmlt.times
    pos_rmlatmlt = dat_pos_rmlatmlt.y
    pos_rmlatmlt_interp = mathpy.interp_vec(times, times_pos, pos_rmlatmlt)
    pytplot.store_data('pos_rmlatmlt_interp', {'x': times, 'y': pos_rmlatmlt_interp})

    
    # distribution
    # savecdf_xy = os.path.join(basedir_savecdf, 'freqs_norm_representative_xy.cdf')
    # savecdf_z = os.path.join(basedir_savecdf, 'freqs_norm_representative_z.cdf')
    dict_rmlatmlt_meshgrid_xy = distribution.rmlatmlt_meshgrid(
        'pos_rmlatmlt_interp',
        datatype='average',
        varname_data='freqs_norm_representative_xy',
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        rmlat_whole=True,
        outcdf=False,
        # save_cdf=savecdf_xy
    )

    dict_rmlatmlt_meshgrid_z = distribution.rmlatmlt_meshgrid(
        'pos_rmlatmlt_interp',
        datatype='average',
        varname_data='freqs_norm_representative_z',
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        rmlat_whole=True,
        outcdf=False,
        # save_cdf=savecdf_z
    )

    # distribution.plot_rmlatmlt(
    #     dict_rmlatmlt_meshgrid_xy['mesh_theta_rmlt'],
    #     dict_rmlatmlt_meshgrid_xy['mesh_r_rmlt'],
    #     dict_rmlatmlt_meshgrid_xy['rmlt_grid'],
    #     dict_rmlatmlt_meshgrid_xy['mesh_theta_rmlat'],
    #     dict_rmlatmlt_meshgrid_xy['mesh_r_rmlat'],
    #     dict_rmlatmlt_meshgrid_xy['rmlat_grid'],
    #     savefig='out/test/dist_freq_over_fcp_xy.png',
    #     rmlat_whole=True
    # )

    # distribution.plot_rmlatmlt(
    #     dict_rmlatmlt_meshgrid_z['mesh_theta_rmlt'],
    #     dict_rmlatmlt_meshgrid_z['mesh_r_rmlt'],
    #     dict_rmlatmlt_meshgrid_z['rmlt_grid'],
    #     dict_rmlatmlt_meshgrid_z['mesh_theta_rmlat'],
    #     dict_rmlatmlt_meshgrid_z['mesh_r_rmlat'],
    #     dict_rmlatmlt_meshgrid_z['rmlat_grid'],
    #     savefig='out/test/dist_freq_over_fcp_z.png',
    #     rmlat_whole=True
    # )

    return dict_rmlatmlt_meshgrid_xy, dict_rmlatmlt_meshgrid_z


def update_cdffile(
        cdf_filepath,
        dict_data
):
    dict_from_cdf = cdf.cdffile_to_dict(cdf_filepath)
    dict_return = {
        'mesh_theta_rmlt': dict_from_cdf['mesh_theta_rmlt'],
        'mesh_r_rmlt': dict_from_cdf['mesh_r_rmlt'],
        'mesh_theta_rmlat': dict_from_cdf['mesh_theta_rmlat'],
        'mesh_r_rmlat': dict_from_cdf['mesh_r_rmlat'],
    }
    sum_rmlt_grid_cdf = dict_from_cdf['rmlt_grid'] * dict_from_cdf['rmlt_grid_count']
    sum_rmlat_grid_cdf = dict_from_cdf['rmlat_grid'] * dict_from_cdf['rmlat_grid_count']

    sum_rmlt_grid_dict = dict_data['rmlt_grid'] * dict_data['rmlt_grid_count']
    sum_rmlat_grid_dict = dict_data['rmlat_grid'] * dict_data['rmlat_grid_count']

    sum_rmlt_grid = sum_rmlt_grid_cdf + sum_rmlt_grid_dict
    sum_rmlat_grid = sum_rmlat_grid_cdf + sum_rmlat_grid_dict

    sum_rmlt_grid_count = dict_from_cdf['rmlt_grid_count'] + dict_data['rmlt_grid_count']
    sum_rmlat_grid_count = dict_from_cdf['rmlat_grid_count'] + dict_data['rmlat_grid_count']

    rmlt_grid = np.zeros_like(sum_rmlt_grid)
    nonzero_rmlt_count = sum_rmlt_grid_count != 0
    rmlt_grid[nonzero_rmlt_count] = sum_rmlt_grid[nonzero_rmlt_count] / sum_rmlt_grid_count[nonzero_rmlt_count]
    dict_return['rmlt_grid'] = rmlt_grid

    rmlat_grid = np.zeros_like(sum_rmlat_grid)
    nonzero_rmlat_count = sum_rmlat_grid_count != 0
    rmlat_grid[nonzero_rmlat_count] = sum_rmlat_grid[nonzero_rmlat_count] / sum_rmlat_grid_count[nonzero_rmlat_count]
    dict_return['rmlat_grid'] = rmlat_grid

    dict_return['rmlt_grid_count'] = sum_rmlt_grid_count
    dict_return['rmlat_grid_count'] = sum_rmlat_grid_count

    # update cdf file
    cdf.dict_to_cdffile(dict_return, cdf_filepath)

    return dict_return


def get_rmlatmlt_meshgrid(
        trange,
        basedir_savecdf
):
    time_list = util.make_time_list(trange, 2, 'hours')
    initialized_months = []
    start_time_loop = datetime.now()
    for i, trange_i in enumerate(time_list):
        try:
            display.progress_bar(i, len(time_list), start_time_loop)
            display.info(f'{trange_i=}')
            pytplot.del_data()
            dict_xy, dict_z = get_rmlatmlt_meshgrid_single_step(trange_i)
            dt_start = time.convert(trange_i[0], frm='str', into='datetime')
            year = dt_start.year
            month = dt_start.month
            year_month_key = f"{year:04}{month:02}"
            savecdf_xy = os.path.join(
                basedir_savecdf,
                f'{year:04}',
                f'{month:02}',
                f'dist_freq_over_fcp_xy_{year:04}{month:02}.cdf'
            )
            savecdf_z = os.path.join(
                basedir_savecdf,
                f'{year:04}',
                f'{month:02}',
                f'dist_freq_over_fcp_z_{year:04}{month:02}.cdf'
            )

            if year_month_key not in initialized_months:
                for fpath in [savecdf_xy, savecdf_z]:
                    if os.path.exists(fpath):
                        os.remove(fpath)
                        display.info(f'Removed existing file for new month: {fpath}')
                initialized_months.append(year_month_key)

            # xy
            if os.path.exists(savecdf_xy):
                update_cdffile(savecdf_xy, dict_xy)
            else:
                cdf.dict_to_cdffile(dict_xy, savecdf_xy)

            # z
            if os.path.exists(savecdf_z):
                update_cdffile(savecdf_z, dict_z)
            else:
                cdf.dict_to_cdffile(dict_z, savecdf_z)
            
        except Exception as e:
            display.error(f'{trange_i=}, {e}')
        
    return


def update_dict(
        dict_data,
        dict_data_i
):
    dict_return = dict_data.copy()
    sum_rmlt_grid_data = dict_data['rmlt_grid'] * dict_data['rmlt_grid_count']
    sum_rmlat_grid_data = dict_data['rmlat_grid'] * dict_data['rmlat_grid_count']

    sum_rmlt_grid_i = dict_data_i['rmlt_grid'] * dict_data_i['rmlt_grid_count']
    sum_rmlat_grid_i = dict_data_i['rmlat_grid'] * dict_data_i['rmlat_grid_count']

    sum_rmlt_grid = sum_rmlt_grid_data + sum_rmlt_grid_i
    sum_rmlat_grid = sum_rmlat_grid_data + sum_rmlat_grid_i

    sum_rmlt_grid_count = dict_data['rmlt_grid_count'] + dict_data_i['rmlt_grid_count']
    sum_rmlat_grid_count = dict_data['rmlat_grid_count'] + dict_data_i['rmlat_grid_count']

    rmlt_grid = np.zeros_like(sum_rmlt_grid)
    nonzero_rmlt_count = sum_rmlt_grid_count != 0
    rmlt_grid[nonzero_rmlt_count] = sum_rmlt_grid[nonzero_rmlt_count] / sum_rmlt_grid_count[nonzero_rmlt_count]
    dict_return['rmlt_grid'] = rmlt_grid

    rmlat_grid = np.zeros_like(sum_rmlat_grid)
    nonzero_rmlat_count = sum_rmlat_grid_count != 0
    rmlat_grid[nonzero_rmlat_count] = sum_rmlat_grid[nonzero_rmlat_count] / sum_rmlat_grid_count[nonzero_rmlat_count]
    dict_return['rmlat_grid'] = rmlat_grid

    dict_return['rmlt_grid_count'] = sum_rmlt_grid_count
    dict_return['rmlat_grid_count'] = sum_rmlat_grid_count

    return dict_return


def plot_dist(
        trange,
        basedir_cdf
):
    time_list = util.make_time_list(trange, 1, 'months')
    dict_xy = {}
    is_first_xy = True
    is_first_z = True
    for i, trange_i in enumerate(time_list):
        dt_start = time.convert(trange_i[0], frm='str', into='datetime')
        year = dt_start.year
        month = dt_start.month
        # xy
        cdf_filepath_search_xy = os.path.join(
            basedir_cdf,
            f'{year:04}',
            f'{month:02}',
            f'dist*_xy_{year:04}{month:02}.cdf'
        )
        cdf_filepath_candidate_xy = glob(cdf_filepath_search_xy)
        if len(cdf_filepath_candidate_xy) == 0:
            display.warning(f'No cdf file: {cdf_filepath_search_xy}')
            continue
        elif len(cdf_filepath_candidate_xy) == 1:
            cdf_filepath_xy = cdf_filepath_candidate_xy[0]
        else:
            display.warning(f'cdf_filepath_candidate_xy is not 1: {len(cdf_filepath_candidate_xy)=} -> adopted the 1st one')
            cdf_filepath_xy = cdf_filepath_candidate_xy[0]
        
        dict_xy_i = cdf.cdffile_to_dict(cdf_filepath_xy)
        if is_first_xy:
            dict_xy = dict_xy_i
            is_first_xy = False
        else: # update dict data
            dict_xy = update_dict(dict_xy, dict_xy_i)
        
        # z
        cdf_filepath_search_z = os.path.join(
            basedir_cdf,
            f'{year:04}',
            f'{month:02}',
            f'dist*_z_{year:04}{month:02}.cdf'
        )
        cdf_filepath_candidate_z = glob(cdf_filepath_search_z)
        if len(cdf_filepath_candidate_z) == 0:
            display.warning(f'No cdf file: {cdf_filepath_search_z}')
            continue
        elif len(cdf_filepath_candidate_z) == 1:
            cdf_filepath_z = cdf_filepath_candidate_z[0]
        else:
            display.warning(f'cdf_filepath_candidate_z is not 1: {len(cdf_filepath_candidate_z)=} -> adopted the 1st one')
            cdf_filepath_z = cdf_filepath_candidate_z[0]
        
        dict_z_i = cdf.cdffile_to_dict(cdf_filepath_z)
        if is_first_z:
            dict_z = dict_z_i
            is_first_z = False
        else: # update dict data
            dict_z = update_dict(dict_z, dict_z_i)
        
    # plot
    distribution.plot_rmlatmlt(
        dict_xy['mesh_theta_rmlt'],
        dict_xy['mesh_r_rmlt'],
        dict_xy['rmlt_grid'],
        dict_xy['mesh_theta_rmlat'],
        dict_xy['mesh_r_rmlat'],
        dict_xy['rmlat_grid'],
        savefig='out/test/dist_freq_over_fcp_xy.png',
        rmlat_whole=True,
        colormap='jet',
        suptitle=f'f/fcp distribution in PSD_xy: {trange}'
    )

    distribution.plot_rmlatmlt(
        dict_z['mesh_theta_rmlt'],
        dict_z['mesh_r_rmlt'],
        dict_z['rmlt_grid'],
        dict_z['mesh_theta_rmlat'],
        dict_z['mesh_r_rmlat'],
        dict_z['rmlat_grid'],
        savefig='out/test/dist_freq_over_fcp_z.png',
        rmlat_whole=True,
        colormap='jet',
        suptitle=f'f/fcp distribution in PSD_z: {trange}'
    )
    return
