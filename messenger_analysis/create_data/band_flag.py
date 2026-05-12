import os
from datetime import datetime
from common import pytplot, cdf, util, time, display, csv
from messenger_analysis.analysis.analysis import analysis
from messenger_analysis.event_search.get_event_flag import get_event_flag
from messenger_analysis.detect_band.get_band_flag import classify_bands

def create_band_flag_data_trange(
        trange,
        savecdf,
        basedir_cdf=None,
        threshold_psd=1e3,
        threshold_ratio=10,
        threshold_polari=-0.5,
        freqs_band=None,
):
    analysis(
        trange,
        basedir_cdf_files=basedir_cdf,
    )
    dat_psd_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
    times = dat_psd_norm_x.times
    freqs_norm = dat_psd_norm_x.v
    get_event_flag(
        'mag_mfa_x_dpwrspc_psd_norm',
        'mag_mfa_y_dpwrspc_psd_norm',
        'mag_mfa_z_dpwrspc_psd_norm',
        'polarization_norm',
        threshold_psd=threshold_psd,
        threshold_ratio=threshold_ratio,
        threshold_polari=threshold_polari,
    )

    emic_flag = pytplot.get_data('event_flag_emic').y

    # band flag
    if freqs_band is None:
        freqs_band = [0, 0.25, 0.5, 1.0]
    band_results = classify_bands(emic_flag, freqs_norm, freqs_band)

    dict_return = {
        'times': times,
        'freqs_norm': freqs_norm,
        'freqs_band': freqs_band,
        'threshold_psd': threshold_psd,
        'threshold_ratio': threshold_ratio,
        'threshold_polari': threshold_polari,
    }
    dict_return.update(band_results)

    cdf.dict_to_cdffile(dict_return, savecdf)
    return



def create_band_flag_data_event(
        trange,
        basedir_event,
        basedir_savecdf,
        basedir_mag_cdf=None,
        threshold_psd=1e3,
        threshold_ratio=10,
        threshold_polari=-0.5,
        freqs_band=None,
):
    trange_list = util.make_time_list(trange, 1, 'months')
    start_time_loop = datetime.now()
    for i, trange_i in enumerate(trange_list):
        pytplot.del_data()
        display.progress_bar(i, len(trange_list), start_time_loop, color='yellow')
        dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
        year_i = dt_start_i.year
        month_i = dt_start_i.month
        csv_filepath = os.path.join(
            basedir_event,
            f'{year_i:04}',
            f'emic_event_{year_i:04}{month_i:02}.csv'
        )
        if not os.path.exists(csv_filepath):
            display.warning(f'No existing csv file: {csv_filepath}')
            continue
        
        start_time_loop_i = datetime.now()
        trange_list_event = csv.get_trange_list(csv_filepath)
        for j, trange_j in enumerate(trange_list_event):
            pytplot.del_data()
            display.progress_bar(j, len(trange_list_event), start_time_loop_i)
            dt_start_j = time.convert(trange_j[0], frm='str', into='datetime')
            year_j = dt_start_j.year
            month_j = dt_start_j.month
            day_j = dt_start_j.day
            hour_j = dt_start_j.hour
            minute_j = dt_start_j.minute
            savecdf = os.path.join(
                basedir_savecdf,
                f'{year_j:04}',
                f'{month_j:02}',
                f'messenger_band_flag_emic_event_{year_j:04}{month_j:02}{day_j:02}{hour_j:02}{minute_j:02}.cdf'
            )
            create_band_flag_data_trange(
                trange_j,
                savecdf,
                basedir_cdf=basedir_mag_cdf,
                threshold_psd=threshold_psd,
                threshold_ratio=threshold_ratio,
                threshold_polari=threshold_polari,
                freqs_band=freqs_band
            )

    return