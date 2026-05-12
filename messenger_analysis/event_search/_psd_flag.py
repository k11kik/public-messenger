import numpy as np
from common import display


def get_psd_flag(
        psd_x,
        psd_y,
        psd_z,
        threshold_psd=1e2,
        threshold_ratio=10
):
    psd_xy = (psd_x + psd_y) / 2
    noise = np.nanpercentile(psd_z, 50)
    is_event_psd = (psd_xy > threshold_psd * noise)
    psd_ratio = psd_xy / psd_z
    is_event_ratio = psd_ratio > threshold_ratio
    # flag_psd = np.where(is_event_psd, 1, 0)
    # flag_ratio = np.where(is_event_ratio, 1, 0)
    flag = np.where(is_event_psd & is_event_ratio, 1, 0)
    return flag

