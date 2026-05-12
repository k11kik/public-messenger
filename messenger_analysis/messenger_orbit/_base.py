import numpy as np
from common import orbit

def mso_to_rmlatmlt(mso_data: np.ndarray) -> np.ndarray:
    """
    水星のMSO座標系での位置データをR, MLAT, MLTに変換します。
    
    仮定:
    - 磁気双極子軸はMSO座標系のz軸と一致する。
    - MLTの0時はMSO座標系のx軸と一致する。
    
    Parameters
    ----------
    mso_data : np.ndarray
        水星のMSO座標系での位置データ。形状は (n_times, 3) で、
        各列が (x_mso, y_mso, z_mso) に対応。
        
    Returns
    -------
    np.ndarray
        変換されたデータ。形状は (n_times, 3) で、
        各列が (R, MLAT, MLT) に対応。
    """
    if mso_data.ndim != 2 or mso_data.shape[1] != 3:
        raise ValueError("mso_data must be a 2D numpy array with 3 columns.")

    # 1. xyz -> polar 変換
    # MSOのx, y, z成分は、磁気座標系のx_mag, y_mag, z_magと一致すると仮定
    r_mag, theta_mag, phi_mag = orbit.xyz_to_polar(
        mso_data[:, 0], # x_mso -> x_mag
        mso_data[:, 1], # y_mso -> y_mag
        mso_data[:, 2]  # z_mso -> z_mag
    )

    # 2. R (半径)
    # xyz_to_polar関数で計算されたradiusがRに相当
    R = r_mag

    # 3. MLAT (磁気緯度) の計算
    # MLAT = 90° - theta (極角)
    # theta_magはラジアンなので、度数に変換
    mlat_deg = 90.0 - np.rad2deg(theta_mag)

    # 4. MLT (磁気地方時) の計算
    # MLTは phi_mag (方位角) から計算
    # phi_magは -pi から +pi の範囲（-180°から +180°）
    # 1時間は15°なので、度数に変換して15で割る
    phi_deg = np.rad2deg(phi_mag)
    mlt_hours = phi_deg / 15.0

    # MLTを0-24時間の範囲に変換
    # -12時間から+12時間なので、マイナスの場合は+24する
    mlt_hours = np.where(mlt_hours < 0, mlt_hours + 24.0, mlt_hours)

    # 5. 結果を一つの配列に結合
    return np.stack([R, mlat_deg, mlt_hours], axis=1)


def mso_to_polar(
        mso_data,  # (n, 3)
):
    rmlatmlt = mso_to_rmlatmlt(mso_data)
    return
