import numpy as np

def get_polari_flag(
        polari,
        threshold_polari=-.5
):
    flag = np.where((polari < threshold_polari) & (polari >= -1), 1, 0)
    return flag
