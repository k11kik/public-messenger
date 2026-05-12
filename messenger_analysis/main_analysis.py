import numpy as np

from messenger_analysis import getdata
from common import pytplot, data_process, spec, quant

def main_analysis():
    trange = ['2013-01-01 22:00:00', '2013-01-02 00:00:00']
    getdata.messenger_mag(trange)
    getdata.messenger_orb(trange)

    # resampling
    resampling_rate = 10

    dat_mag = pytplot.get_data('mag')
    times = dat_mag.times
    mag = dat_mag.y
    times_resampled, mag_resampled = data_process.resample_data(times, mag, target_sampling_rate=resampling_rate)
    pytplot.store_data('mag_resampled', {'x': times_resampled, 'y': mag_resampled})

    # spectrogram
    spec.spectrogram_vec('mag_resampled', rate_overlap=.9)
    dat_psd_abs = pytplot.get_data('mag_resampled_psd_abs')

    # fcp
    dat_mag_norm = pytplot.get_data('mag_norm')
    _, mag_norm_resampled = data_process.resample_data(times, dat_mag_norm.y, target_sampling_rate=resampling_rate)
    fcp = quant.cyclotron_frequency(1, mag_norm_resampled * 1e-9)
    fcp = np.interp(dat_psd_abs.times, times_resampled, fcp)
    pytplot.store_data('fcp', {'x': dat_psd_abs.times, 'y': fcp})



    pytplot.tplot_names()

    # cdf_file_path = "messenger_data/mag_mso/2014/01/messenger_mag_mso_20140101.cdf"
    # cdf.cdfdata.info(cdf_file_path)
    # cdf_data = cdf.cdfdata.get(cdf_file_path)
    # times = cdf_data['time']
    # mag = cdf_data['mag']
    # pos = cdf_data['pos']
    # pytplot.store_data('mag', {'x': times, 'y': mag})
    # pytplot.store_data('pos', {'x': times, 'y': pos})
    # pytplot.tplot(['mag', 'pos'])
    pytplot.options(
        'mag', 
        legend_names=['Bx', 'By', 'Bz'],
        legend=1,
        ylabel='mag_mso'
    )
    pytplot.options(
        'pos',
        ylabel='pos_mso',
        legend_names=['x_mso', 'y_mso', 'z_mso'],
        legend=1
    )
    pytplot.options(
        'mag_resampled_psd_abs',
        zlog=True,
        zrange=[5e-2, 5e4],
        ylog=True,
        yrange=[5e-2, int(resampling_rate / 2)],
        colormap='jet'
    )
    pytplot.options(
        'fcp',
        color='white',
        linestyle='dashed',
        # linewidth=3,
    )
    
    pytplot.tplot(
        [
            # 'mag',
            'mag_resampled',
            'mag_norm',
            # 'fcp',
            ['mag_resampled_psd_abs', 'fcp']
        ],
        delta_xticks=30,
        timeunit_xticks='minutes',
        save_png='out/test/mag.png',
        var_orbit='pos',
        list_label_orbit=['X_MSO', 'Y_MSO', 'Z_MSO', 'TIME']

    )

    
    return




# --------------------------------------------------------------------------
# distribution
# --------------------------------------------------------------------------
def distribution_freq_over_fcp():
    from messenger_analysis.analysis.dist_freq_over_fcp import (
        get_rmlatmlt_meshgrid
    )

    get_rmlatmlt_meshgrid(
        ['2011-03-01 00:00:00', '2015-05-01 00:00:00'],
        basedir_savecdf=r"D:\messenger\messenger_data_analysis\dist\freq_over_fcp"
    )
    return


def plot_distribution_freq_over_fcp():
    from messenger_analysis.analysis.dist_freq_over_fcp import (
        plot_dist
    )

    # basedir_cdf = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/dist/freq_over_fcp'
    basedir_cdf = r"D:\messenger\messenger_data_analysis\dist\freq_over_fcp"
    plot_dist(
        ['2011-03-01 00:00:00', '2015-05-01 00:00:00'],
        basedir_cdf=basedir_cdf
    )
    return
