import os
from datetime import datetime
from common import cdf, pytplot, orbit, time, display, util, path
from common.data_process.resampling import resample_data
from common.const.const_planets import RM


def create_orb_data_from_cdf_filepath(
        cdf_filepath,
        savecdf,
        timeres=6, # time resolution [s]
):
    if not os.path.exists(cdf_filepath):
        display.warning(f'No existing file: {cdf_filepath}')
        return
    
    dict_data = cdf.cdffile_to_dict(cdf_filepath)

    # resampling
    times_orig = dict_data['time']
    orb_mso_orig = dict_data['pos']
    times, orb_mso = resample_data(times_orig, orb_mso_orig, target_sampling_rate=1/timeres)
    orb_mso /= RM * 1e-3
    pytplot.store_data('orb_mso', {'x': times, 'y': orb_mso})
    orbit.xyz2polar('orb_mso', 'orb_polar', to='polar')
    orbit.rmlatmlt2polar('orb_polar', 'orb_rmlatmlt', to='rmlatmlt')

    # output cdf
    dict_return = {
        'times': times,
        'orb_mso': orb_mso,
        'orb_polar': pytplot.get_data('orb_polar').y,
        'orb_rmlatmlt': pytplot.get_data('orb_rmlatmlt').y,
    }
    cdf.dict_to_cdffile(dict_return, savecdf)

    return


def create_orb_data(
        trange,
        basedir_mag_mso,
        basedir_savecdf,
        timeres=6,
):
    trange_list = util.make_time_list(trange, 1, 'days')
    start_time_loop = datetime.now()
    for i, trange_i in enumerate(trange_list):
        display.progress_bar(i, len(trange_list), start_time_loop)
        pytplot.del_data()
        dt_start = time.convert(trange_i[0], frm='str', into='datetime')
        year = dt_start.year
        month = dt_start.month
        day = dt_start.day
        cdf_filepath_search = os.path.join(
            basedir_mag_mso,
            f'{year:04}',
            f'{month:02}',
            f'messenger_*_{year:04}{month:02}{day:02}.cdf'
        )
        cdf_filepath = path.glob_one(cdf_filepath_search)
        if cdf_filepath is None:
            display.info('cdf_filepath is None -> continue')
            continue

        savecdf = os.path.join(
            basedir_savecdf,
            f'{year:04}',
            f'{month:02}',
            f'messenger_orb_{timeres}s_{year:04}{month:02}{day:02}.cdf'
        )
        create_orb_data_from_cdf_filepath(
            cdf_filepath,
            savecdf,
            timeres=timeres
        )

    return
