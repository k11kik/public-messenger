import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
from datetime import datetime
import os
from common import cdf, path, distribution, display


def plot_dist(
        cdf_filepath,
        savefig=None,
        suptitle=None,
        zlabel_rmlt=None,
        zlabel_rmlat=None,
):
    mesh_theta_rmlt = cdf.get_data(cdf_filepath, 'mesh_theta_rmlt')
    mesh_r_rmlt = cdf.get_data(cdf_filepath, 'mesh_r_rmlt')
    rmlt_grid = cdf.get_data(cdf_filepath, 'rmlt_grid')
    mesh_theta_rmlat = cdf.get_data(cdf_filepath, 'mesh_theta_rmlat')
    mesh_r_rmlat = cdf.get_data(cdf_filepath, 'mesh_r_rmlat')
    rmlat_grid = cdf.get_data(cdf_filepath, 'rmlat_grid')

    # plot
    fig, axes = plt.subplots(1, 2, subplot_kw={'projection': 'polar'}, figsize=(12, 8))
    if suptitle is not None:
        fig.suptitle(suptitle)

    # マスク処理：duration=0 をマスクして灰色に
    masked_rmlt = ma.masked_where(rmlt_grid == 0, rmlt_grid)
    masked_rmlat = ma.masked_where(rmlat_grid == 0, rmlat_grid)

    # カラーマップ：ゼロのところは灰色に
    cmap = plt.get_cmap('viridis').copy()
    cmap.set_bad(color='lightgray')  # マスク部分を灰色に

    # (r, mlt)
    if zlabel_rmlt is None:
        zlabel_rmlt = 'Dwell time [s]'
    pcm0 = axes[0].pcolormesh(mesh_theta_rmlt, mesh_r_rmlt, masked_rmlt, shading='auto', cmap=cmap)
    fig.colorbar(
        pcm0, ax=axes[0], label=zlabel_rmlt,
        orientation='horizontal', pad=0.15, fraction=0.046,
    )

    # supress automatical tick labels
    axes[0].set_xticklabels([])
    axes[0].set_yticklabels([])
    # add MLT labels
    axes[0].text(90 * np.pi / 180, 8.4, '06 MLT', fontsize=10, ha='center', va='center', color='black')
    axes[0].text(180 * np.pi / 180, 8.4, '12 MLT', fontsize=10, ha='center', va='center', color='black', rotation=90)
    axes[0].text(270 * np.pi / 180, 8.4, '18 MLT', fontsize=10, ha='center', va='center', color='black', rotation=180)
    axes[0].text(360 * np.pi / 180, 8.4, '24 MLT', fontsize=10, ha='center', va='center', color='black', rotation=-90)

    # oplot earth
    theta2 = np.linspace(-np.pi / 2, np.pi / 2, 100)  # 0-180 deg
    r = theta2 * 0 + 1  # radius = 1
    axes[0].fill(theta2, r, color='black', alpha=1.0)  # fill the semicircle

    # (r, mlat)
    pcm1 = axes[1].pcolormesh(mesh_theta_rmlat, mesh_r_rmlat, masked_rmlat, shading='auto', cmap=cmap)

    if zlabel_rmlat is None:
        zlabel_rmlat = 'Dwell time [s]'
    fig.colorbar(
        pcm1, ax=axes[1], label=zlabel_rmlat,
        orientation='horizontal', pad=0.15, fraction=0.046
    )

    # [-90°, 90°]だけに制限
    axes[1].set_thetamin(-90)
    axes[1].set_thetamax(90)

    axes[1].text(0, 9.5, 'MLAT', fontsize=10, ha='center', va='center', color='black')

    # 地球を黒く塗る
    # theta2 = np.linspace(-np.pi / 2, np.pi / 2, 100)
    # r_earth = np.ones_like(theta2) * 1  # radius=1
    # ax.fill(theta2, r_earth, color='black', alpha=1.0)

    path.savefig(savefig)

    return


def plot_dist_cdf_files(
        list_cdf_filepaths,
        savefig=None,
        suptitle=None,
        zlabel_rmlt=None,
        zlabel_rmlat=None,
        info=True
):
    # check cdf file paths
    paths = sorted(list_cdf_filepaths)

    # 存在しないfile pathを削除
    path_not_exist = []
    for i, filepath in enumerate(paths):
        if not os.path.exists(filepath):
            path_not_exist.append(filepath)
            display.warning('_plot/plot_dist_cdf_files', f'the file does not exist: {filepath}')

    [paths.remove(i) for i in path_not_exist]
    list_cdf_filepaths = paths

    if len(list_cdf_filepaths) == 0:
        display.error('_plot/plot_dist_cdf_files', 'No cdf file to read')
        return None

    else:
        print(f"number of cdf files to read: {len(list_cdf_filepaths)}")

    ref_cdf_filepath = list_cdf_filepaths[0]
    mesh_theta_rmlt = cdf.get_data(ref_cdf_filepath, 'mesh_theta_rmlt')
    mesh_r_rmlt = cdf.get_data(ref_cdf_filepath, 'mesh_r_rmlt')
    rmlt_grid = cdf.get_data(ref_cdf_filepath, 'rmlt_grid')
    mesh_theta_rmlat = cdf.get_data(ref_cdf_filepath, 'mesh_theta_rmlat')
    mesh_r_rmlat = cdf.get_data(ref_cdf_filepath, 'mesh_r_rmlat')
    rmlat_grid = cdf.get_data(ref_cdf_filepath, 'rmlat_grid')
    
    loop_start_time = datetime.now()
    for i, cdf_filepath in enumerate(list_cdf_filepaths):
        if info:
            display.progress_bar(i, len(list_cdf_filepaths), loop_start_time)
        rmlt_grid_i = cdf.get_data(cdf_filepath, 'rmlt_grid')
        rmlat_grid_i = cdf.get_data(cdf_filepath, 'rmlat_grid')

        rmlt_grid = rmlt_grid + rmlt_grid_i
        rmlat_grid = rmlat_grid + rmlat_grid_i
    
    distribution.plot_rmlatmlt(
        mesh_theta_rmlt,
        mesh_r_rmlt,
        rmlt_grid,
        mesh_theta_rmlat,
        mesh_r_rmlat,
        rmlat_grid,
        savefig=savefig,
        suptitle=suptitle,
        zlabel_rmlt=zlabel_rmlt,
        zlabel_rmlat=zlabel_rmlat
    )

    return
