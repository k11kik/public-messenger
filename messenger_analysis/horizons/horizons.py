import numpy as np
import pandas as pd
import os
from common import display, path, time, cdf
from .downloader import download_horizons_data


def load_taa(
        trange,
        savecdf=None
):
    csv_filepath = download_horizons_data(
        target_id='199',
        location='@sun',
        start_time=trange[0],
        stop_time=trange[1],
        time_step='1d',
    )
    df = pd.read_csv(csv_filepath)
    times_dt = pd.to_datetime(df['datetime_str'], format='%Y-%b-%d %H:%M').to_list()
    times_unix = time.convert(times_dt, frm='datetime', into='unix')
    times_unix = np.array(times_unix)
    taa = df['true_anom'].to_numpy()
    dict_return = {
        'times': times_unix,
        'taa': taa
    }
    start_str, end_str = time.convert([times_unix[0], times_unix[-1]], frm='unix', into='str')
    dict_description = {
        'times': f'time array (unix): [{start_str}, {end_str}]',
        'taa': 'TAA from Horizons https://ssd.jpl.nasa.gov/horizons/app.html#/'
    }
    
    if savecdf is None:
        filepath = os.path.splitext(csv_filepath)[0]
        savecdf = filepath + '.cdf'
    
    cdf.dict_to_cdffile(dict_return, savecdf, dict_description=dict_description)
    return
