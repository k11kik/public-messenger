import numpy as np
from common import pytplot
# from ._psd_flag import get_psd_flag
# from ._polari_flag import get_polari_flag
# from ._extract import get_dense_flag
from ._get_emic_flag import get_psd_flag, get_polari_flag, get_dense_flag, get_emic_flag


def get_event_flag(
        var_psd_norm_x,
        var_psd_norm_y,
        var_psd_norm_z,
        var_polari,
        threshold_psd=1e3,
        threshold_ratio=1,
        threshold_polari=-.5,
        varname_out='event_flag',
        window_size=(5, 5),
        min_density=0.5,
):
    dat_psd_x = pytplot.get_data(var_psd_norm_x)
    dat_psd_y = pytplot.get_data(var_psd_norm_y)
    dat_psd_z = pytplot.get_data(var_psd_norm_z)
    times = dat_psd_x.times
    freqs = dat_psd_x.v
    flag_psd = get_psd_flag(
        dat_psd_x.y,
        dat_psd_y.y,
        dat_psd_z.y,
        threshold_psd=threshold_psd,
        threshold_ratio=threshold_ratio
    )
    dat_polari = pytplot.get_data(var_polari)
    flag_polari = get_polari_flag(
        dat_polari.y,
        threshold_polari=threshold_polari
    )
    flag = np.where((flag_psd == 1) & (flag_polari == 1), 1, 0)

    emic_flag = get_emic_flag(
        times,
        freqs,
        flag
    )

    dense_flag = get_dense_flag(emic_flag, window_size=window_size, min_density=min_density)


    pytplot.store_data(f'{varname_out}_psd', {'x': dat_psd_x.times, 'y': flag_psd, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_psd', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_polari', {'x': dat_psd_x.times, 'y': flag_polari, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_polari', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(varname_out, {'x': dat_psd_x.times, 'y': flag, 'v': dat_psd_x.v})
    pytplot.options(varname_out, colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_emic', {'x': dat_psd_x.times, 'y': emic_flag, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_emic', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_dense', {'x': dat_psd_x.times, 'y': dense_flag, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_dense', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])


    return


def get_wna_flag(
        wna,
        threshold_wna=30
):
    flag = np.where((wna < threshold_wna) & (wna >= 0), 1, 0)
    return flag


def get_planarity_flag(
        planarity,
        threshold_planarity=.5
):
    flag = np.where((planarity > threshold_planarity) & (planarity <= 1), 1, 0)
    return flag



def get_event_flag_emic(
        var_psd_norm_x,
        var_psd_norm_y,
        var_psd_norm_z,
        var_polari,
        var_wna,
        var_planarity,
        threshold_psd=1e3,
        threshold_ratio=1,
        threshold_polari=-.5,
        threshold_wna=30,
        threshold_planarity=.5,
        varname_out='event_flag',
        # window_size=(5, 5),
        # min_density=0.5,
):
    dat_psd_x = pytplot.get_data(var_psd_norm_x)
    dat_psd_y = pytplot.get_data(var_psd_norm_y)
    dat_psd_z = pytplot.get_data(var_psd_norm_z)
    times = dat_psd_x.times
    freqs = dat_psd_x.v
    flag_psd, dict_support_flag_psd = get_psd_flag(
        dat_psd_x.y,
        dat_psd_y.y,
        dat_psd_z.y,
        threshold_psd=threshold_psd,
        threshold_ratio=threshold_ratio,
        get_support_data=True
    )
    polari = pytplot.get_data(var_polari).y
    wna = pytplot.get_data(var_wna).y
    planarity = pytplot.get_data(var_planarity).y
    flag_polari = get_polari_flag(
        polari,
        threshold_polari=threshold_polari
    )
    flag_wna = get_wna_flag(wna, threshold_wna=threshold_wna)
    flag_planarity = get_planarity_flag(planarity, threshold_planarity=threshold_planarity)
    flag = np.where((flag_psd == 1) & (flag_polari == 1) & (flag_wna == 1) & (flag_planarity == 1), 1, 0)

    # emic_flag = get_emic_flag(
    #     times,
    #     freqs,
    #     flag
    # )

    # dense_flag = get_dense_flag(emic_flag, window_size=window_size, min_density=min_density)

    pytplot.store_data(f'{varname_out}_psd_intensity', {'x': dat_psd_x.times, 'y': dict_support_flag_psd['flag_psd_intensity'], 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_psd_intensity', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_psd_ratio', {'x': dat_psd_x.times, 'y': dict_support_flag_psd['flag_psd_ratio'], 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_psd_ratio', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_psd', {'x': dat_psd_x.times, 'y': flag_psd, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_psd', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_polari', {'x': dat_psd_x.times, 'y': flag_polari, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_polari', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_wna', {'x': dat_psd_x.times, 'y': flag_polari, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_wna', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_planarity', {'x': dat_psd_x.times, 'y': flag_polari, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_planarity', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    pytplot.store_data(f'{varname_out}_emic', {'x': dat_psd_x.times, 'y': flag, 'v': dat_psd_x.v})
    pytplot.options(f'{varname_out}_emic', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    # pytplot.store_data(f'{varname_out}_emic', {'x': dat_psd_x.times, 'y': emic_flag, 'v': dat_psd_x.v})
    # pytplot.options(f'{varname_out}_emic', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])

    # pytplot.store_data(f'{varname_out}_dense', {'x': dat_psd_x.times, 'y': dense_flag, 'v': dat_psd_x.v})
    # pytplot.options(f'{varname_out}_dense', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])


    return


