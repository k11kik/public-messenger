from common import pytplot, cdf
from .analysis import analysis
from messenger_analysis.event_search.get_event_flag import get_event_flag_emic


def create_event_flag_emic_trange(
        trange,
        basedir_mag_mso='',
        basedir_orb='',
        threshold_psd=1e3,
        threshold_ratio=2,
        threshold_polari=-0.5,
        threshold_wna=30,
        threshold_planarity=.6,
        savecdf=None,
        save_all=False,
):
    params = analysis(
        trange,
        basedir_orb=basedir_orb,
        basedir_cdf_files=basedir_mag_mso,
        spec_window_sec=200,
    )

    dat_psd_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
    times = dat_psd_norm_x.times
    freqs_norm = dat_psd_norm_x.v
    get_event_flag_emic(
        'mag_mfa_x_dpwrspc_psd_norm',
        'mag_mfa_y_dpwrspc_psd_norm',
        'mag_mfa_z_dpwrspc_psd_norm',
        'polarization_norm',
        'wna_norm',
        'planarity_norm',
        threshold_psd=threshold_psd,
        threshold_ratio=threshold_ratio,
        threshold_polari=threshold_polari,
        threshold_wna=threshold_wna,
        threshold_planarity=threshold_planarity
    )

    
    event_flag_emic = pytplot.get_data('event_flag_emic').y

    if save_all:
        event_flag_psd_intensity = pytplot.get_data('event_flag_psd_intensity').y
        event_flag_psd_ratio = pytplot.get_data('event_flag_psd_ratio').y
        event_flag_psd = pytplot.get_data('event_flag_psd').y
        event_flag_polari = pytplot.get_data('event_flag_polari').y
        event_flag_wna = pytplot.get_data('event_flag_wna').y
        event_flag_planarity = pytplot.get_data('event_flag_planarity').y
        dict_return = {
            'times': times,
            'freqs_norm': freqs_norm,
            'threshold_psd': threshold_psd,
            'threshold_ratio': threshold_ratio,
            'threshold_polari': threshold_polari,
            'threshold_wna': threshold_wna,
            'threshold_planarity': threshold_planarity,
            'event_flag_psd_intensity': event_flag_psd_intensity,
            'event_flag_psd_ratio': event_flag_psd_ratio,
            'event_flag_psd': event_flag_psd,
            'event_flag_polarization': event_flag_polari,
            'event_flag_wna': event_flag_wna,
            'event_flag_planarity': event_flag_planarity,
            'event_flag_emic': event_flag_emic,
        }
    else:
        dict_return = {
            'times': times,
            'freqs_norm': freqs_norm,
            'threshold_psd_': threshold_psd,
            'threshold_ratio': threshold_ratio,
            'threshold_polari': threshold_polari,
            'threshold_wna': threshold_wna,
            'threshold_planarity': threshold_planarity,
            # 'event_flag_psd_intensity': event_flag_psd_intensity,
            # 'event_flag_psd_ratio': event_flag_psd_ratio,
            # 'event_flag_psd': event_flag_psd,
            # 'event_flag_polarization': event_flag_polari,
            # 'event_flag_wna': event_flag_wna,
            # 'event_flag_planarity': event_flag_planarity,
            'event_flag_emic': event_flag_emic,
        }


    dict_return.update(params)
    # remove
    del dict_return['resampling_rate']
    del dict_return['window']

    if savecdf is not None:
        cdf.dict_to_cdffile(dict_return, savecdf)

    return
