# import warnings
# warnings.filterwarnings('ignore', message='.*OpenSSL.*', category=UserWarning)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
# import struct
import os
# import zipfile
# import tempfile
from pathlib import Path
# import json
import time
# import re
from urllib.parse import urljoin, urlparse
# from bs4 import BeautifulSoup, Tag
# import requests
# import concurrent.futures
# import threading
# from tqdm import tqdm
# import pytplot
from glob import glob

from messenger_analysis import getdata, messenger_orbit, analysis, ql, event_search, horizons
from common import cdf, pytplot, git, quant, spec, data_process, orbit, display, coordinate, gmail, time, util, security, path, csv, mathpy, pydistplot, distribution
# from erg_analysis import cdf, plot

from messenger_analysis.main_analysis import (
    distribution_freq_over_fcp,
    plot_distribution_freq_over_fcp
)
from messenger_analysis.config import CONFIG
ROOT = CONFIG['root']
DATA = CONFIG['data']
MAIN_DIR = CONFIG['main_dir']


github_token = security.github_token
    
# ------------------------------------------------------------
# download/update module
# ------------------------------------------------------------
def git_download():
    def git_download_0(confirm=True):
        git.download_github(
            owner='k11kik',
            repo='Messenger',
            branch='main',
            remote_path='messenger_analysis',
            is_dir=True,
            github_token=github_token,
            confirm=confirm
        )
        return
    
    def git_download_1(confirm=True):
        git.download_github(
            owner='k11kik',
            repo='Common',
            branch='main',
            remote_path='common',
            is_dir=True,
            github_token=github_token,
            confirm=confirm
        )
        return

    def git_download_2(confirm=True):
        git.download_github(
            owner='k11kik',
            repo='Messenger',
            branch='main',
            remote_path='MessengerAnalysis.py',
            is_dir=False,
            github_token=github_token,
            confirm=confirm
        )
        return
    
    print('[Download from GitHub] Select the number:')
    print(' 0: messenger_analysis')
    print(' 1: common')
    print(' 2: this file')
    print(' 99: all')
    print(' n: canceled')
    input_num = input()
    if input_num == '0':
        git_download_0()
        
    elif input_num == '1':
        git_download_1()
        
    elif input_num == '2':
        git_download_2()
    
    elif input_num == '99':
        ans = input("Download all? [Y/n]: ").strip().lower()
        if ans not in ['', 'y']:
            print("Upload cancelled.")
        
        git_download_0(confirm=False)
        git_download_1(confirm=False)
        git_download_2(confirm=False)

    elif input_num == 'n':
        print('Canceled')
        return
    else:
        raise ValueError(f'Invalid input number: {input_num}')
    return


def git_upload():
    def git_upload_0(confirm=True):
        git.upload_github(
            owner='k11kik',
            repo='Messenger',
            branch='main',
            local_path='messenger_analysis',
            remote_path='messenger_analysis',
            is_dir=True,
            github_token=github_token,
            confirm=confirm
        )
        return
    
    def git_upload_1(confirm=True):
        git.upload_github(
            owner='k11kik',
            repo='Common',
            branch='main',
            local_path='common',
            remote_path='common',
            is_dir=True,
            github_token=github_token,
            confirm=confirm
        )
        return
    
    def git_upload_2(confirm=True):
        git.upload_github(
            owner='k11kik',
            repo='Messenger',
            branch='main',
            local_path='MessengerAnalysis.py',
            remote_path='',
            is_dir=False,
            github_token=github_token,
            confirm=confirm
        )
        return
    

    print('[Upload from GitHub] Select the number:')
    print(' 0: messenger_analysis')
    print(' 1: common')
    print(' 2: this file')
    print(' 99: all')
    print(' n: canceled')
    input_num = input()
    if input_num == '0':
        git_upload_0()
    elif input_num == '1':
        git_upload_1()
    elif input_num == '2':
        git_upload_2()
    elif input_num == '99':
        ans = input("Upload all? [Y/n]: ").strip().lower()
        if ans not in ['', 'y']:
            print("Upload cancelled.")
        
        git_upload_0(confirm=False)
        git_upload_1(confirm=False)
        git_upload_2(confirm=False)
    elif input_num == 'n':
        print('Canceled')
        return
    else:
        raise ValueError(f'Invalid input number: {input_num}')
    return


def git_upload_public():
    def git_upload_0(confirm=True):
        git.upload_github(
            owner='k11kik',
            repo='public-messenger',
            branch='main',
            local_path='messenger_analysis',
            remote_path='messenger_analysis',
            is_dir=True,
            github_token=github_token,
            confirm=confirm
        )
        return
    
    def git_upload_1(confirm=True):
        git.upload_github(
            owner='k11kik',
            repo='public-messenger',
            branch='main',
            local_path='common',
            remote_path='common',
            is_dir=True,
            github_token=github_token,
            confirm=confirm
        )
        return
    
    def git_upload_2(confirm=True):
        git.upload_github(
            owner='k11kik',
            repo='public-messenger',
            branch='main',
            local_path='MessengerAnalysis.py',
            remote_path='',
            is_dir=False,
            github_token=github_token,
            confirm=confirm
        )
        return
    

    print('[Upload from GitHub] Select the number:')
    print(' 0: messenger_analysis')
    print(' 1: common')
    print(' 2: this file')
    print(' 99: all')
    print(' n: canceled')
    input_num = input()
    if input_num == '0':
        git_upload_0()
    elif input_num == '1':
        git_upload_1()
    elif input_num == '2':
        git_upload_2()
    elif input_num == '99':
        ans = input("Upload all? [Y/n]: ").strip().lower()
        if ans not in ['', 'y']:
            print("Upload cancelled.")
        
        git_upload_0(confirm=False)
        git_upload_1(confirm=False)
        git_upload_2(confirm=False)
    elif input_num == 'n':
        print('Canceled')
        return
    else:
        raise ValueError(f'Invalid input number: {input_num}')
    return



# --------------------------------------------------------
# download data
# --------------------------------------------------------

def main_download():
    trange = ['2011-03-23 00:00:00', '2011-03-24 00:00:00']
    getdata.download_mag_mso(
        trange,
        download_dir='',
    )


    # convert tab to cdf by giving filepath (for files not downloaded completely)
    # -------
    # getdata.convert_tab_to_cdf_mag_mso(
    #     '/Users/kikuchiriku/Python/messenger/messenger_data/mag_mso/2015/03/MAGMSOSCI15073_V08.TAB'
    # )
    # -------



    # data_dir = '/Volumes/SSD-PGCU3C/messenger/messenger_data'
    # data_dir = 'test_download'
    # max_workers = 1
    
    # デバッグ用：URLの構築を確認
    # print("=== デバッグ情報 ===")
    # from messenger_analysis.getdata.download import MessengerDataDownloader
    # downloader = MessengerDataDownloader()
    
    # # 最初の数日間のURLを確認
    # from datetime import datetime
    # start_date = datetime.strptime(trange[0], '%Y-%m-%d %H:%M:%S')
    # for i in range(5):  # 最初の5日間を確認
    #     test_date = start_date + timedelta(days=i)
    #     url = downloader.construct_download_url_from_date(test_date)
    #     print(f"{test_date.strftime('%Y-%m-%d')}: {url}")
    
    # 新しいtrange形式の関数を使用
    # getdata.download_messenger_data(trange, data_dir, max_workers=max_workers, info=True, use_parallel=False, update_cdf=True)
    
    # if success:
    #     print("ダウンロードが完了しました")
    # else:
    #     print("ダウンロードに失敗しました")
    
    return


# -------------------------------------------------------------
# ql
# -------------------------------------------------------------
def ql_spectrogram():
    ql.spectrogram(
        ['2012-04-14 20:00:00', '2012-04-15 00:00:00'],
        # parent_dir_save_png=r'E:\messenger'
    )

    sender = gmail.GmailSender()
    sender_email = 'kikuchi.riku.s2@dc.tohoku.ac.jp'
    receiver_email = 'kikuchi.riku.s2@dc.tohoku.ac.jp'
    subject = '[MessengerAnalysis] QL Spectrogram Finished'
    body = 'Messenger Analysis.py\n' + '-----------------------\n' + 'ql_spectrogram successfully finished'

    if sender.service:
        sender.send_message(
            sender_email,
            receiver_email,
            subject,
            body
        )
    return


def ql_specpolari():
    if __name__ == '__main__':
        ql.specpolari(
            ['2008-10-01 00:00:00', '2011-03-01 00:00:00'],
            use_parallel=False,
            parent_dir_save_png=r"D:\messenger",
        )

        ql.specpolari(
            ['2011-03-01 00:00:00', '2015-05-01 00:00:00'],
            use_parallel=False,
            parent_dir_save_png=r"D:\messenger",
        )


def ql_polarization():
    from messenger_analysis.ql.polari import polarization

    # win
    basedir_mag_mso = r"E:\messenger\messenger_data\pl1\mag_mso"
    basedir_orb = r"E:\messenger\messenger_data\pl2\orb"
    basedir_savefig = r"E:\messenger\ql\mag\2h\polarization"

    # mac
    # basedir_mag_mso = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso'
    # basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'
    # basedir_savefig = '/Volumes/SSD4T/messenger/ql/mag/2h/polarization'

    trange = ['2011-03-23 00:00:00', '2015-05-01 00:00:00']
    polarization(
        trange,
        basedir_mag_mso=basedir_mag_mso,
        basedir_orb=basedir_orb,
        basedir_savefig=basedir_savefig
    )


# -------------------------------------------------------------
# Orbit
# -------------------------------------------------------------
def create_orb():
    from messenger_analysis.analysis.create_orb import create_orb_data

    trange = ['2008-01-01 00:00:00', '2015-05-01 00:00:00']
    create_orb_data(
        trange,
        basedir_mag_mso='/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso',
        basedir_savecdf='/Volumes/SSD-PGCU3C/messenger/messenger_data/orb'
    )
    return

def create_reference_dwell_time():
    """
    ref_dwell_fine:
        low resolution
            r_bins = np.arange(1, 7+.5, .5)
            mlt_bins = np.arange(0, 24+1, 1)
            mlat_bins = np.arange(-90, 90+5, 5)

        high resolution
            r_bins = np.arange(1, 7+.1, .1)
            mlt_bins = np.arange(0, 24+.2, .2)
            mlat_bins = np.arange(-90, 90+1, 1)

    """
    from messenger_analysis.distribution._dwell_time import (
        create_ref_dwell_cdf
    )

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'
    r_bins = np.arange(1, 7+.1, .1)
    mlt_bins = np.arange(0, 24+.2, .2)
    mlat_bins = np.arange(-90, 90+1, 1)
    # ----------------------------------

    # rmlat_whole = True
    create_ref_dwell_cdf(
        trange,
        basedir_orb=basedir_orb,
        basedir_savecdf='/Volumes/SSD4T/messenger/messenger_data_analysis/orb/ref_dwell_rmlat_whole_6s/highres/1month',
        # parent_dir_save_cdf='/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis',
        savename='ref_dwell_rmlat_whole_6s',
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        rmlat_whole=True,
        delta_t_sec=6
    )

    # rmlat_whole = False
    # create_ref_dwell_cdf(
    #     ['2011-03-01 00:00:00', '2011-08-01 00:00:00'],
    #     parent_dir_save_cdf='/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis',
    #     savename='ref_dwell',
    #     r_bins=r_bins,
    #     mlt_bins=mlt_bins,
    #     mlat_bins=mlat_bins,
    #     rmlat_whole=False
    # )
    
    return


def dwell_time():
    from messenger_analysis.distribution._dwell_time import (
        get_trange_list_from_csvs,
        get_dwell_time_trange_list,
        get_dwell_time_trange_with_ref
    )
    from common.distribution import plot_rmlatmlt

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'

    # bins setting
    # lowres
    # r_bins = np.arange(1, 7+.5, .5)
    # mlt_bins = np.arange(0, 24+1, 1)
    # mlat_bins = np.arange(-90, 90+5, 5)
    # highres
    r_bins = np.arange(1, 7+.1, .1)
    mlt_bins = np.arange(0, 24+.2, .2)
    mlat_bins = np.arange(-90, 90+1, 1)

    # ------------------------------------------
    # event time distribution
    # ------------------------------------------
    # # newly create cdf
    # csv_filelist = []
    # base_dir = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/emic_event/'
    # basedir_orb = '/Volumes/SSD-PGCU3C/messenger/messenger_data/orb'
    # time_list = util.make_time_list(trange, 1, 'months')
    # for time_list_i in time_list:
    #     dt_start = time.convert(time_list_i[0], frm='str', into='datetime')
    #     year = dt_start.year
    #     month = dt_start.month
    #     csv_filepath = os.path.join(base_dir, f'{year}/emic_event_{year:04}{month:02}.csv')
    #     csv_filelist.append(csv_filepath)
    # trange_list = get_trange_list_from_csvs(csv_filelist)

    # # dwell time in event list
    # dict_orb_meshgrid_event = get_dwell_time_trange_list(
    #     trange_list,
    #     basedir_orb,
    #     r_bins=r_bins,
    #     mlt_bins=mlt_bins,
    #     mlat_bins=mlat_bins,
    #     rmlat_whole=True
    # )
    # cdf.dict_to_cdffile(dict_orb_meshgrid_event, 'dist_orb_meshgrid_event.cdf')
    
    # ## read cdf
    # dict_orb_meshgrid_event = cdf.cdffile_to_dict('dist_orb_meshgrid_event.cdf')

    # plot_rmlatmlt(
    #     dict_orb_meshgrid_event['mesh_theta_rmlt'],
    #     dict_orb_meshgrid_event['mesh_r_rmlt'],
    #     dict_orb_meshgrid_event['rmlt_grid'],
    #     dict_orb_meshgrid_event['mesh_theta_rmlat'],
    #     dict_orb_meshgrid_event['mesh_r_rmlat'],
    #     dict_orb_meshgrid_event['rmlat_grid'],
    #     savefig='out/orb_dwell_time_trange_list.png',
    #     suptitle=f'Dwell time in event lists: {trange=}',
    #     pos_label_rmlat=1,
    #     rmlat_whole=True,
    #     zlabel_rmlt='(R, MLT) dwell time [s]',
    #     zlabel_rmlat='(R, MLAT) dwell time [s]',
    # )

    # plot_rmlatmlt(
    #     dict_orb_meshgrid_event['mesh_theta_rmlt'],
    #     dict_orb_meshgrid_event['mesh_r_rmlt'],
    #     dict_orb_meshgrid_event['rmlt_grid_count'],
    #     dict_orb_meshgrid_event['mesh_theta_rmlat'],
    #     dict_orb_meshgrid_event['mesh_r_rmlat'],
    #     dict_orb_meshgrid_event['rmlat_grid_count'],
    #     savefig='out/orb_dwell_time_trange_list_count.png',
    #     suptitle=f'Dwell time in event lists (count): {trange=}',
    #     pos_label_rmlat=1,
    #     rmlat_whole=True,
    #     zlabel_rmlt='(R, MLT) count',
    #     zlabel_rmlat='(R, MLAT) count',
    # )



    # ------------------------------------------
    # dwell time
    # ------------------------------------------
    # trange = ['2011-03-01 00:00:00', '2013-01-01 00:00:00']
    dict_orb_meshgrid = get_dwell_time_trange_with_ref(
        trange,
        basedir_orb=basedir_orb,
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        # parent_dir_ref_dwell='/Volumes/SSD-PGCU3C/messenger',
        basedir_ref_dwell='/Volumes/SSD4T/messenger/messenger_data_analysis/orb/ref_dwell_rmlat_whole_6s/highres/1month',
        rmlat_whole=True
    )
    display.debug(f'{dict_orb_meshgrid.keys()=}')
    plot_rmlatmlt(
        dict_orb_meshgrid['mesh_theta_rmlt'],
        dict_orb_meshgrid['mesh_r_rmlt'],
        dict_orb_meshgrid['rmlt_grid'],
        dict_orb_meshgrid['mesh_theta_rmlat'],
        dict_orb_meshgrid['mesh_r_rmlat'],
        dict_orb_meshgrid['rmlat_grid'],
        savefig='out/orb_dwell_time_trange.png',
        suptitle=f'Dwell time: {trange=}',
        rmlat_whole=True,
        zlabel_rmlt='(R, MLT) dwell time [s]',
        zlabel_rmlat='(R, MLAT) dwell time [s]',
    )
    plot_rmlatmlt(
        dict_orb_meshgrid['mesh_theta_rmlt'],
        dict_orb_meshgrid['mesh_r_rmlt'],
        dict_orb_meshgrid['rmlt_grid_count'],
        dict_orb_meshgrid['mesh_theta_rmlat'],
        dict_orb_meshgrid['mesh_r_rmlat'],
        dict_orb_meshgrid['rmlat_grid_count'],
        savefig='out/orb_dwell_time_trange_count.png',
        suptitle=f'Dwell time (count): {trange=}',
        rmlat_whole=True,
        zlabel_rmlt='(R, MLT) count',
        zlabel_rmlat='(R, MLAT) count',
    )

    # ------------------------------------------
    # occurence rate
    # ------------------------------------------
    # dict_orb_meshgrid_occ = {}
    # dict_orb_meshgrid_occ['mesh_theta_rmlt'] = dict_orb_meshgrid_event['mesh_theta_rmlt']
    # dict_orb_meshgrid_occ['mesh_r_rmlt'] = dict_orb_meshgrid_event['mesh_r_rmlt']
    # dict_orb_meshgrid_occ['mesh_theta_rmlat'] = dict_orb_meshgrid_event['mesh_theta_rmlat']
    # dict_orb_meshgrid_occ['mesh_r_rmlat'] = dict_orb_meshgrid_event['mesh_r_rmlat']
    # dict_orb_meshgrid_occ['mesh_theta_rmlt'] = dict_orb_meshgrid_event['mesh_theta_rmlt']
    # dict_orb_meshgrid_occ['rmlt_grid'] = dict_orb_meshgrid_event['rmlt_grid'] / dict_orb_meshgrid['rmlt_grid'] * 100
    # dict_orb_meshgrid_occ['rmlat_grid'] = dict_orb_meshgrid_event['rmlat_grid'] / dict_orb_meshgrid['rmlat_grid'] * 100
    # dict_orb_meshgrid_occ['rmlt_grid_count'] = dict_orb_meshgrid_event['rmlt_grid_count'] / dict_orb_meshgrid['rmlt_grid_count'] * 100
    # dict_orb_meshgrid_occ['rmlat_grid_count'] = dict_orb_meshgrid_event['rmlat_grid_count'] / dict_orb_meshgrid['rmlat_grid_count'] * 100
    # plot_rmlatmlt(
    #     dict_orb_meshgrid_occ['mesh_theta_rmlt'],
    #     dict_orb_meshgrid_occ['mesh_r_rmlt'],
    #     dict_orb_meshgrid_occ['rmlt_grid'],
    #     dict_orb_meshgrid_occ['mesh_theta_rmlat'],
    #     dict_orb_meshgrid_occ['mesh_r_rmlat'],
    #     dict_orb_meshgrid_occ['rmlat_grid'],
    #     savefig='out/orb_dwell_time_occ.png',
    #     suptitle=f'Occurrence rate by dwell time: {trange=}',
    #     zlabel_rmlt='(R, MLT) Occurrence rate [%]',
    #     zlabel_rmlat='(R, MLAT) Occurrence rate [%]',
    #     rmlat_whole=True,
    # )
    # plot_rmlatmlt(
    #     dict_orb_meshgrid_occ['mesh_theta_rmlt'],
    #     dict_orb_meshgrid_occ['mesh_r_rmlt'],
    #     dict_orb_meshgrid_occ['rmlt_grid_count'],
    #     dict_orb_meshgrid_occ['mesh_theta_rmlat'],
    #     dict_orb_meshgrid_occ['mesh_r_rmlat'],
    #     dict_orb_meshgrid_occ['rmlat_grid_count'],
    #     savefig='out/orb_dwell_time_occ_count.png',
    #     suptitle=f'Occurrence rate by count: {trange=}',
    #     zlabel_rmlt='(R, MLT) Occurrence rate [%]',
    #     zlabel_rmlat='(R, MLAT) Occurrence rate [%]',
    #     rmlat_whole=True
    # )

    return

# -------- dist - intensity --------
def create_reference_intensity_dist():
    from messenger_analysis.distribution.intensity import (
        create_ref_intensity_dist_cdf
    )

    trange = ['2011-04-01 00:00:00', '2015-05-01 00:00:00']
    # parameters
    # ---------------------------------
    resampling_rate = 20
    average_window_mfa_sec=30
    spec_window_size=1024
    spec_rate_overlap=.9
    average_window_sec = 10
    # bins setting
    r_bins = np.arange(1, 7+.5, .5)
    mlt_bins = np.arange(0, 24+1, 1)
    mlat_bins = np.arange(-90, 90+5, 5)
    # ---------------------------------

    parent_dir_save_cdf = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/dist/intensity/ref_intensity/1month'
    create_ref_intensity_dist_cdf(
        trange,
        parent_dir_save_cdf=parent_dir_save_cdf,
        resampling_rate=resampling_rate,
        average_window_mfa_sec=average_window_mfa_sec,
        spec_window_size=spec_window_size,
        spec_rate_overlap=spec_rate_overlap,
        average_window_sec=average_window_sec,
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        force_create=True
    )

    return


def distribution_intensity():
    from messenger_analysis.distribution.intensity import (
        get_intensity_dist_trange_list,
        get_intensity_dist_trange_with_ref
    )
    from common.distribution import plot_rmlatmlt
    from common.cdf.cdfdata import cdffile_to_dict

    from messenger_analysis.distribution._dwell_time import (
        get_trange_list_from_csvs,
    )

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    # parameters
    # ---------------------------------
    resampling_rate = 20
    average_window_mfa_sec=30
    spec_window_size=1024
    spec_rate_overlap=.9
    average_window_sec = 10
    # bins setting
    r_bins = np.arange(1, 7+.5, .5)
    mlt_bins = np.arange(0, 24+1, 1)
    mlat_bins = np.arange(-90, 90+5, 5)
    # cdf
    outcdf = False
    # ---------------------------------

    # event time distribution
    # ---------------------------------
    # csv_filelist = []
    # base_dir = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/emic_event'
    # time_list = util.make_time_list(trange, 1, 'months')
    # for time_list_i in time_list:
    #     dt_start = time.convert(time_list_i[0], frm='str', into='datetime')
    #     year = dt_start.year
    #     month = dt_start.month
    #     csv_filepath = os.path.join(base_dir, f'{year}/emic_event_{year:04}{month:02}.csv')
    #     csv_filelist.append(csv_filepath)
    # trange_list = get_trange_list_from_csvs(csv_filelist)


    # if outcdf:
    #     savecdf = os.path.join(
    #         '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis', 
    #         'dist/intensity/dist_intensity_trange_list.cdf'
    #     )

    #     dict_intensity_meshgrid = get_intensity_dist_trange_list(
    #         trange_list,
    #         resampling_rate=resampling_rate,
    #         average_window_mfa_sec=average_window_mfa_sec,
    #         spec_window_size=spec_window_size,
    #         spec_rate_overlap=spec_rate_overlap,
    #         average_window_sec=average_window_sec,
    #         r_bins=r_bins,
    #         mlt_bins=mlt_bins,
    #         mlat_bins=mlat_bins,
    #         savecdf=savecdf
    #     )
    
    # else:
    #     dict_intensity_meshgrid = cdffile_to_dict('/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/dist/intensity/dist_intensity_trange_list.cdf')

    # plot_rmlatmlt(
    #     dict_intensity_meshgrid['mesh_theta_rmlt'],
    #     dict_intensity_meshgrid['mesh_r_rmlt'],
    #     dict_intensity_meshgrid['rmlt_intensity_avg'],
    #     dict_intensity_meshgrid['mesh_theta_rmlat'],
    #     dict_intensity_meshgrid['mesh_r_rmlat'],
    #     dict_intensity_meshgrid['rmlat_intensity_avg'],
    #     savefig='out/dist_intensity_trange_list.png',
    #     suptitle=f'Distribution of intensity in event lists: {trange=}',
    #     zlabel_rmlt='Average intensity [$nT^2/Hz$]',
    #     zlabel_rmlat='Average intensity [$nT^2/Hz$]',
    #     pos_label_rmlat=1.8,
    #     zlog=True,
    #     zrange=[1, 1e3],
    #     colormap='jet'
    # )

    # plot_rmlatmlt(
    #     dict_intensity_meshgrid['mesh_theta_rmlt'],
    #     dict_intensity_meshgrid['mesh_r_rmlt'],
    #     dict_intensity_meshgrid['rmlt_count'],
    #     dict_intensity_meshgrid['mesh_theta_rmlat'],
    #     dict_intensity_meshgrid['mesh_r_rmlat'],
    #     dict_intensity_meshgrid['rmlat_count'],
    #     savefig='out/dist_count_trange_list.png',
    #     suptitle=f'Distribution of counts in event lists: {trange=}',
    #     zlabel_rmlt='Counts',
    #     zlabel_rmlat='Counts',
    #     pos_label_rmlat=1.8,
    #     zlog=True,
    #     zrange=[1, 5e4],
    #     colormap='jet'
    # )
    # ---------------------------------

    # intensity with ref
    # ---------------------------------
    dict_intensity_meshgrid_ref = get_intensity_dist_trange_with_ref(
        trange,
        parent_dir_ref='/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/dist/intensity/ref_intensity/1month',
        resampling_rate=resampling_rate,
        average_window_mfa_sec=average_window_mfa_sec,
        spec_window_size=spec_window_size,
        spec_rate_overlap=spec_rate_overlap,
        average_window_sec=average_window_sec,
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
    )

    plot_rmlatmlt(
        dict_intensity_meshgrid_ref['mesh_theta_rmlt'],
        dict_intensity_meshgrid_ref['mesh_r_rmlt'],
        dict_intensity_meshgrid_ref['rmlt_intensity_avg'],
        dict_intensity_meshgrid_ref['mesh_theta_rmlat'],
        dict_intensity_meshgrid_ref['mesh_r_rmlat'],
        dict_intensity_meshgrid_ref['rmlat_intensity_avg'],
        savefig='out/dist_intensity.png',
        suptitle=f'Distribution of intensity in event lists: {trange=}',
        zlabel_rmlt='Average intensity [$nT^2/Hz$]',
        zlabel_rmlat='Average intensity [$nT^2/Hz$]',
        pos_label_rmlat=1.8,
        zrange=[1e-1, 1e2],
        zlog=True,
        colormap='jet'
    )

    plot_rmlatmlt(
        dict_intensity_meshgrid_ref['mesh_theta_rmlt'],
        dict_intensity_meshgrid_ref['mesh_r_rmlt'],
        dict_intensity_meshgrid_ref['rmlt_count'],
        dict_intensity_meshgrid_ref['mesh_theta_rmlat'],
        dict_intensity_meshgrid_ref['mesh_r_rmlat'],
        dict_intensity_meshgrid_ref['rmlat_count'],
        savefig='out/dist_count.png',
        suptitle=f'Distribution of counts in event lists: {trange=}',
        zlabel_rmlt='Counts',
        zlabel_rmlat='Counts',
        pos_label_rmlat=1.8,
        colormap='jet',
        zlog=True
    )
    # ---------------------------------

    return


# -------------------------------------------------------------
# EMIC
# -------------------------------------------------------------
def testrun_flag_emic():
    from messenger_analysis.analysis.create_event_flag import create_event_flag_emic_trange
    from messenger_analysis.detect_band.get_band_flag import get_band_flag

    # trange = ['2011-03-25 00:00:00', '2011-03-25 02:00:00']
    # trange = ['2012-01-01 04:00:00', '2012-01-01 06:00:00']
    trange = ['2011-05-17 08:00:00', '2011-05-17 10:00:00']

    basedir_mag_mso = os.path.join(MAIN_DIR, 'messenger_data/pl1/mag_mso')
    basedir_orb = os.path.join(MAIN_DIR, 'messenger_data/pl2/orb')
    # win
    # basedir_mag_mso = r"E:\messenger\messenger_data\pl1\mag_mso"
    # basedir_orb = r"E:\messenger\messenger_data\pl2\orb"
    # mac
    # basedir_mag_mso = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso'
    # basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'

    # create cdf
    # ------------
    create_event_flag_emic_trange(
        trange,
        basedir_mag_mso=basedir_mag_mso,
        basedir_orb=basedir_orb,
        save_all=True,
        savecdf='test.cdf'
    )
    pytplot.tplot_names()
    # pytplot.del_data()
    # ------------

    # read cdf
    dict_data = cdf.cdffile_to_dict('test.cdf')
    cdf.info('test.cdf')
    display.print_dict(dict_data)

    times = dict_data['times']
    freqs_norm = dict_data['freqs_norm']

    pytplot.store_data('event_flag_psd_intensity', {'x': times, 'y': dict_data['event_flag_psd_intensity'], 'v': freqs_norm})
    pytplot.store_data('event_flag_psd_ratio', {'x': times, 'y': dict_data['event_flag_psd_ratio'], 'v': freqs_norm})
    pytplot.store_data('event_flag_psd', {'x': times, 'y': dict_data['event_flag_psd'], 'v': freqs_norm})
    pytplot.store_data('event_flag_polarization', {'x': times, 'y': dict_data['event_flag_polarization'], 'v': freqs_norm})
    pytplot.store_data('event_flag_wna', {'x': times, 'y': dict_data['event_flag_wna'], 'v': freqs_norm})
    pytplot.store_data('event_flag_planarity', {'x': times, 'y': dict_data['event_flag_planarity'], 'v': freqs_norm})
    pytplot.store_data('event_flag_emic', {'x': times, 'y': dict_data['event_flag_emic'], 'v': freqs_norm})
    pytplot.options('event_flag_psd_intensity', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='PSD intensity flag')
    pytplot.options('event_flag_psd_ratio', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='PSD ratio flag')
    pytplot.options('event_flag_psd', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='PSD flag')
    pytplot.options('event_flag_polarization', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='Polarization flag')
    pytplot.options('event_flag_wna', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='WNA flag')
    pytplot.options('event_flag_planarity', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='Planarity flag')
    pytplot.options('event_flag_emic', yrange=[0, 1.1], colormap='binary', ylabel='f/fcp', zlabel='EMIC flag')
    pytplot.tplot_names()

    pytplot.tplot(
        [
            'event_flag_psd_intensity',
            'event_flag_psd_ratio',
            'event_flag_psd',
            'event_flag_polarization',
            'event_flag_wna',
            'event_flag_planarity',
            'event_flag_emic',
        ],
        figsize=(12, 16),
        delta_xticks=30,
        timeunit_xticks='minutes',
        save_png='out/testrun/flag_emic.png'
    )

    # band flag
    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    n_band = len(freqs_band) - 1

    flag_emic = pytplot.get_data('event_flag_emic').y
    band_flag = get_band_flag(
        flag_emic,
        freqs_norm,
        freqs_band=freqs_band,
        min_continuity=3
    )
    display.debug(f'{band_flag.shape=}')

    vars_tplot_band_flag = ['event_flag_emic']
    # vars_tplot_band_flag = [['event_flag_emic', 'mq23_norm']]
    ylabels = [
        'Na+ flag',
        'O+ flag',
        'Li+ flag',
        'He+ flag',
        'He++ flag',
        'H+ flag',
    ]
    for i in range(n_band):
        band_flag_i = band_flag[:, i]
        pytplot.store_data(f'band_flag_{i}', {'x': times, 'y': band_flag_i})
        pytplot.options(f'band_flag_{i}', yrange=[-0.1, 1.1], ylabel=ylabels[i])
        vars_tplot_band_flag.append(f'band_flag_{i}')
    
    # pytplot.options('event_flag_emic', yrange=[0, 1/16])
    # mq23_norm = 1/23 * np.ones_like(times)
    # pytplot.store_data('mq23_norm', {'x': times, 'y': mq23_norm})
    # pytplot.options('mq23_norm', color='pink', linestyle='dashed')
    pytplot.tplot_names()
    
    pytplot.tplot(
        vars_tplot_band_flag,
        figsize=(12, 16),
        save_png='out/testrun/flag_emic2.png'
    )

    pytplot.options('mag_mfa_x_dpwrspc_psd_norm', zlabel='PSD_perp1')
    pytplot.options('mag_mfa_y_dpwrspc_psd_norm', zlabel='PSD_perp2')
    pytplot.options('mag_mfa_z_dpwrspc_psd_norm', zlabel='PSD_para')
    pytplot.options('polarization_norm', zlabel='Polarization\nellipticity')
    pytplot.options('wna_norm', zlabel='WNA')
    pytplot.options('planarity_norm', zlabel='Planarity')
    pytplot.options('mq1_norm', ylabel='f/fcp')
    pytplot.options('mq1_norm', legend=True, legend_names=['H+'])
    pytplot.tplot(
        [
            ['mag_mfa_x_dpwrspc_psd_norm', 'mq1_norm'],
            ['mag_mfa_y_dpwrspc_psd_norm', 'mq1_norm'],
            ['mag_mfa_z_dpwrspc_psd_norm', 'mq1_norm'],
            ['polarization_norm', 'mq1_norm'],
            ['wna_norm', 'mq1_norm'],
            ['planarity_norm', 'mq1_norm'],
            ['event_flag_emic']
        ],
        figsize=(12, 16),
        # suptitle=suptitle,
        xlim=trange,
        delta_xticks=30,
        timeunit_xticks='minutes',
        save_png='out/testrun/flag_emic3.png',
        var_orbit='orb_rmlatmlt',
        list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]']
    )

    



    return


def emic_event_search():
    trange = ['2011-03-23 00:00:00', '2015-05-01 00:00:00']
    # trange = ['2011-03-31 00:00:00', '2011-04-02 00:00:00']

    analysis.search_emic_events(
        trange,
        output_dir='/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis',
        threshold_psd=1e3,
        threshold_ratio=10,
        threshold_polari=-0.5,
        min_event_delta_time=60,
        min_event_delta_freq=0.1,
        merge_timespan=300,
        send_gmail=False
    )

    return


def create_band_flag_data_in_event():
    from messenger_analysis.analysis.band_flag import create_band_flag_data_event

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    basedir_event = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/emic'
    basedir_savecdf = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/band_flag'
    basedir_mag_cdf = '/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso'
    create_band_flag_data_event(
        trange,
        basedir_event,
        basedir_savecdf,
        basedir_mag_cdf=basedir_mag_cdf
    )
    return


def create_event_flag_emic():
    from messenger_analysis.analysis.create_event_flag import create_event_flag_emic_trange

    trange = ['2011-03-23 00:00:00', '2015-01-01 00:00:00']
    # Windows
    basedir_savecdf = r"E:\messenger\messenger_data_analysis\event\event_flag_emic"
    basedir_mag_mso = r"E:\messenger\messenger_data\pl1\mag_mso"
    basedir_orb = r"E:\messenger\messenger_data\pl2\orb"
    # Mac
    # basedir_savecdf = '/Volumes/SSD4T/messenger/messenger_data_analysis/event/event_flag_emic'
    # basedir_mag_mso = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso'
    # basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'
    # ---------------------

    trange_list = time.make_time_list(trange, 2, 'hours')
    start_time_loop = datetime.now()
    for i, trange_i in enumerate(trange_list):
        try:
            display.progress_bar(i, len(trange_list), start_time_loop)
            pytplot.del_data()
            dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
            year = dt_start_i.year
            month = dt_start_i.month
            day = dt_start_i.day
            hour = dt_start_i.hour
            savecdf = os.path.join(
                basedir_savecdf,
                f'{year:04}',
                f'{month:02}',
                f'messenger_event_flag_emic_{year:04}{month:02}{day:02}{hour:02}.cdf'
            )
            create_event_flag_emic_trange(
                trange_i,
                basedir_mag_mso=basedir_mag_mso,
                basedir_orb=basedir_orb,
                savecdf=savecdf,
            )
        except Exception as e:
            display.error(f'{trange_i=}: {e}')



    return



def collect_event_ql():
    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    basedir_ql = '/Volumes/SSD-PGCU3C/messenger/ql/mag/2h/specpolari_norm'
    basedir_event = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/emic'
    basedir_for_copy = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/emic_ql'

    # ---------
    trange_list = util.make_time_list(trange, 1, 'months')
    for i, trange_i in enumerate(trange_list):
        filepath_ql = None
        dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
        year = dt_start_i.year
        month = dt_start_i.month
        csv_filepath_event = os.path.join(
            basedir_event,
            f'{year:04}',
            f'emic_event_{year:04}{month:02}.csv'
        )
        if not os.path.exists(csv_filepath_event):
            display.warning(f'No csv_event file: {csv_filepath_event}')
            continue

        trange_list_event = csv.get_trange_list(csv_filepath_event)

        for j, trange_j in enumerate(trange_list_event):
            dt_start_j = time.convert(trange_j[0], frm='str', into='datetime')
            year_j = dt_start_j.year
            month_j = dt_start_j.month
            day_j = dt_start_j.day
            hour_j = dt_start_j.hour
            hour_j_ql = (hour_j // 2) * 2
            filepath_search = os.path.join(
                basedir_ql,
                f'{year_j:04}',
                f'{month_j:02}',
                f'messenger_*{year_j:04}{month_j:02}{day_j:02}{hour_j_ql:02}*.png'
            )
            filepath_candidate = glob(filepath_search)
            if len(filepath_candidate) == 0:
                display.warning(f'No existing filepath_search: {filepath_search}')
                continue
            elif len(filepath_candidate) == 1:
                filepath_ql = filepath_candidate[0]
            else:
                display.warning(f'Duplicate filepath_search: {filepath_search} -> Applying the 1st one')
                filepath_ql = filepath_candidate[0]
            
            # copy
            if filepath_ql is not None:
                dir_for_copy = os.path.join(
                    basedir_for_copy,
                    f'{year_j:04}',
                    f'{month_j:02}'
                )
                path.copy_file(
                    filepath_ql,
                    dir_for_copy
                )

    return


def event_distribution_band_flag():
    from common import distribution
    from common.distribution._base import update_dict
    from messenger_analysis.distribution._dwell_time import (
        get_dwell_time_trange_with_ref
    )

    basedir_event_band_flag = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic'
    trange = ['2011-03-01 00:00:00', '2012-04-01 00:00:00']
    r_bins = np.arange(1, 7+.5, .5)
    mlt_bins = np.arange(0, 24+1, 1)
    mlat_bins = np.arange(-90, 90+5, 5)
    freqs_band = [0, 1/23, 1/16, 1/4, 1/2, 1]
    # -----------

    # create cdf
    # ----------------------
    trange_list = util.make_time_list(trange, 1, 'months')
    dict_band_0 = {}
    dict_band_1 = {}
    dict_band_2 = {}
    start_time_loop = datetime.now()
    for i, trange_i in enumerate(trange_list):
        display.progress_bar(i, len(trange_list), start_time_loop, color='yellow')
        display.info(f'{trange_i=}')
        dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
        year = dt_start_i.year
        month = dt_start_i.month
        cdf_filepath_search = os.path.join(
            basedir_event_band_flag,
            f'{year:04}',
            f'{month:02}',
            f'messenger_band_flag_event_{year:04}{month:02}*.cdf'
        )
        cdf_filepaths = glob(cdf_filepath_search)
        start_time_loop_i = datetime.now()
        for j, cdf_filepath in enumerate(cdf_filepaths):
            display.progress_bar(j, len(cdf_filepaths), start_time_loop_i)
            pytplot.del_data()
            display.info(f'cdf filepath: {cdf_filepath}')
            dict_data = cdf.cdffile_to_dict(cdf_filepath)
            pytplot.store_data('band_flag', {'x': dict_data['times'], 'y': dict_data['band_flag']})
            # pytplot.dict_to_tplot(
            #     dict_data,
            #     'times',
            #     [
            #         'band_0_0p25',
            #         'band_0p25_0p5',
            #         'band_0p5_1p0',
            #     ]
            # )

            times = dict_data['times']
            trange = time.convert([times[0], times[-1]], frm='unix', into='str')
            getdata.messenger_orb(trange)
            dat_orb = pytplot.get_data('pos')
            orb = dat_orb.y / 2439.7
            pytplot.store_data('pos', {'x': dat_orb.times, 'y': orb}, replace=True)
            orbit.xyz2polar('pos', to='polar')
            orbit.rmlatmlt2polar('pos_polar', 'pos_rmlatmlt', to='rmlatmlt')

            # interp
            dat_orb_rmlatmlt = pytplot.get_data('pos_rmlatmlt')
            orb_interp = mathpy.interp_vec(times, dat_orb.times, dat_orb_rmlatmlt.y)
            pytplot.store_data('orb_interp', {'x': times, 'y': orb_interp})

            dict_band_0_j = distribution.rmlatmlt_meshgrid(
                'orb_interp',
                datatype='average',
                varname_data='band_0_0p25',
                r_bins=r_bins,
                mlt_bins=mlt_bins,
                mlat_bins=mlat_bins
            )
            dict_band_1_j = distribution.rmlatmlt_meshgrid(
                'orb_interp',
                datatype='average',
                varname_data='band_0p25_0p5',
                r_bins=r_bins,
                mlt_bins=mlt_bins,
                mlat_bins=mlat_bins
            )
            dict_band_2_j = distribution.rmlatmlt_meshgrid(
                'orb_interp',
                datatype='average',
                varname_data='band_0p5_1p0',
                r_bins=r_bins,
                mlt_bins=mlt_bins,
                mlat_bins=mlat_bins
            )

            if not dict_band_0:
                dict_band_0 = dict_band_0_j
                dict_band_1 = dict_band_1_j
                dict_band_2 = dict_band_2_j
            
            else: # update
                dict_band_0 = update_dict(dict_band_0, dict_band_0_j)
                dict_band_1 = update_dict(dict_band_1, dict_band_1_j)
                dict_band_2 = update_dict(dict_band_2, dict_band_2_j)

    # output cdf
    cdf.dict_to_cdffile(
        dict_band_0,
        os.path.join(basedir_event_band_flag, 'dict_band_0.cdf')
    )
    cdf.dict_to_cdffile(
        dict_band_1,
        os.path.join(basedir_event_band_flag, 'dict_band_1.cdf')
    )
    cdf.dict_to_cdffile(
        dict_band_2,
        os.path.join(basedir_event_band_flag, 'dict_band_2.cdf')
    )
    # ----------------------

    # read cdf
    # ----------------------
    dict_band_0 = cdf.cdffile_to_dict(
        os.path.join(basedir_event_band_flag, 'dict_band_0.cdf')
    )
    dict_band_1 = cdf.cdffile_to_dict(
        os.path.join(basedir_event_band_flag, 'dict_band_1.cdf')
    )
    dict_band_2 = cdf.cdffile_to_dict(
        os.path.join(basedir_event_band_flag, 'dict_band_2.cdf')
    )
    
    # ----------------------
    distribution.plot_rmlatmlt(
        dict_band_0['mesh_theta_rmlt'],
        dict_band_0['mesh_r_rmlt'],
        dict_band_0['rmlt_grid'],
        dict_band_0['mesh_theta_rmlat'],
        dict_band_0['mesh_r_rmlat'],
        dict_band_0['rmlat_grid'],
        savefig='out/event_dist_band_flag_0.png',
        suptitle='Event distribution: Band Flag fcp=[0, 0.25]',
    )
    distribution.plot_rmlatmlt(
        dict_band_1['mesh_theta_rmlt'],
        dict_band_1['mesh_r_rmlt'],
        dict_band_1['rmlt_grid'],
        dict_band_1['mesh_theta_rmlat'],
        dict_band_1['mesh_r_rmlat'],
        dict_band_1['rmlat_grid'],
        savefig='out/event_dist_band_flag_1.png',
        suptitle='Event distribution: Band Flag fcp=[0.25, 0.5]',
    )
    distribution.plot_rmlatmlt(
        dict_band_2['mesh_theta_rmlt'],
        dict_band_2['mesh_r_rmlt'],
        dict_band_2['rmlt_grid'],
        dict_band_2['mesh_theta_rmlat'],
        dict_band_2['mesh_r_rmlat'],
        dict_band_2['rmlat_grid'],
        savefig='out/event_dist_band_flag_2.png',
        suptitle='Event distribution: Band Flag fcp=[0.5, 1]',
    )

    # Dwell time (whole period)
    dict_orb_meshgrid = get_dwell_time_trange_with_ref(
        trange,
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        # parent_dir_ref_dwell='/Volumes/SSD-PGCU3C/messenger',
        basedir_ref_dwell='/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/orb/ref_dwell_rmlat_whole/1month',
        rmlat_whole=True
    )
    distribution.plot_rmlatmlt_dict(
        dict_orb_meshgrid,
        savefig='out/test/orb_dwell_time.png'
    )

    # Occurrence rate
    dict_band_occ_0 = dict_band_0.copy()
    dict_band_occ_0['rmlt_grid'] = dict_band_0['rmlt_grid'] * dict_band_0['rmlt_grid_count'] / dict_orb_meshgrid['rmlt_grid_count'] * 100
    dict_band_occ_0['rmlat_grid'] = dict_band_0['rmlat_grid'] * dict_band_0['rmlat_grid_count'] / dict_orb_meshgrid['rmlat_grid_count'] * 100
    
    dict_band_occ_1 = dict_band_1.copy()
    dict_band_occ_1['rmlt_grid'] = dict_band_1['rmlt_grid'] * dict_band_1['rmlt_grid_count'] / dict_orb_meshgrid['rmlt_grid_count'] * 100
    dict_band_occ_1['rmlat_grid'] = dict_band_1['rmlat_grid'] * dict_band_1['rmlat_grid_count'] / dict_orb_meshgrid['rmlat_grid_count'] * 100
    
    dict_band_occ_2 = dict_band_2.copy()
    dict_band_occ_2['rmlt_grid'] = dict_band_2['rmlt_grid'] * dict_band_2['rmlt_grid_count'] / dict_orb_meshgrid['rmlt_grid_count'] * 100
    dict_band_occ_2['rmlat_grid'] = dict_band_2['rmlat_grid'] * dict_band_2['rmlat_grid_count'] / dict_orb_meshgrid['rmlat_grid_count'] * 100

    distribution.plot_rmlatmlt(
        dict_band_occ_0['mesh_theta_rmlt'],
        dict_band_occ_0['mesh_r_rmlt'],
        dict_band_occ_0['rmlt_grid'],
        dict_band_occ_0['mesh_theta_rmlat'],
        dict_band_occ_0['mesh_r_rmlat'],
        dict_band_occ_0['rmlat_grid'],
        savefig='out/event_dist_band_flag_occ_0.png',
        suptitle='Event distribution (Occurrence rate): Band Flag fcp=[0, 0.25]',
    )
    distribution.plot_rmlatmlt(
        dict_band_occ_1['mesh_theta_rmlt'],
        dict_band_occ_1['mesh_r_rmlt'],
        dict_band_occ_1['rmlt_grid'],
        dict_band_occ_1['mesh_theta_rmlat'],
        dict_band_occ_1['mesh_r_rmlat'],
        dict_band_occ_1['rmlat_grid'],
        savefig='out/event_dist_band_flag_occ_1.png',
        suptitle='Event distribution (Occurrence rate): Band Flag fcp=[0.25, 0.5]',
    )
    distribution.plot_rmlatmlt(
        dict_band_occ_2['mesh_theta_rmlt'],
        dict_band_occ_2['mesh_r_rmlt'],
        dict_band_occ_2['rmlt_grid'],
        dict_band_occ_2['mesh_theta_rmlat'],
        dict_band_occ_2['mesh_r_rmlat'],
        dict_band_occ_2['rmlat_grid'],
        savefig='out/event_dist_band_flag_occ_2.png',
        suptitle='Event distribution (Occurrence rate): Band Flag fcp=[0.5, 1.0]',
    )

    
    # count
    distribution.plot_rmlatmlt(
        dict_band_0['mesh_theta_rmlt'],
        dict_band_0['mesh_r_rmlt'],
        dict_band_0['rmlt_grid_count'],
        dict_band_0['mesh_theta_rmlat'],
        dict_band_0['mesh_r_rmlat'],
        dict_band_0['rmlat_grid_count'],
        savefig='out/event_dist_band_flag_0_count.png',
        suptitle='Event distribution (count): Band Flag fcp=[0, 0.25]'
    )
    distribution.plot_rmlatmlt(
        dict_band_1['mesh_theta_rmlt'],
        dict_band_1['mesh_r_rmlt'],
        dict_band_1['rmlt_grid_count'],
        dict_band_1['mesh_theta_rmlat'],
        dict_band_1['mesh_r_rmlat'],
        dict_band_1['rmlat_grid_count'],
        savefig='out/event_dist_band_flag_1_count.png',
        suptitle='Event distribution (count): Band Flag fcp=[0.25, 0.5]'
    )
    distribution.plot_rmlatmlt(
        dict_band_2['mesh_theta_rmlt'],
        dict_band_2['mesh_r_rmlt'],
        dict_band_2['rmlt_grid_count'],
        dict_band_2['mesh_theta_rmlat'],
        dict_band_2['mesh_r_rmlat'],
        dict_band_2['rmlat_grid_count'],
        savefig='out/event_dist_band_flag_2_count.png',
        suptitle='Event distribution (count): Band Flag fcp=[0.5, 1]'
    )
    # total
    dict_band_total = {
        'mesh_theta_rmlt': dict_band_0['mesh_theta_rmlt'],
        'mesh_r_rmlt': dict_band_0['mesh_r_rmlt'],
        'mesh_theta_rmlat': dict_band_0['mesh_theta_rmlat'],
        'mesh_r_rmlat': dict_band_0['mesh_r_rmlat'],
        'rmlt_grid': np.zeros_like(dict_band_0['rmlt_grid']),
        'rmlt_grid_count': np.zeros_like(dict_band_0['rmlt_grid_count']),
        'rmlat_grid': np.zeros_like(dict_band_0['rmlat_grid']),
        'rmlat_grid_count': np.zeros_like(dict_band_0['rmlat_grid_count']),
    }
    for dict_band_i in [dict_band_0, dict_band_1, dict_band_2]:
        dict_band_total = update_dict(dict_band_total, dict_band_i)
    distribution.plot_rmlatmlt(
        dict_band_total['mesh_theta_rmlt'],
        dict_band_total['mesh_r_rmlt'],
        dict_band_total['rmlt_grid'],
        dict_band_total['mesh_theta_rmlat'],
        dict_band_total['mesh_r_rmlat'],
        dict_band_total['rmlat_grid'],
        savefig='out/event_dist_band_flag_total.png',
        suptitle='Event distribution: Band Flag fcp=[0, 1]',
    )

    dict_band_occ_total = dict_band_total.copy()
    dict_band_occ_total['rmlt_grid'] = dict_band_total['rmlt_grid'] * dict_band_total['rmlt_grid_count'] / dict_orb_meshgrid['rmlt_grid_count'] * 100
    dict_band_occ_total['rmlat_grid'] = dict_band_total['rmlat_grid'] * dict_band_total['rmlat_grid_count'] / dict_orb_meshgrid['rmlat_grid_count'] * 100
    distribution.plot_rmlatmlt_dict(
        dict_band_occ_total,
        savefig='out/event_dist_band_flag_occ_total.png',
    )
    

    return


def create_band_flag_from_event_flag_emic():
    from common import distribution
    from messenger_analysis.analysis.band_flag import create_band_flag_data_from_event_flag_emic

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    # mac
    # basedir_event_flag_emic = '/Volumes/SSD4T/messenger/messenger_data_analysis/event/event_flag_emic'
    # basedir_savecdf = '/Volumes/SSD4T/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic'
    # win
    basedir_event_flag_emic = r"E:\messenger\messenger_data_analysis\event\event_flag_emic"
    basedir_savecdf = r"E:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic"

    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]

    create_band_flag_data_from_event_flag_emic(
        trange,
        basedir_event_flag_emic=basedir_event_flag_emic,
        basedir_savecdf=basedir_savecdf,
        freqs_band=freqs_band
    )
    return


def create_distribution_band_flag_from_event_flag_emic():
    import gc
    from common.distribution._base import update_dict, calculate_time_intervals, update_dict_sum

    res_mode = 'high' # 'high', 'low'

    # ディレクトリ設定 (環境に合わせて適宜変更)
    basedir_band_flag = r"E:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic"
    basedir_save_dict_band = fr"E:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic\{res_mode}"
    basedir_orb = r"E:\messenger\messenger_data\pl2\orb"

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    
    # ビン設定
    if res_mode == 'low':
        r_bins = np.arange(1, 7.5, .5)
        mlt_bins = np.arange(0, 25, 1)
        mlat_bins = np.arange(-90, 95, 5)
    elif res_mode == 'high':
        r_bins = np.arange(1, 7.1, .1)
        mlt_bins = np.arange(0, 24.2, .2)
        mlat_bins = np.arange(-90, 91, 1)

    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    n_band = len(freqs_band) - 1

    def initialize_dict():
        d = {'total': {}, 'dwell_time': {}}
        for i in range(n_band):
            d[f'band{i}'] = {}
        return d

    def save_monthly_data(d, year, month):
        """月ごとに各キーをCDF保存する"""
        if year is None or month is None: return
        for key, val in d.items():
            if val:
                file_name = f'dict_{key}_{year:04}{month:02}.cdf'
                out_path = os.path.join(basedir_save_dict_band, file_name)
                cdf.dict_to_cdffile(val, out_path)

    # メインループ
    trange_list = time.make_time_list(trange, 2, 'hours')
    dict_band = initialize_dict()
    current_year = None
    current_month = None

    start_time_loop = datetime.now()
    for i, trange_i in enumerate(trange_list):
        pytplot.del_data(silent=True)
        display.progress_bar(i, len(trange_list), start_time_loop, level='WARNING')
        
        dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
        year, month = dt_start_i.year, dt_start_i.month
        
        # 月が変わったら保存してリセット
        if current_month is not None and (month != current_month or year != current_year):
            save_monthly_data(dict_band, current_year, current_month)
            dict_band = initialize_dict()
            gc.collect()

        current_year, current_month = year, month

        # データの読み込み
        day, hour = dt_start_i.day, dt_start_i.hour
        cdf_filepath_search = os.path.join(
            basedir_band_flag, f'{year:04}', f'{month:02}',
            f'messenger_band_flag_{year:04}{month:02}{day:02}{hour:02}*.cdf'
        )
        cdf_filepath = path.glob_one(cdf_filepath_search)
        if cdf_filepath is None: continue
        
        dict_data = cdf.cdffile_to_dict(cdf_filepath)
        times = dict_data['times']
        
        # 軌道データ取得と補間
        trange_data = time.convert([times[0], times[-1]], frm='unix', into='str')
        getdata.messenger_orb(trange_data, basedir_orb)
        dat_orb_rmlatmlt = pytplot.get_data('orb_rmlatmlt')
        if dat_orb_rmlatmlt is None: continue
        
        orb_interp = mathpy.interp_vec(times, dat_orb_rmlatmlt.times, dat_orb_rmlatmlt.y)
        pytplot.store_data('orb_interp', {'x': times, 'y': orb_interp})

        # 時間間隔の計算
        dts = calculate_time_intervals(times)
        pytplot.store_data('dts_val', {'x': times, 'y': dts})

        # Dwell Time 集計
        dict_dwell_i = distribution.rmlatmlt_meshgrid(
            'orb_interp', datatype='orbit', varname_data='dts_val',
            r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins
        )
        dict_band['dwell_time'] = update_dict_sum(dict_band['dwell_time'], dict_dwell_i)

        # Band-specific 集計
        for j in range(n_band):
            band_flag_j = dict_data['band_flag'][:, j]
            pytplot.store_data('dts_is_flag', {'x': times, 'y': dts * band_flag_j}, replace=True)

            dict_mesh_j = distribution.rmlatmlt_meshgrid(
                'orb_interp', datatype='orbit', varname_data='dts_is_flag',
                r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins
            )
            dict_band[f'band{j}'] = update_dict_sum(dict_band[f'band{j}'], dict_mesh_j)

        # Total 集計
        total_flag = np.any(dict_data['band_flag'] == 1, axis=1).astype(float)
        pytplot.store_data('dts_is_total', {'x': times, 'y': dts * total_flag}, replace=True)
        dict_total_i = distribution.rmlatmlt_meshgrid(
            'orb_interp', datatype='orbit', varname_data='dts_is_total',
            r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins
        )
        dict_band['total'] = update_dict_sum(dict_band['total'], dict_total_i)
        
        del dict_data, times, dts, orb_interp, dict_dwell_i, dict_total_i

    # 最後の月を保存
    if current_month is not None:
        save_monthly_data(dict_band, current_year, current_month)

    return

def _create_distribution_band_flag_from_event_flag_emic():
    import gc
    from common.distribution._base import update_dict, calculate_time_intervals, update_dict_sum

    res_mode = 'high' # 'high', 'low'

    # mac
    # basedir_band_flag = '/Volumes/SSD4T/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic'
    # basedir_save_dict_band = f'/Volumes/SSD4T/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}'
    # basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'
    # win
    basedir_band_flag = r"E:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic"
    basedir_save_dict_band = fr"E:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic\{res_mode}"
    basedir_orb = r"E:\messenger\messenger_data\pl2\orb"

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    # low res
    if res_mode == 'low':
        r_bins = np.arange(1, 7+.5, .5)
        mlt_bins = np.arange(0, 24+1, 1)
        mlat_bins = np.arange(-90, 90+5, 5)
    # high res
    elif res_mode == 'high':
        r_bins = np.arange(1, 7+.1, .1)
        mlt_bins = np.arange(0, 24+.2, .2)
        mlat_bins = np.arange(-90, 90+1, 1)
    else:
        raise ValueError(f'Unsupported type: {res_mode=}')

    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    # -----------

    def initialize_dict():
        d = {'total': {}, 'dwell_time': {}} # dwell_timeを追加
        for i in range(n_band):
            d[f'band{i}'] = {}
        return d


    n_band = len(freqs_band) - 1

    # create cdf
    # ----------------------
    trange_list = time.make_time_list(trange, 2, 'hours')
    
    dict_band = {}
    dict_band['total'] = {}
    dict_band['dwell_time'] = {}
    for i in range(n_band):
        dict_band[f'band{i}'] = {}
    current_year = None

    start_time_loop = datetime.now()
    for i, trange_i in enumerate(trange_list):
        pytplot.del_data(silent=True)
        display.progress_bar(i, len(trange_list), start_time_loop, level='WARNING')
        display.info(f'{trange_i=}')
        dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
        year = dt_start_i.year
        
        # output cdf when the year changes
        if current_year is not None and year != current_year:
            # 年ごとの保存処理
            for key in dict_band.keys():
                if dict_band[key]:
                    file_name = f'dict_{key}_{current_year:04}.cdf'
                    cdf.dict_to_cdffile(
                        dict_band[key],
                        os.path.join(basedir_save_dict_band, file_name)
                    )
            # 初期化
            dict_band = initialize_dict()
            gc.collect()

        # if current_year is None:
        #     current_year = year
        # else:
        #     if year == current_year:
        #         pass
        #     else:
        #         # output cdf by year
        #         for i_band in range(n_band):
        #             dict_band_i = dict_band[f'band{i_band}']
        #             cdf.dict_to_cdffile(
        #                 dict_band_i,
        #                 os.path.join(basedir_save_dict_band, f'dict_band_{i_band}_{current_year:04}.cdf')
        #             )
        #         cdf.dict_to_cdffile(
        #             dict_band['total'],
        #             os.path.join(basedir_save_dict_band, f'dict_band_total_{current_year:04}.cdf')
        #         )
        #         # initialize
        #         dict_band = {}
        #         dict_band['total'] = {}
        #         for i in range(n_band):
        #             dict_band[f'band{i}'] = {}
        #         current_year = year

        current_year = year

        month = dt_start_i.month
        day = dt_start_i.day
        hour = dt_start_i.hour
        cdf_filepath_search = os.path.join(
            basedir_band_flag,
            f'{year:04}',
            f'{month:02}',
            f'messenger_band_flag_{year:04}{month:02}{day:02}{hour:02}*.cdf'
        )
        cdf_filepath = path.glob_one(cdf_filepath_search)
        if cdf_filepath is None:
            display.info('cdf_filepath is None -> continue')
            continue
        dict_data = cdf.cdffile_to_dict(cdf_filepath)

        
        times = dict_data['times']
        trange_data = time.convert([times[0], times[-1]], frm='unix', into='str')
        getdata.messenger_orb(trange_data, basedir_orb)

        # interp
        dat_orb_rmlatmlt = pytplot.get_data('orb_rmlatmlt')
        orb_interp = mathpy.interp_vec(times, dat_orb_rmlatmlt.times, dat_orb_rmlatmlt.y)
        pytplot.store_data('orb_interp', {'x': times, 'y': orb_interp})

        # calculate dts (time intervals)
        dts = calculate_time_intervals(times)
        pytplot.store_data('dts_val', {'x': times, 'y': dts})
        dict_dwell_i = distribution.rmlatmlt_meshgrid(
            'orb_interp', 
            datatype='orbit', 
            varname_data='dts_val',
            r_bins=r_bins, 
            mlt_bins=mlt_bins, 
            mlat_bins=mlat_bins
        )
        if not dict_band['dwell_time']:
            dict_band['dwell_time'] = dict_dwell_i
        else:
            dict_band['dwell_time'] = update_dict_sum(dict_band['dwell_time'], dict_dwell_i)

        # each band
        dict_band_j = {}
        for j in range(n_band):
            if 'dts_is_flag' in pytplot.tplot_names(quiet=True):
                pytplot.del_data('dts_is_flag')
            band_flag_j = dict_data['band_flag'][:, j]
            dts_is_flag = dts * band_flag_j
            pytplot.store_data('dts_is_flag', {'x': times, 'y': dts_is_flag})

            # indices_active = np.where(band_flag_j == 1)[0]
            
            # if len(indices_active) == 0:
            #     display.info('No indices_active -> continue')
            #     continue

            # times_active = times[indices_active]
            # orb_active = orb_interp[indices_active]
            # pytplot.store_data('orb_active_temp', {'x': times_active, 'y': orb_active})

            # pytplot.store_data(f'band_flag_{j}', {'x': dict_data['times'], 'y': dict_data['band_flag'][:, j]})

            dict_band_j[f'band{j}'] = distribution.rmlatmlt_meshgrid(
                'orb_interp',
                datatype='orbit',
                varname_data='dts_is_flag',
                r_bins=r_bins,
                mlt_bins=mlt_bins,
                mlat_bins=mlat_bins
            )

            if not dict_band[f'band{j}']:
                dict_band[f'band{j}'] = dict_band_j[f'band{j}']
            
            else: # update
                dict_band[f'band{j}'] = update_dict_sum(dict_band[f'band{j}'], dict_band_j[f'band{j}'])
    
        band_flag_all = dict_data['band_flag'] # (time, n_band)
        total_flag = np.any(band_flag_all == 1, axis=1).astype(int) 
        dts_is_total = dts * total_flag
        pytplot.store_data('dts_is_total', {'x': times, 'y': dts_is_total})

        dict_total_i = distribution.rmlatmlt_meshgrid(
            'orb_interp',
            datatype='orbit',
            varname_data='dts_is_total',
            r_bins=r_bins,
            mlt_bins=mlt_bins,
            mlat_bins=mlat_bins
        )

        if dict_band['total']:
            dict_band['total'] = update_dict_sum(dict_band['total'], dict_total_i)
        else:
            dict_band['total'] = dict_total_i
        
        del dict_data, times, dts, orb_interp, dict_dwell_i, dict_total_i
        if i % 10 == 0: # 10回に一度は強制回収
            gc.collect()
    
    # output last-year data
    if current_year is not None:
        for key in dict_band.keys():
            if dict_band[key]:
                cdf.dict_to_cdffile(
                    dict_band[key],
                    os.path.join(basedir_save_dict_band, f'dict_{key}_{current_year:04}.cdf')
                )

    # if current_year is not None:
    #     # output cdf by year
    #     for i_band in range(n_band):
    #         dict_band_i = dict_band[f'band{i_band}']
    #         cdf.dict_to_cdffile(
    #             dict_band_i,
    #             os.path.join(basedir_save_dict_band, f'dict_band_{i_band}_{current_year:04}.cdf')
    #         )
    #     cdf.dict_to_cdffile(
    #         dict_band['total'],
    #         os.path.join(basedir_save_dict_band, f'dict_band_total_{current_year:04}.cdf')
    #     )

    return


def distribution_band_flag_from_event_flag_emic():
    from common.distribution._base import update_dict_sum
    from messenger_analysis.distribution.distribution import (
        plot_bar_ions
    )

    basedir_out = 'out/distribution_band_flag_from_event_flag_emic'
    res_mode = 'high'
    basedir_save_dict_band = os.path.join(ROOT, f'messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}')
    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    # trange = ['2011-03-01 00:00:00', '2012-03-01 00:00:00']
    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    labels_freqs_band = ['Na+', 'O+', 'Li+', 'He+', 'He++', 'H+']
    # ----------

    n_band = len(freqs_band) - 1
    if len(labels_freqs_band) != n_band:
        display.warning(f'The lengths of freqs_band and labels_freqs_band must be same: {n_band=}, {len(labels_freqs_band)=}')
        return
    
    # ロードする変数：各バンド、全バンド統合(total)、軌道滞在時間(dwell_time)
    keys_to_load = [f'band{i}' for i in range(n_band)] + ['total', 'dwell_time']

    # 1. 指定期間内の全月ファイルをロード・統合
    month_list = time.make_time_list(trange, 1, 'months')
    dict_all_period = {key: {} for key in keys_to_load}

    for tr_m in month_list:
        dt_m = time.convert(tr_m[0], frm='str', into='datetime')
        yyyymm = f"{dt_m.year:04}{dt_m.month:02}"
        
        for key in keys_to_load:
            file_path = os.path.join(basedir_save_dict_band, f'dict_{key}_{yyyymm}.cdf')
            if os.path.exists(file_path):
                dict_month = cdf.cdffile_to_dict(file_path)
                if not dict_all_period[key]:
                    dict_all_period[key] = dict_month
                else:
                    dict_all_period[key] = update_dict_sum(dict_all_period[key], dict_month)

    dict_dwell_total = dict_all_period['dwell_time']
    if not dict_dwell_total:
        display.error("Not found for dwell time data")
        return

    # ファイル名用の時間文字列
    tr_dt0 = time.convert(trange[0], frm='str', into='datetime')
    tr_dt1 = time.convert(trange[1], frm='str', into='datetime')
    tr_str = f"{tr_dt0:%Y%m%d}-{tr_dt1:%Y%m%d}"
    outdir = os.path.join(basedir_out, f'{res_mode}_{tr_str}')
    # --- 2. 軌道滞在時間 (Dwell Time) のプロット ---
    distribution.plot_rmlatmlt_dict(
        dict_dwell_total,
        savefig=f'{outdir}/dwell_time_dist_{res_mode}_{tr_str}.png',
        suptitle=f'Total Orbital Dwell Time [s]\n{trange}',
    )

    # --- 3. 各周波数バンドごとの処理 ---
    for i in range(n_band):
        key = f'band{i}'
        dict_band_i = dict_all_period[key]
        if not dict_band_i:
            continue
        
        z_suffix = f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]'
        
        # zlim (occurrence rateのスケール調整)
        # zlim_occ = [0, 50] if i in [0, 1, 2] else [0, 100]
        # zlim_occ = [0, 50]
        zlim_occ = None

        # A. Event Time Distribution (イベント継続時間の生値)
        # R-MLT
        pydistplot.store_data(f'{key}_time_rmlt', {
            'x': dict_band_i['mesh_theta_rmlt'], 'y': dict_band_i['mesh_r_rmlt'], 'z': dict_band_i['rmlt_grid']
        })
        pydistplot.options(f'{key}_time_rmlt', datatype='rmlt', zlabel=f'Event Time [s]\n{labels_freqs_band[i]} band')
        
        # R-MLAT
        pydistplot.store_data(f'{key}_time_rmlat', {
            'x': dict_band_i['mesh_theta_rmlat'], 'y': dict_band_i['mesh_r_rmlat'], 'z': dict_band_i['rmlat_grid']
        })
        pydistplot.options(f'{key}_time_rmlat', datatype='rmlat', zlabel=f'Event Time [s]\n{labels_freqs_band[i]} band')

        # B. Occurrence Rate [%] 計算
        dict_occ_i = dict_band_i.copy()
        with np.errstate(divide='ignore', invalid='ignore'):
            dict_occ_i['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, 
                                             (dict_band_i['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
            dict_occ_i['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, 
                                              (dict_band_i['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)

        # R-MLT
        pydistplot.store_data(f'{key}_occ_rmlt', {
            'x': dict_occ_i['mesh_theta_rmlt'], 'y': dict_occ_i['mesh_r_rmlt'], 'z': dict_occ_i['rmlt_grid']
        })
        pydistplot.options(f'{key}_occ_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\n{labels_freqs_band[i]} band', zlim=zlim_occ)
        
        # R-MLAT
        pydistplot.store_data(f'{key}_occ_rmlat', {
            'x': dict_occ_i['mesh_theta_rmlat'], 'y': dict_occ_i['mesh_r_rmlat'], 'z': dict_occ_i['rmlat_grid']
        })
        pydistplot.options(f'{key}_occ_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\n{labels_freqs_band[i]} band', zlim=zlim_occ)

    # バンド別プロットの実行 (各バンドを並べて1枚の画像に出力)
    # pydistplot.plot([f'band{i}_occ_rmlt' for i in range(n_band)], 
    #                savefig=f'{outdir}/occ_rate_rmlt_{tr_str}.png', suptitle=f'Occurrence Rate (R, MLT)\n{trange}')
    # pydistplot.plot([f'band{i}_occ_rmlat' for i in range(n_band)], 
    #                savefig=f'{outdir}/occ_rate_rmlat_{tr_str}.png', suptitle=f'Occurrence Rate (R, MLAT)\n{trange}')
    # pydistplot.plot([f'band{i}_time_rmlt' for i in range(n_band)], 
    #                savefig=f'{outdir}/event_time_rmlt_{tr_str}.png', suptitle=f'Event Time (R, MLT) [s]\n{trange}')
    # pydistplot.plot([f'band{i}_time_rmlat' for i in range(n_band)], 
    #                savefig=f'{outdir}/event_time_rmlat_{tr_str}.png', suptitle=f'Event Time (R, MLAT) [s]\n{trange}')

    # --- 4. Total (全周波数バンド統合) のプロット ---
    dict_total = dict_all_period['total']
    if dict_total:
        # Total Occ. Rate 計算
        dict_total_occ = dict_total.copy()
        with np.errstate(divide='ignore', invalid='ignore'):
            dict_total_occ['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, 
                                                  (dict_total['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
            dict_total_occ['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, 
                                                   (dict_total['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)
        # Total occ
        # R-MLT
        pydistplot.store_data(f'total_occ_rmlt', {
            'x': dict_total_occ['mesh_theta_rmlt'], 'y': dict_total_occ['mesh_r_rmlt'], 'z': dict_total_occ['rmlt_grid']
        })
        pydistplot.options(f'total_occ_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\nAll band', zlim=zlim_occ)
        
        # R-MLAT
        pydistplot.store_data(f'total_occ_rmlat', {
            'x': dict_total_occ['mesh_theta_rmlat'], 'y': dict_total_occ['mesh_r_rmlat'], 'z': dict_total_occ['rmlat_grid']
        })
        pydistplot.options(f'total_occ_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\nAll band', zlim=zlim_occ)

        # Total event time
        # R-MLT
        pydistplot.store_data(f'total_time_rmlt', {
            'x': dict_total['mesh_theta_rmlt'], 'y': dict_total['mesh_r_rmlt'], 'z': dict_total['rmlt_grid']
        })
        pydistplot.options(f'total_time_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\nAll band', zlim=zlim_occ)
        
        # R-MLAT
        pydistplot.store_data(f'total_time_rmlat', {
            'x': dict_total['mesh_theta_rmlat'], 'y': dict_total['mesh_r_rmlat'], 'z': dict_total['rmlat_grid']
        })
        pydistplot.options(f'total_time_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\nAll band', zlim=zlim_occ)

        
        # # Total Occurrence Rate プロット
        # distribution.plot_rmlatmlt_dict(
        #     dict_total_occ,
        #     savefig=f'{outdir}/total_occ_rate_{res_mode}_{tr_str}.png',
        #     suptitle=f'Total EMIC Occurrence Rate [%]\n{trange}',
        # )

        # # Total Event Time プロット
        # distribution.plot_rmlatmlt_dict(
        #     dict_total,
        #     savefig=f'{outdir}/total_event_time_{res_mode}_{tr_str}.png',
        #     suptitle=f'Total EMIC Event Duration [s]\n{trange}',
        # )
    
    pydistplot.dist_names()
    for dist_type_i in ['rmlt', 'rmlat']:
        for datatype_j in ['time', 'occ']:
            vars = [
                f'total_{datatype_j}_{dist_type_i}'
            ]
            for i in range(n_band):
                vars.append(f'band{i}_{datatype_j}_{dist_type_i}')
                if i==2:
                    vars.append('')
            pydistplot.plot(
                vars,
                shape=(2, 4),
                savefig=f'{outdir}/distribution_{datatype_j}_{dist_type_i}_{tr_str}.png'
            )

        # Integral time in (R, MLT) & (R, MLAT) distribution for each band
        times_sum = []
        for i in range(n_band):
            var = f'band{i}_time_{dist_type_i}'
            band_time_i = pydistplot.get_data(var).z
            time_sum_i = np.nansum(band_time_i)
            times_sum.append(time_sum_i)
        plot_bar_ions(
            times_sum, 
            labels_freqs_band,
            suptitle=f'Integral time in {dist_type_i} distribution',
            savefig=f'{outdir}/integral_time_{dist_type_i}.png',
            ylog=True,
            ylabel='integral time [s]'
        )



    return


def _distribution_band_flag_from_event_flag_emic():#20260408
    from common.distribution._base import update_dict_sum

    # resolution mode: 'high', 'low'
    res_mode = 'high'
    # res_mode = 'low'

    # ディレクトリ設定
    # mac
    # basedir_band_flag = f'/Volumes/SSD4T/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}'
    # win
    basedir_band_flag = fr"E:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic\{res_mode}"
    # --------------------

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    
    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    n_band = len(freqs_band) - 1

    # 1. データ統合
    dt_trange = time.convert(trange, frm='str', into='datetime')
    years = range(dt_trange[0].year, dt_trange[1].year + 1)
    
    keys_to_load = [f'band{i}' for i in range(n_band)] + ['total', 'dwell_time']
    dict_all_period = {key: {} for key in keys_to_load}

    for year in years:
        for key in keys_to_load:
            file_path = os.path.join(basedir_band_flag, f'dict_{key}_{year:04}.cdf')
            if os.path.exists(file_path):
                dict_year = cdf.cdffile_to_dict(file_path)
                if not dict_all_period[key]:
                    dict_all_period[key] = dict_year
                else:
                    dict_all_period[key] = update_dict_sum(dict_all_period[key], dict_year)

    dict_dwell_total = dict_all_period['dwell_time']
    if not dict_dwell_total:
        raise FileNotFoundError("dwell_time data is missing.")

    # --- 2. 軌道滞在時間 (Dwell Time) のプロット (バンドによらない) ---
    dict_dwell_plot = dict_dwell_total.copy()
    dict_dwell_plot['rmlt_grid'] = dict_dwell_total['rmlt_grid']
    dict_dwell_plot['rmlat_grid'] = dict_dwell_total['rmlat_grid']

    distribution.plot_rmlatmlt_dict(
        dict_dwell_plot,
        savefig=f'out/dwell_time_distribution_{res_mode}.png',
        suptitle=f'Total Orbital Dwell Time [s]\n{trange}',
    )

    # --- 3. バンドごとの計算とプロット ---
    for i in range(n_band):
        key = f'band{i}'
        dict_band_i = dict_all_period[key]
        if not dict_band_i: continue

        z_suffix = f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]'

        # A. Event Time Distribution
        # --------------------------------------------------------
        pydistplot.store_data(f'{key}_event_time_rmlt', {
            'x': dict_band_i['mesh_theta_rmlt'], 
            'y': dict_band_i['mesh_r_rmlt'], 
            'z': dict_band_i['rmlt_grid']
        })
        pydistplot.options(f'{key}_event_time_rmlt', datatype='rmlt', zlabel=f'Event Time [s]\n{z_suffix}')

        pydistplot.store_data(f'{key}_event_time_rmlat', {
            'x': dict_band_i['mesh_theta_rmlat'], 
            'y': dict_band_i['mesh_r_rmlat'], 
            'z': dict_band_i['rmlat_grid']
        })
        pydistplot.options(f'{key}_event_time_rmlat', datatype='rmlat', zlabel=f'Event Time [s]\n{z_suffix}')

        # B. Occurrence Rate (百分率 [%])
        # --------------------------------------------------------
        dict_band_occ_i = dict_band_i.copy()
        with np.errstate(divide='ignore', invalid='ignore'):
            dict_band_occ_i['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, 
                                                    (dict_band_i['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
            dict_band_occ_i['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, 
                                                     (dict_band_i['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)

        pydistplot.store_data(f'{key}_occ_rmlt', {
            'x': dict_band_occ_i['mesh_theta_rmlt'], 
            'y': dict_band_occ_i['mesh_r_rmlt'], 
            'z': dict_band_occ_i['rmlt_grid']
        })
        pydistplot.options(f'{key}_occ_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\n{z_suffix}')
        
        pydistplot.store_data(f'{key}_occ_rmlat', {
            'x': dict_band_occ_i['mesh_theta_rmlat'], 
            'y': dict_band_occ_i['mesh_r_rmlat'], 
            'z': dict_band_occ_i['rmlat_grid']
        })
        pydistplot.options(f'{key}_occ_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\n{z_suffix}')

    # まとめてプロット実行
    # --- Occurrence Rate ---
    pydistplot.plot([f'band{i}_occ_rmlt' for i in range(n_band)], 
                    savefig=f'out/event_dist_band_occ_rmlt_{res_mode}.png', 
                    suptitle=f'Occurrence Rate (R, MLT)\n{trange}')
    pydistplot.plot([f'band{i}_occ_rmlat' for i in range(n_band)], 
                    savefig=f'out/event_dist_band_occ_rmlat_{res_mode}.png', 
                    suptitle=f'Occurrence Rate (R, MLAT)\n{trange}')

    # --- Event Time ---
    pydistplot.plot([f'band{i}_event_time_rmlt' for i in range(n_band)], 
                    savefig=f'out/event_dist_band_time_rmlt_{res_mode}.png', 
                    suptitle=f'Total Event Duration (R, MLT)\n{trange}')
    pydistplot.plot([f'band{i}_event_time_rmlat' for i in range(n_band)], 
                    savefig=f'out/event_dist_band_time_rmlat_{res_mode}.png', 
                    suptitle=f'Total Event Duration (R, MLAT)\n{trange}')

    # TotalのOccurrence Rate
    dict_total = dict_all_period['total']
    
    # Total Occurrence Rate
    dict_total_occ = dict_total.copy()
    with np.errstate(divide='ignore', invalid='ignore'):
        dict_total_occ['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, (dict_total['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
        dict_total_occ['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, (dict_total['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)
    
    distribution.plot_rmlatmlt_dict(
        dict_total_occ,
        savefig=f'out/event_dist_total_occ_{res_mode}.png',
        suptitle=f'Total Occurrence Rate (f/fcp=[0, 1])\n{trange}',
    )

    # Total Event Time Distribution [s]
    dict_total_time = dict_total.copy()
    dict_total_time['rmlt_grid'] = dict_total['rmlt_grid']
    dict_total_time['rmlat_grid'] = dict_total['rmlat_grid']
    
    distribution.plot_rmlatmlt_dict(
        dict_total_time,
        savefig=f'out/event_dist_total_time_{res_mode}.png',
        suptitle=f'Total Event Duration [s] (f/fcp=[0, 1])\n{trange}',
    )
    return


def create_distribution_band_flag_by_taa():
    """
    TAA (True Anomaly Angle) の範囲ごとに分類されたエミック波の分布データを作成する。
    """
    from common.distribution._base import update_dict, calculate_time_intervals, update_dict_sum

    # --- 設定 ---
    res_mode = 'high'
    
    basedir_band_flag = os.path.join(ROOT, 'messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic')
    basedir_save_root = os.path.join(ROOT, f'messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}')
    basedir_orb = os.path.join(ROOT, 'messenger/messenger_data/pl2/orb')
    taa_cdf_filepath = os.path.join(ROOT, 'horizons_data/taa.cdf')

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    
    # --- ビン設定 ---
    if res_mode == 'low':
        r_bins = np.arange(1, 7.5, .5)
        mlt_bins = np.arange(0, 25, 1)
        mlat_bins = np.arange(-90, 95, 5)
    elif res_mode == 'high':
        r_bins = np.arange(1, 7.1, .1)
        mlt_bins = np.arange(0, 24.2, .2)
        mlat_bins = np.arange(-90, 91, 1)
    else:
        raise ValueError(f'Unsupported resolution mode: {res_mode}')

    # TAAの分類範囲 (45-135: 近心点付近, 135-225: 下降, 225-315: 遠心点付近, 315-45: 上昇)
    # taa_ranges = [(45, 135), (135, 225), (225, 315), (315, 45)]
    taa_ranges = [(0, 180), (180, 360)]


    # --- 補助関数 ---
    def get_fresh_storage():
        """TAAレンジごとの保存用辞書を初期化する"""
        storage = {}
        for r in taa_ranges:
            key = f"taa_{r[0]}_{r[1]}"
            storage[key] = {
                'total': {},        # いずれかのバンドがONの累積時間
                'dwell_time': {}    # その領域での純粋な滞在時間
            }
        return storage

    def save_current_data(storage, year, month):
        """現在の辞書データをファイルに書き出す"""
        if month is None:
            return
        for taa_key, contents in storage.items():
            # TAAレンジごとのサブディレクトリ作成
            save_dir = os.path.join(basedir_save_root, taa_key)
            
            # 各項目（dwell_time, total, band0, band1...）を個別のCDFとして保存
            for var_key, var_data in contents.items():
                if var_data:
                    file_name = f'{taa_key}_{var_key}_{year:04}{month:02}.cdf'
                    out_path = os.path.join(save_dir, file_name)
                    cdf.dict_to_cdffile(var_data, out_path)
    
    def unwrap_angles(angles):
        """角度の不連続点(360->0)を解消して補間しやすくする"""
        return np.unwrap(np.deg2rad(angles))


    # --- メイン処理開始 ---
    # TAAデータの読み込み
    taa_data = cdf.cdffile_to_dict(taa_cdf_filepath)
    taa_times = taa_data['times']
    taa_unwrapped = unwrap_angles(taa_data['taa'])
    # pytplot.store_data('taa_full', {'x': taa_data['times'], 'y': taa_data['taa']})

    trange_list = time.make_time_list(trange, 2, 'hours')
    dict_storage = get_fresh_storage()
    current_month = None
    start_time_loop = datetime.now()

    for i, trange_i in enumerate(trange_list):
        pytplot.del_data()
        display.progress_bar(i, len(trange_list), start_time_loop, level='WARNING')
        display.info(f'{trange_i=}')
        
        dt_start_i = time.convert(trange_i[0], frm='str', into='datetime')
        year = dt_start_i.year
        month = dt_start_i.month
        
        # 月が変わったら保存してリセット
        if current_month is not None and month != current_month:
            save_current_data(dict_storage, current_year, current_month)
            dict_storage = get_fresh_storage()

        current_year = year
        current_month = month

        # 該当するバンドフラグCDFの検索
        month, day, hour = dt_start_i.month, dt_start_i.day, dt_start_i.hour
        cdf_filepath_search = os.path.join(
            basedir_band_flag, f'{year:04}', f'{month:02}',
            f'messenger_band_flag_{year:04}{month:02}{day:02}{hour:02}*.cdf'
        )
        cdf_filepath = path.glob_one(cdf_filepath_search)
        if cdf_filepath is None:
            continue
            
        dict_data = cdf.cdffile_to_dict(cdf_filepath)
        times = dict_data['times']
        n_band = dict_data['band_flag'].shape[1]
        
        # 軌道データの取得と補間
        trange_data = time.convert([times[0], times[-1]], frm='unix', into='str')
        getdata.messenger_orb(trange_data, basedir_orb)
        dat_orb_rmlatmlt = pytplot.get_data('orb_rmlatmlt')
        if dat_orb_rmlatmlt is None: continue
        
        orb_interp = mathpy.interp_vec(times, dat_orb_rmlatmlt.times, dat_orb_rmlatmlt.y)
        pytplot.store_data('orb_interp', {'x': times, 'y': orb_interp})

        # TAAデータの補間 (角度データの補間は急激な変化に注意が必要だが、公転周期に対して2h刻みなら許容範囲)
        taa_interp_rad = mathpy.interp_vec(times, taa_times, taa_unwrapped)
        taa_interp = np.rad2deg(taa_interp_rad) % 360.0  # 度に戻して 0-360に正規化

        # taa_interp = mathpy.interp_vec(times, taa_data['times'], taa_unwrapped)

        # 時間間隔の計算
        dts = calculate_time_intervals(times)

        # --- TAAレンジごとのループ集計 ---
        for r in taa_ranges:
            t_low, t_high = r
            taa_key = f"taa_{t_low}_{t_high}"
            
            # TAA範囲のマスク作成 (0度またぎに対応)
            if t_low < t_high:
                taa_mask = (taa_interp >= t_low) & (taa_interp < t_high)
            else:
                taa_mask = (taa_interp >= t_low) | (taa_interp < t_high)
            
            if not np.any(taa_mask):
                continue
            
            m_float = taa_mask.astype(float)

            # 1. Dwell Time (滞在時間)
            pytplot.store_data('tmp_dts', {'x': times, 'y': dts * m_float}, replace=True)
            dist_dwell = distribution.rmlatmlt_meshgrid(
                'orb_interp', datatype='orbit', varname_data='tmp_dts', 
                r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins
            )
            dict_storage[taa_key]['dwell_time'] = update_dict_sum(dict_storage[taa_key]['dwell_time'], dist_dwell)

            # 2. 各周波数バンドの集計
            for j in range(n_band):
                band_key = f'band{j}'
                # TAA内にいて、かつそのバンドのフラグが立っている場合
                combined_flag = dict_data['band_flag'][:, j] * m_float
                pytplot.store_data('tmp_dts_flag', {'x': times, 'y': dts * combined_flag}, replace=True)
                
                dist_band = distribution.rmlatmlt_meshgrid(
                    'orb_interp', datatype='orbit', varname_data='tmp_dts_flag',
                    r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins
                )
                
                if band_key not in dict_storage[taa_key]:
                    dict_storage[taa_key][band_key] = {}
                dict_storage[taa_key][band_key] = update_dict_sum(dict_storage[taa_key][band_key], dist_band)

            # 3. Total (いずれかのバンドが1)
            # band_flagのいずれかの列が1であればTrue
            total_active = np.any(dict_data['band_flag'] == 1, axis=1).astype(float)
            combined_total_flag = total_active * m_float
            pytplot.store_data('tmp_dts_total', {'x': times, 'y': dts * combined_total_flag}, replace=True)
            
            dist_total = distribution.rmlatmlt_meshgrid(
                'orb_interp', datatype='orbit', varname_data='tmp_dts_total',
                r_bins=r_bins, mlt_bins=mlt_bins, mlat_bins=mlat_bins
            )
            dict_storage[taa_key]['total'] = update_dict_sum(dict_storage[taa_key]['total'], dist_total)

        # メモリ解放
        del dict_data, times, dts, taa_interp, orb_interp

    # 最終年のデータを保存
    if current_month is not None:
        save_current_data(dict_storage, current_year, current_month)

    return


def distribution_band_flag_by_taa():
    """
    指定された trange に基づいて TAA ごとの分布図（Occ. Rate, Event Time, Dwell Time）をプロットする。
    ディレクトリ構造: basedir/{res_mode}/{taa_key}/{taa_key}_{var}_{YYYYMM}.cdf
    """
    from common.distribution._base import update_dict_sum
    from messenger_analysis.distribution.distribution import (
        plot_bar_ions
    )

    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    res_mode = 'high'
    basedir_band_flag_dist = os.path.join(ROOT, f'messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}')
    basedir_out = 'out/distribution_band_flag_by_taa'
    
    # バンド設定
    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    labels_freqs_band = ['Na+', 'O+', 'Li+', 'He+', 'He++', 'H+']
    # taa_ranges = [(45, 135), (135, 225), (225, 315), (315, 45)]
    taa_ranges = [(0, 180), (180, 360)]
    # ----------

    n_band = len(freqs_band) - 1
    if len(labels_freqs_band) != n_band:
        display.warning(f'The lengths of freqs_band and labels_freqs_band must be same: {n_band=}, {len(labels_freqs_band)=}')
        return
    
    keys_to_load = [f'band{i}' for i in range(n_band)] + ['total', 'dwell_time']

    # 指定された trange から対象となる年月のリストを作成
    month_list = time.make_time_list(trange, 1, 'months')
    # ファイル名用文字列
    tr_str = f"{time.convert(trange[0], frm='str', into='datetime'):%Y%m%d}_{time.convert(trange[1], frm='str', into='datetime'):%Y%m%d}"
    
    # --- TAAレンジごとのループ処理 ---
    for r in taa_ranges:
        t_low, t_high = r
        taa_key = f"taa_{t_low}_{t_high}"
        label_taa = f'TAA:[{t_low}-{t_high}]'
        display.info(f'Processing: {taa_key}')
        
        # 1. データの読み込みと統合
        dict_all_period = {key: {} for key in keys_to_load}
        for tr_m in month_list:
            dt_m = time.convert(tr_m[0], frm='str', into='datetime')
            yyyymm = f"{dt_m.year:04}{dt_m.month:02}"
            
            for var_key in keys_to_load:
                file_path = os.path.join(basedir_band_flag_dist, taa_key, f'{taa_key}_{var_key}_{yyyymm}.cdf')
                if os.path.exists(file_path):
                    dict_month = cdf.cdffile_to_dict(file_path)
                    if not dict_all_period[var_key]:
                        dict_all_period[var_key] = dict_month
                    else:
                        dict_all_period[var_key] = update_dict_sum(dict_all_period[var_key], dict_month)

        dict_dwell_total = dict_all_period['dwell_time']
        if not dict_dwell_total:
            display.warning(f'No dwell_time data found for {taa_key}')
            continue
        
        outdir = os.path.join(basedir_out, f'{taa_key}_{tr_str}')
        # --- 2. 軌道滞在時間 (Dwell Time) のプロット ---
        distribution.plot_rmlatmlt_dict(
            dict_dwell_total,
            savefig=f'{outdir}/dwell_time_{taa_key}_{tr_str}.png',
            suptitle=f'Orbital Dwell Time [s] - {label_taa}\n{trange}',
        )

        # --- 3. バンドごとの計算とプロット ---
        for i in range(n_band):
            key = f'band{i}'
            dict_band_i = dict_all_period[key]
            if not dict_band_i: continue

            z_suffix = f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]'

            # zlim
            # if i in [0, 1, 2]:
            #     zlim_occ = [0, 50]
            # else:
            #     zlim_occ = [0, 100]
            # zlim_occ = [0, 50]
            zlim_occ = None

            # A. Event Time Distribution
            pydistplot.store_data(f'{taa_key}_{key}_time_rmlt', {
                'x': dict_band_i['mesh_theta_rmlt'], 'y': dict_band_i['mesh_r_rmlt'], 'z': dict_band_i['rmlt_grid']
            })
            pydistplot.options(f'{taa_key}_{key}_time_rmlt', datatype='rmlt', zlabel=f'Event Time [s]\n{z_suffix}\n{label_taa}')

            pydistplot.store_data(f'{taa_key}_{key}_time_rmlat', {
                'x': dict_band_i['mesh_theta_rmlat'], 'y': dict_band_i['mesh_r_rmlat'], 'z': dict_band_i['rmlat_grid']
            })
            pydistplot.options(f'{taa_key}_{key}_time_rmlat', datatype='rmlat', zlabel=f'Event Time [s]\n{z_suffix}\n{label_taa}')

            # B. Occurrence Rate [%]
            dict_band_occ_i = dict_band_i.copy()
            with np.errstate(divide='ignore', invalid='ignore'):
                dict_band_occ_i['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, (dict_band_i['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
                dict_band_occ_i['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, (dict_band_i['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)

            pydistplot.store_data(f'{taa_key}_{key}_occ_rmlt', {
                'x': dict_band_occ_i['mesh_theta_rmlt'], 'y': dict_band_occ_i['mesh_r_rmlt'], 'z': dict_band_occ_i['rmlt_grid']
            })
            pydistplot.options(f'{taa_key}_{key}_occ_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\n{labels_freqs_band[i]} band\n{label_taa}', zlim=zlim_occ)
            
            pydistplot.store_data(f'{taa_key}_{key}_occ_rmlat', {
                'x': dict_band_occ_i['mesh_theta_rmlat'], 'y': dict_band_occ_i['mesh_r_rmlat'], 'z': dict_band_occ_i['rmlat_grid']
            })
            pydistplot.options(f'{taa_key}_{key}_occ_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\n{labels_freqs_band[i]} band\n{label_taa}')

        # バンド別プロット実行
        # pydistplot.plot([f'{taa_key}_band{i}_occ_rmlt' for i in range(n_band)], 
        #                 savefig=f'{outdir}/dist_{taa_key}_occ_rmlt_{tr_str}.png', suptitle=f'Occ. Rate (R, MLT) - {label_taa}')
        # pydistplot.plot([f'{taa_key}_band{i}_occ_rmlat' for i in range(n_band)], 
        #                 savefig=f'{outdir}/dist_{taa_key}_occ_rmlat_{tr_str}.png', suptitle=f'Occ. Rate (R, MLAT) - {label_taa}')
        # pydistplot.plot([f'{taa_key}_band{i}_time_rmlt' for i in range(n_band)], 
        #                 savefig=f'{outdir}/dist_{taa_key}_time_rmlt_{tr_str}.png', suptitle=f'Event Time (R, MLT) - {label_taa}')
        # pydistplot.plot([f'{taa_key}_band{i}_time_rmlat' for i in range(n_band)], 
        #                 savefig=f'{outdir}/dist_{taa_key}_time_rmlat_{tr_str}.png', suptitle=f'Event Time (R, MLAT) - {label_taa}')

        # --- 4. Total (全バンド統合) のプロット ---
        dict_total = dict_all_period['total']
        if dict_total:
            # Total Occ. Rate
            dict_total_occ = dict_total.copy()
            with np.errstate(divide='ignore', invalid='ignore'):
                dict_total_occ['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, (dict_total['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
                dict_total_occ['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, (dict_total['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)
            
            # Total occ
            # R-MLT
            pydistplot.store_data(f'{taa_key}_total_occ_rmlt', {
                'x': dict_total_occ['mesh_theta_rmlt'], 'y': dict_total_occ['mesh_r_rmlt'], 'z': dict_total_occ['rmlt_grid']
            })
            pydistplot.options(f'{taa_key}_total_occ_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\nAll band\n{label_taa}', zlim=zlim_occ)
            
            # R-MLAT
            pydistplot.store_data(f'{taa_key}_total_occ_rmlat', {
                'x': dict_total_occ['mesh_theta_rmlat'], 'y': dict_total_occ['mesh_r_rmlat'], 'z': dict_total_occ['rmlat_grid']
            })
            pydistplot.options(f'{taa_key}_total_occ_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\nAll band\n{label_taa}', zlim=zlim_occ)

            # Total event time
            # R-MLT
            pydistplot.store_data(f'{taa_key}_total_time_rmlt', {
                'x': dict_total['mesh_theta_rmlt'], 'y': dict_total['mesh_r_rmlt'], 'z': dict_total['rmlt_grid']
            })
            pydistplot.options(f'{taa_key}_total_time_rmlt', datatype='rmlt', zlabel=f'Occ. Rate [%]\nAll band\n{label_taa}', zlim=zlim_occ)
            
            # R-MLAT
            pydistplot.store_data(f'{taa_key}_total_time_rmlat', {
                'x': dict_total['mesh_theta_rmlat'], 'y': dict_total['mesh_r_rmlat'], 'z': dict_total['rmlat_grid']
            })
            pydistplot.options(f'{taa_key}_total_time_rmlat', datatype='rmlat', zlabel=f'Occ. Rate [%]\nAll band\n{label_taa}', zlim=zlim_occ)

            # distribution.plot_rmlatmlt_dict(
            #     dict_total_occ,
            #     savefig=f'{outdir}/dist_{taa_key}_total_occ_{tr_str}.png',
            #     suptitle=f'Total Occurrence Rate - {label_taa}\n{trange}',
            # )

            # # Total Event Time
            # distribution.plot_rmlatmlt_dict(
            #     dict_total,
            #     savefig=f'{outdir}/dist_{taa_key}_total_time_{tr_str}.png',
            #     suptitle=f'Total Event Duration [s] - {label_taa}\n{trange}',
            # )
    
    pydistplot.dist_names()
    for r in taa_ranges:
        t_low, t_high = r
        taa_key = f"taa_{t_low}_{t_high}"
        label_taa = f'TAA:[{t_low}-{t_high}]'
        outdir = os.path.join(basedir_out, f'{taa_key}_{tr_str}')
        for dist_type_i in ['rmlt', 'rmlat']:
            for datatype_j in ['time', 'occ']:
                vars = [
                    f'{taa_key}_total_{datatype_j}_{dist_type_i}'
                ]
                for i in range(n_band):
                    vars.append(f'{taa_key}_band{i}_{datatype_j}_{dist_type_i}')
                    if i==2:
                        vars.append('')
                pydistplot.plot(
                    vars,
                    shape=(2, 4),
                    savefig=f'{outdir}/distribution_{taa_key}_{datatype_j}_{dist_type_i}_{tr_str}.png'
                )
            # Integral time in (R, MLT) & (R, MLAT) distribution for each band
            times_sum = []
            for i in range(n_band):
                var = f'{taa_key}_band{i}_time_{dist_type_i}'
                band_time_i = pydistplot.get_data(var).z
                time_sum_i = np.nansum(band_time_i)
                times_sum.append(time_sum_i)
            plot_bar_ions(
                times_sum, 
                labels_freqs_band,
                suptitle=f'Integral time in distribution: {taa_key}, {dist_type_i}',
                savefig=f'{outdir}/integral_time_{taa_key}_{dist_type_i}.png',
                ylog=True,
                ylabel='integral time [s]',
                # yrange=[0, 2e7]
            )


    return


def _distribution_band_flag_by_taa():# 20260407
    """
    指定された trange に基づいて TAA ごとの分布図をプロットする。
    ディレクトリ構造: basedir/{res_mode}/{taa_key}/{taa_key}_{var}_{YYYYMM}.cdf
    """
    from common.distribution._base import update_dict_sum

    # --- 設定 ---
    trange = ['2011-03-01 00:00:00', '2015-05-01 00:00:00']
    res_mode = 'high'
    
    # 保存ルートディレクトリ
    basedir_band_flag_dist = os.path.join(MAIN_DIR, f'messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}')
    
    # バンド設定
    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    n_band = len(freqs_band) - 1
    taa_ranges = [(45, 135), (135, 225), (225, 315), (315, 45)]
    keys_to_load = [f'band{i}' for i in range(n_band)] + ['total', 'dwell_time']

    # 1. 指定された trange から対象となる年月のリストを作成
    # time.make_time_list を使用して1ヶ月刻みのリストを取得
    month_list = time.make_time_list(trange, 1, 'months')
    
    # --- TAAレンジごとのループ処理 ---
    for r in taa_ranges:
        t_low, t_high = r
        taa_key = f"taa_{t_low}_{t_high}"
        
        # この TAA レンジかつ指定期間の全データを統合する辞書
        dict_all_period = {key: {} for key in keys_to_load}
        
        # 2. データの読み込みと統合
        for tr_m in month_list:
            dt_m = time.convert(tr_m[0], frm='str', into='datetime')
            yyyymm = f"{dt_m.year:04}{dt_m.month:02}"
            
            # 各変数（band, total, dwell_time）のファイルを読み込み
            for var_key in keys_to_load:
                # ディレクトリ構造: {taa_key}/{taa_key}_{var_key}_{yyyymm}.cdf
                file_path = os.path.join(basedir_band_flag_dist, taa_key, f'{taa_key}_{var_key}_{yyyymm}.cdf')
                
                if os.path.exists(file_path):
                    dict_month = cdf.cdffile_to_dict(file_path)
                    if not dict_all_period[var_key]:
                        dict_all_period[var_key] = dict_month
                    else:
                        dict_all_period[var_key] = update_dict_sum(dict_all_period[var_key], dict_month)

        # 滞在時間データがない場合はその TAA レンジをスキップ
        dict_dwell_total = dict_all_period['dwell_time']
        if not dict_dwell_total:
            display.warning(f'No dwell_time data found for {taa_key} in {trange}')
            continue

        # --- 3. プロット用データの計算と保存 ---
        for i in range(n_band):
            key = f'band{i}'
            dict_band_i = dict_all_period[key]
            if not dict_band_i: continue

            z_suffix = f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]'
            label_taa = f'TAA:[{t_low}-{t_high}]'

            # Occurrence Rate [%] の算出
            dict_band_occ_i = dict_band_i.copy()
            with np.errstate(divide='ignore', invalid='ignore'):
                # MLT
                dict_band_occ_i['rmlt_grid'] = np.where(
                    dict_dwell_total['rmlt_grid'] > 0, 
                    (dict_band_i['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0
                )
                # MLAT
                dict_band_occ_i['rmlat_grid'] = np.where(
                    dict_dwell_total['rmlat_grid'] > 0, 
                    (dict_band_i['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0
                )

            # tplot 変数への格納
            v_rmlt = f'{taa_key}_{key}_occ_rmlt'
            pydistplot.store_data(v_rmlt, {
                'x': dict_band_occ_i['mesh_theta_rmlt'], 
                'y': dict_band_occ_i['mesh_r_rmlt'], 
                'z': dict_band_occ_i['rmlt_grid']
            })
            pydistplot.options(v_rmlt, datatype='rmlt', zlabel=f'Occ. Rate [%]\n{z_suffix}\n{label_taa}')

            v_rmlat = f'{taa_key}_{key}_occ_rmlat'
            pydistplot.store_data(v_rmlat, {
                'x': dict_band_occ_i['mesh_theta_rmlat'], 
                'y': dict_band_occ_i['mesh_r_rmlat'], 
                'z': dict_band_occ_i['rmlat_grid']
            })
            pydistplot.options(v_rmlat, datatype='rmlat', zlabel=f'Occ. Rate [%]\n{z_suffix}\n{label_taa}')

        # --- 4. 画像の出力 ---
        # 期間をファイル名に含める
        tr_str = f"{time.convert(trange[0], frm='str', into='datetime'):%Y%m%d}_{time.convert(trange[1], frm='str', into='datetime'):%Y%m%d}"
        
        pydistplot.plot(
            [f'{taa_key}_band{i}_occ_rmlt' for i in range(n_band)], 
            savefig=f'out/dist_{taa_key}_occ_rmlt_{tr_str}.png', 
            suptitle=f'Occurrence Rate (R, MLT) - {label_taa}\nRange: {trange}'
        )
        pydistplot.plot(
            [f'{taa_key}_band{i}_occ_rmlat' for i in range(n_band)], 
            savefig=f'out/dist_{taa_key}_occ_rmlat_{tr_str}.png', 
            suptitle=f'Occurrence Rate (R, MLAT) - {label_taa}\nRange: {trange}'
        )

    return


def _distribution_band_flag_from_event_flag_emic():# 20260331
    from common.distribution._base import update_dict_sum

    res_mode = 'high' # 'high', 'low'

    # ディレクトリ設定
    basedir_band_flag = f'/Volumes/SSD4T/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}'
    # basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'

    trange = ['2011-03-01 00:00:00', '2013-03-01 00:00:00']
    
    # ビン設定 (create関数と一致させる)
    if res_mode == 'low':
        r_bins = np.arange(1, 7+.5, .5)
        mlt_bins = np.arange(0, 24+1, 1)
        mlat_bins = np.arange(-90, 90+5, 5)
    elif res_mode == 'high':
        r_bins = np.arange(1, 7+.1, .1)
        mlt_bins = np.arange(0, 24+.2, .2)
        mlat_bins = np.arange(-90, 90+1, 1)
    
    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    n_band = len(freqs_band) - 1

    # 1. 年ごとのCDFを統合して全期間の分布(dict)を作成
    # ----------------------
    dt_trange = time.convert(trange, frm='str', into='datetime')
    years = range(dt_trange[0].year, dt_trange[1].year + 1)
    
    # 統合用データの初期化
    # 修正ポイント: dwell_time も統合対象に含める
    keys_to_load = [f'band{i}' for i in range(n_band)] + ['total', 'dwell_time']
    dict_all_period = {key: {} for key in keys_to_load}

    for year in years:
        for key in keys_to_load:
            # create関数の命名規則 "dict_{key}_{year}.cdf" に合わせる
            file_path = os.path.join(basedir_band_flag, f'dict_{key}_{year:04}.cdf')
            
            if os.path.exists(file_path):
                dict_year = cdf.cdffile_to_dict(file_path)
                if not dict_all_period[key]:
                    dict_all_period[key] = dict_year
                else:
                    dict_all_period[key] = update_dict_sum(dict_all_period[key], dict_year)
            else:
                display.warning(f'File not found: {file_path}')

    # 2. 全期間統合済みファイルを保存 (中間キャッシュ)
    # ----------------------
    for key in keys_to_load:
        if dict_all_period[key]:
            output_path = os.path.join(basedir_band_flag, f'dict_{key}_merged.cdf')
            cdf.dict_to_cdffile(dict_all_period[key], output_path)

    # 3. Occurrence rate の計算とプロット
    # ----------------------
    # 分母となる実際の滞在時間を取得
    dict_dwell_total = dict_all_period['dwell_time']
    
    if not dict_dwell_total:
        raise FileNotFoundError("dwell_time data is missing. Please run create_... function again.")

    # バンドごとに計算
    for i in range(n_band):
        key = f'band{i}'
        dict_band_i = dict_all_period[key]
        if not dict_band_i: continue

        # Occurrence Rate 算出 (分子:イベント時間 / 分母:全滞在時間)
        dict_band_occ_i = dict_band_i.copy()
        
        # ゼロ除算を避けて計算
        with np.errstate(divide='ignore', invalid='ignore'):
            dict_band_occ_i['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, 
                                                    (dict_band_i['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
            dict_band_occ_i['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, 
                                                     (dict_band_i['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)

        # プロット用データの準備
        z_label = f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]'
        
        # rmlt plot
        pydistplot.store_data(f'{key}_occ_rmlt', {
            'x': dict_band_occ_i['mesh_theta_rmlt'], 
            'y': dict_band_occ_i['mesh_r_rmlt'], 
            'z': dict_band_occ_i['rmlt_grid']
        })
        pydistplot.options(f'{key}_occ_rmlt', datatype='rmlt', zlabel=z_label)
        
        # rmlat plot
        pydistplot.store_data(f'{key}_occ_rmlat', {
            'x': dict_band_occ_i['mesh_theta_rmlat'], 
            'y': dict_band_occ_i['mesh_r_rmlat'], 
            'z': dict_band_occ_i['rmlat_grid']
        })
        pydistplot.options(f'{key}_occ_rmlat', datatype='rmlat', zlabel=z_label)

    pydistplot.dist_names()

    pydistplot.plot([f'band{i}_occ_rmlt' for i in range(n_band)], 
                    savefig=f'out/event_dist_band_flag_occ_rmlt_{res_mode}.png', suptitle=f'Occurrence Rate (R-MLT)\n{trange}')
    pydistplot.plot([f'band{i}_occ_rmlat' for i in range(n_band)], 
                    savefig=f'out/event_dist_band_flag_occ_rmlat_{res_mode}.png', suptitle=f'Occurrence Rate (R-MLat)\n{trange}')

    # TotalのOccurrence Rate
    dict_total = dict_all_period['total']
    dict_total_occ = dict_total.copy()
    with np.errstate(divide='ignore', invalid='ignore'):
        dict_total_occ['rmlt_grid'] = np.where(dict_dwell_total['rmlt_grid'] > 0, (dict_total['rmlt_grid'] / dict_dwell_total['rmlt_grid']) * 100, 0)
        dict_total_occ['rmlat_grid'] = np.where(dict_dwell_total['rmlat_grid'] > 0, (dict_total['rmlat_grid'] / dict_dwell_total['rmlat_grid']) * 100, 0)
    
    distribution.plot_rmlatmlt_dict(
        dict_total_occ,
        savefig=f'out/event_dist_band_flag_occ_total_{res_mode}.png',
        suptitle=f'Total Occurrence Rate (f/fcp 0-1)\n{trange=}'
    )

    return


def _distribution_band_flag_from_event_flag_emic():
    from common import distribution
    from common.distribution._base import update_dict, calculate_time_intervals, update_dict_sum
    from messenger_analysis.distribution._dwell_time import (
        get_dwell_time_trange_with_ref
    )
    res_mode = 'low'

    # mac
    basedir_band_flag = f'/Volumes/SSD4T/messenger/messenger_data_analysis/event/band_flag_from_event_flag_emic/{res_mode}'
    basedir_ref_dwell_time = f'/Volumes/SSD4T/messenger/messenger_data_analysis/orb/ref_dwell_rmlat_whole_6s/{res_mode}res/1month'
    basedir_orb = '/Volumes/SSD4T/messenger/messenger_data/pl2/orb'
    # win
    # basedir_band_flag = r"F:\messenger\messenger_data_analysis\event\band_flag_from_event_flag_emic"
    # basedir_ref_dwell_time = r"F:\messenger\messenger_data_analysis\orb\ref_dwell_rmlat_whole_6s\1month"

    trange = ['2011-03-01 00:00:00', '2013-03-01 00:00:00']
    # low res
    if res_mode == 'low':
        r_bins = np.arange(1, 7+.5, .5)
        mlt_bins = np.arange(0, 24+1, 1)
        mlat_bins = np.arange(-90, 90+5, 5)
    # high res
    elif res_mode == 'high':
        r_bins = np.arange(1, 7+.1, .1)
        mlt_bins = np.arange(0, 24+.2, .2)
        mlat_bins = np.arange(-90, 90+1, 1)
    else:
        raise ValueError(f'Unsupported type: {res_mode=}')

    freqs_band = [0, 1/23, 1/16, 1/7, 1/4, 1/2, 1]
    # ----------------------

    n_band = len(freqs_band) - 1

    # output cdf
    dt_trange = time.convert(trange, frm='str', into='datetime')
    start_year = dt_trange[0].year
    end_year = dt_trange[1].year
    years = range(start_year, end_year+1)
    dict_band = {}
    dict_band['total'] = {}
    for i in range(n_band):
        dict_band[f'band{i}'] = {}
    for year in years:
        for i in range(n_band):
            # band
            cdf_filepath_band_year = os.path.join(basedir_band_flag, f'dict_band_{i}_{year:04}.cdf')
            if os.path.exists(cdf_filepath_band_year):
                dict_band_i = cdf.cdffile_to_dict(cdf_filepath_band_year)
                if dict_band[f'band{i}']:
                    dict_band[f'band{i}'] = update_dict_sum(dict_band[f'band{i}'], dict_band_i)
                else:
                    dict_band[f'band{i}'] = dict_band_i
                
                
            else:
                display.warning(f'No cdf file: {cdf_filepath_band_year}')
                continue
        # total
        cdf_filepath_total_year = os.path.join(basedir_band_flag, f'dict_band_total_{year:04}.cdf')
        if os.path.exists(cdf_filepath_total_year):
            dict_total_i = cdf.cdffile_to_dict(cdf_filepath_total_year)
            if dict_band['total']:
                dict_band['total'] = update_dict_sum(dict_band['total'], dict_total_i)
            else:
                dict_band['total'] = dict_total_i
        else:
            display.warning(f'No cdf file: {cdf_filepath_total_year}')
            continue

    for i_band in range(n_band):
        dict_band_i = dict_band[f'band{i_band}']
        cdf.dict_to_cdffile(
            dict_band_i,
            os.path.join(basedir_band_flag, f'dict_band_{i_band}.cdf')
        )
    cdf.dict_to_cdffile(
        dict_band['total'],
        os.path.join(basedir_band_flag, 'dict_band_total.cdf')
    )

    # read cdf
    # ----------------------
    dict_band = {}
    for i in range(n_band):
        dict_band[f'band{i}'] = cdf.cdffile_to_dict(
            os.path.join(basedir_band_flag, f'dict_band_{i}.cdf')
        )
    dict_band['total'] = cdf.cdffile_to_dict(
        os.path.join(basedir_band_flag, 'dict_band_total.cdf')
    )
    # ----------------------

    vars_distplot_rmlt = []
    vars_distplot_rmlat = []
    for i in range(n_band):
        dict_band_i = dict_band[f'band{i}']
        # rmlt
        pydistplot.store_data(f'band{i}_rmlt', {'x': dict_band_i['mesh_theta_rmlt'], 'y': dict_band_i['mesh_r_rmlt'], 'z': dict_band_i['rmlt_grid']})
        pydistplot.options(f'band{i}_rmlt', datatype='rmlt', zlabel=f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]')
        vars_distplot_rmlt.append(f'band{i}_rmlt')
        # rmlat
        pydistplot.store_data(f'band{i}_rmlat', {'x': dict_band_i['mesh_theta_rmlat'], 'y': dict_band_i['mesh_r_rmlat'], 'z': dict_band_i['rmlat_grid']})
        pydistplot.options(f'band{i}_rmlat', datatype='rmlat', zlabel=f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]')
        vars_distplot_rmlat.append(f'band{i}_rmlat')
        # distribution.plot_rmlatmlt(
        #     dict_band_i['mesh_theta_rmlt'],
        #     dict_band_i['mesh_r_rmlt'],
        #     dict_band_i['rmlt_grid'],
        #     dict_band_i['mesh_theta_rmlat'],
        #     dict_band_i['mesh_r_rmlat'],
        #     dict_band_i['rmlat_grid'],
        #     savefig=f'out/event_dist_band_flag_{i}.png',
        #     suptitle=f'Event distribution: Band Flag f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]\n{trange=}',
        # )
    
    pydistplot.dist_names()
    pydistplot.plot(
        vars_distplot_rmlt,
        savefig=f'out/event_distribution_band_flag_rmlt_{res_mode}.png'
    )
    pydistplot.plot(
        vars_distplot_rmlat,
        savefig=f'out/event_distribution_band_flag_rmlat_{res_mode}.png'
    )

    # Dwell time (whole period)
    dict_orb_meshgrid = get_dwell_time_trange_with_ref(
        trange,
        basedir_orb=basedir_orb,
        r_bins=r_bins,
        mlt_bins=mlt_bins,
        mlat_bins=mlat_bins,
        # parent_dir_ref_dwell='/Volumes/SSD-PGCU3C/messenger',
        basedir_ref_dwell=basedir_ref_dwell_time,
        rmlat_whole=True
    )
    distribution.plot_rmlatmlt_dict(
        dict_orb_meshgrid,
        suptitle=f'Dwell Time\n{trange=}',
        savefig=f'out/orb_dwell_time_{res_mode}.png'
    )

    # Occurrence rate
    vars_distplot_rmlt_occ = []
    vars_distplot_rmlat_occ = []
    for i in range(n_band):
        dict_band_i = dict_band[f'band{i}']
        dict_band_occ_i = dict_band_i.copy()
        dict_band_occ_i['rmlt_grid'] = dict_band_i['rmlt_grid'] / dict_orb_meshgrid['rmlt_grid'] * 100
        dict_band_occ_i['rmlat_grid'] = dict_band_i['rmlat_grid'] / dict_orb_meshgrid['rmlat_grid'] * 100

        # rmlt
        pydistplot.store_data(f'band{i}_rmlt_occ', {'x': dict_band_occ_i['mesh_theta_rmlt'], 'y': dict_band_occ_i['mesh_r_rmlt'], 'z': dict_band_occ_i['rmlt_grid']})
        pydistplot.options(f'band{i}_rmlt_occ', datatype='rmlt', zlabel=f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]')
        vars_distplot_rmlt_occ.append(f'band{i}_rmlt_occ')
        # rmlat
        pydistplot.store_data(f'band{i}_rmlat_occ', {'x': dict_band_occ_i['mesh_theta_rmlat'], 'y': dict_band_occ_i['mesh_r_rmlat'], 'z': dict_band_occ_i['rmlat_grid']})
        pydistplot.options(f'band{i}_rmlat_occ', datatype='rmlat', zlabel=f'f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]')
        vars_distplot_rmlat_occ.append(f'band{i}_rmlat_occ')

        # distribution.plot_rmlatmlt(
        #     dict_band_occ_i['mesh_theta_rmlt'],
        #     dict_band_occ_i['mesh_r_rmlt'],
        #     dict_band_occ_i['rmlt_grid'],
        #     dict_band_occ_i['mesh_theta_rmlat'],
        #     dict_band_occ_i['mesh_r_rmlat'],
        #     dict_band_occ_i['rmlat_grid'],
        #     savefig=f'out/event_dist_band_flag_occ_{i}.png',
        #     suptitle=f'Event distribution (Occurrence rate): Band Flag f/fcp=[{freqs_band[i]:.2f}, {freqs_band[i+1]:.2f}]\n{trange=}',
        # )
    
    pydistplot.dist_names()
    pydistplot.plot(
        vars_distplot_rmlt_occ,
        suptitle=f'Occurrence Rate: {trange=}',
        savefig=f'out/event_distribution_band_flag_rmlt_occ_{res_mode}.png'
    )

    pydistplot.plot(
        vars_distplot_rmlat_occ,
        suptitle=f'Occurrence Rate: {trange=}',
        savefig=f'out/event_distribution_band_flag_rmlat_occ_{res_mode}.png',
    )

    # total
    dict_band_total = dict_band['total']
    # dict_band_0 = dict_band['band0']
    # dict_band_total = {
    #     'mesh_theta_rmlt': dict_band_0['mesh_theta_rmlt'],
    #     'mesh_r_rmlt': dict_band_0['mesh_r_rmlt'],
    #     'mesh_theta_rmlat': dict_band_0['mesh_theta_rmlat'],
    #     'mesh_r_rmlat': dict_band_0['mesh_r_rmlat'],
    #     'rmlt_grid': np.zeros_like(dict_band_0['rmlt_grid']),
    #     'rmlt_grid_count': np.zeros_like(dict_band_0['rmlt_grid_count']),
    #     'rmlat_grid': np.zeros_like(dict_band_0['rmlat_grid']),
    #     'rmlat_grid_count': np.zeros_like(dict_band_0['rmlat_grid_count']),
    # }
    # for i in range(n_band):
    #     dict_band_i = dict_band[f'band{i}']
    #     dict_band_total = update_dict_sum(dict_band_total, dict_band_i)
    distribution.plot_rmlatmlt(
        dict_band_total['mesh_theta_rmlt'],
        dict_band_total['mesh_r_rmlt'],
        dict_band_total['rmlt_grid'],
        dict_band_total['mesh_theta_rmlat'],
        dict_band_total['mesh_r_rmlat'],
        dict_band_total['rmlat_grid'],
        savefig=f'out/event_dist_band_flag_total_{res_mode}.png',
        suptitle=f'Event distribution: Band Flag f/fcp=[0, 1]\n{trange=}',
    )

    dict_band_occ_total = dict_band_total.copy()
    dict_band_occ_total['rmlt_grid'] = dict_band_total['rmlt_grid'] / dict_orb_meshgrid['rmlt_grid'] * 100
    dict_band_occ_total['rmlat_grid'] = dict_band_total['rmlat_grid'] / dict_orb_meshgrid['rmlat_grid'] * 100
    distribution.plot_rmlatmlt_dict(
        dict_band_occ_total,
        savefig=f'out/event_dist_band_flag_occ_total_{res_mode}.png',
        suptitle=f'Event distribution (Occurrence rate): Band Flag f/fcp=[0, 1]\n{trange=}'
    )
    

    return


# ----------------------------------------------------
# Horizons: https://ssd.jpl.nasa.gov/horizons/app.html#/
# ----------------------------------------------------
def create_taa_data():
    trange = ['2011-01-01', '2015-05-01']
    savecdf = os.path.join(ROOT, 'horizons_data/taa.cdf')
    # ---------------
    horizons.load_taa(trange, savecdf)
    return


# def convert_horizons_taa_to_cdf():
#     from messenger_analysis.horizons.convert_txt_to_cdf import (
#         convert_horizons_taa_txt_to_cdf
#     )

#     input_txt_path = os.path.join(ROOT, 'messenger/horizons_results.txt')
#     output_cdf_path = os.path.join(ROOT, 'messenger/taa.cdf')

#     convert_horizons_taa_txt_to_cdf(input_txt_path, output_cdf_path)
#     return


# -------------------------------------------------------------
# analysis
# -------------------------------------------------------------
def main_analysis():
    from messenger_analysis.analysis.analysis import analysis
    # trange = ['2011-03-25 00:00:00', '2011-03-25 02:00:00']
    trange = ['2011-05-17 08:30:00', '2011-05-17 09:00:00']

    basedir_cdf_files = os.path.join(DATA, 'messenger/messenger_data/pl1/mag_mso')
    basedir_orb = os.path.join(DATA, 'messenger/messenger_data/pl2/orb')

    yrange = [0, 0.15]

    # ---------

    params = analysis(
        trange,
        basedir_cdf_files=basedir_cdf_files,
        basedir_orb=basedir_orb,
        spec_window_sec=200,
        mask=True,
        threshold_psd_abs_mask=100
    )
    display.print_dict(params)

    pytplot.copy_data('fcp', 'fcp_overplot')
    pytplot.options('fcp_overplot', color='white', linewidth=2, linestyle='dashed', ylabel='freq [Hz]')
    pytplot.options('mq23_norm', ylabel='f/fcp')

    # plot
    pytplot.tplot_names()
    pytplot.options('mag', ylabel='Mag (MSO)\n[nT]', legend=True, legend_names=['Bx', 'By', 'Bz'])
    pytplot.options('mag_mfa', ylabel='Mag (MFA)\n[nT]')
    pytplot.options('mag_norm', ylabel='Mag norm\n[nT]')
    pytplot.options('fcp', ylabel='fcp [Hz]')
    pytplot.options('mag_mfa_x_dpwrspc_psd', zlabel='PSD_perp1')
    pytplot.options('mag_mfa_y_dpwrspc_psd', zlabel='PSD_perp2')
    pytplot.options('mag_mfa_z_dpwrspc_psd', zlabel='PSD_para')
    pytplot.options('mag_mfa_x_dpwrspc_psd_norm', zlabel='PSD_perp1', yrange=yrange)
    pytplot.options('mag_mfa_y_dpwrspc_psd_norm', zlabel='PSD_perp2', yrange=yrange)
    pytplot.options('mag_mfa_z_dpwrspc_psd_norm', zlabel='PSD_para', yrange=yrange)
    pytplot.options('polarization_norm', zlabel='Polarization\nellipticity', yrange=yrange)
    pytplot.options('wna_norm', zlabel='WNA', yrange=yrange)
    pytplot.options('planarity_norm', zlabel='Planarity', yrange=yrange)
    pytplot.options('mq1_norm', ylabel='f/fcp')
    pytplot.options('mq16_norm', ylabel='f/fcp', color='black')
    # pytplot.options('mq1_norm', legend=True, legend_names=['H+'])
    pytplot.options('psd_norm_abs', yrange=yrange)
    pytplot.options('psd_norm_x_mask', yrange=yrange)
    pytplot.options('psd_norm_y_mask', yrange=yrange)
    pytplot.options('psd_norm_z_mask', yrange=yrange)
    pytplot.options('polarization_norm_mask', yrange=yrange)
    pytplot.options('wna_norm_mask', yrange=yrange)
    pytplot.options('planarity_norm_mask', yrange=yrange)
    

    suptitle = f'{trange=}\n' + f'resampling_rate={params['resampling_rate']} Hz, average_window_mfa={params['average_window_mfa_sec']} s\n' + f'spec_window_sec={params['spec_window_sec']}, spec_rate_overlap={params['spec_rate_overlap']}, fcp_moving_sec={params['average_window_sec']} s'

    pytplot.tplot(
        [
            'sampling_rate',
            'mag',
            # 'mag_resampled',
            'mag_mfa',
            # 'mag_norm',
            'mag_norm',
            'fcp',
            ['mag_mfa_x_dpwrspc_psd', 'fcp_overplot'],
            ['mag_mfa_y_dpwrspc_psd', 'fcp_overplot'],
            ['mag_mfa_z_dpwrspc_psd', 'fcp_overplot'],
            ['mag_mfa_x_dpwrspc_psd_norm', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['mag_mfa_y_dpwrspc_psd_norm', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['mag_mfa_z_dpwrspc_psd_norm', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['polarization_norm', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['wna_norm', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['planarity_norm', 'mq7_norm', 'mq16_norm', 'mq23_norm']
        ],
        figsize=(12, 18),
        # suptitle=suptitle,
        xlim=trange,
        delta_xticks=10,
        timeunit_xticks='minutes',
        save_png='out/mag_analysis.png',
        var_orbit='orb_rmlatmlt',
        list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]']
    )

    pytplot.tplot(
        [
            'sampling_rate',
            'mag',
            # 'mag_resampled',
            'mag_mfa',
            # 'mag_norm',
            'mag_norm',
            'fcp',
            ['psd_norm_abs', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['psd_norm_x_mask', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['psd_norm_y_mask', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['psd_norm_z_mask', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['polarization_norm_mask', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['wna_norm_mask', 'mq7_norm', 'mq16_norm', 'mq23_norm'],
            ['planarity_norm_mask', 'mq7_norm', 'mq16_norm', 'mq23_norm']
        ],
        figsize=(12, 18),
        # suptitle=suptitle,
        xlim=trange,
        delta_xticks=10,
        timeunit_xticks='minutes',
        save_png='out/mag_analysis_masked.png',
        var_orbit='orb_rmlatmlt',
        list_label_orbit=['R [Rm]', 'MLAT [deg]', 'MLT [hr]', 'TIME [HH:MM]']
    )

    
    return


def main_orbit():
    # trange = ['2012-03-05 16:00:00', '2012-03-05 17:00:00']
    trange = ['2011-04-01 00:00:00', '2011-05-01 00:00:00']

    basedir_orb = os.path.join(MAIN_DIR, 'messenger_data/pl2/orb')

    getdata.messenger_orb(trange, basedir_orb=basedir_orb)
    dat_orb = pytplot.get_data('orb_mso')
    pytplot.store_data('pos', {'x': dat_orb.times, 'y': dat_orb.y}, replace=True)


    # orb_rmlatmlt = messenger_orbit.mso_to_rmlatmlt(orb)
    # pytplot.store_data('rmlatmlt', {'x': dat_orb.times, 'y': orb_rmlatmlt})

    # orbit.rmlatmlt2polar('rmlatmlt')
    

    orbit.xyz2polar('pos', to='polar')
    orbit.rmlatmlt2polar('pos_polar', to='rmlatmlt')
    pytplot.tplot_names()

    orbit.plot('pos', savefig='out/test/orbit.png', suptitle=f'Orbit (MSO): {trange=}')
    orbit.plot('pos_polar', 'polar', savefig='out/test/orbit_polar.png', suptitle=f'Orbit (Polar): {trange=}')
    # rmlatmlt
    orbit.plot(
        'pos_polar_rmlatmlt', 
        'rmlatmlt', 
        savefig='out/test/orbit_rmlatmlt.png',
        suptitle=f'Orbit (R, MLAT, MLT): {trange=}'
    )

    # rmlatmlt_itself
    orbit.plot(
        'pos_polar_rmlatmlt', 
        'rmlatmlt_itself', 
        savefig='out/test/orbit_rmlatmlt_itself.png',
        suptitle=f'Orbit (R, MLAT, MLT) itself: {trange=}'
    )
    return


############################################################
# test
def test_read_cdf():
    # cdf_file_path = os.path.join(MAIN_DIR, 'taa.cdf')
    cdf_file_path = r"D:\horizons_data\taa.cdf"
    cdf.info(cdf_file_path)

    dict_data = cdf.cdffile_to_dict(cdf_file_path)
    pytplot.store_data('taa', {'x': dict_data['times'], 'y': dict_data['taa']})
    pytplot.options('taa', grid=True, ylabel='TAA')

    pytplot.tplot_names()
    pytplot.tplot(
        [
            'taa'
        ],
        # figsize=(12, 16),
        save_png='out/test.png',
        delta_xticks=3,
        timeunit_xticks='months',
    )
    return


def test_mso2mse():
    from messenger_analysis.analysis.analysis import (
        mag_analysis
    )
    from common.coordinate._to_mbe import (
        convert_to_mbe
    )

    trange = ['2012-01-01 00:00:00', '2012-01-01 02:00:00']
    basedir_mag = os.path.join(DATA, 'messenger/messenger_data/pl1/mag_mso')
    basedir_orb = os.path.join(DATA, 'messenger/messenger_data/pl2/orb')

    getdata.messenger_mag(trange, basedir_cdf_files=basedir_mag)
    getdata.messenger_orb(trange, basedir_orb=basedir_orb)

    coordinate.to_mbe('orb_mso', 'mag', window_sec=30, varname_out='orb_mbe')
    coordinate.to_mbe('mag', 'mag', window_sec=30)

    pytplot.tplot_names()
    pytplot.options('mag', legend=True, legend_names=['Bx', 'By', 'Bz'])
    pytplot.tplot(
        [
            'mag',
            'mag_ave',
            'mag_mbe',
            'orb_mso',
            'orb_mbe',
        ],
        figsize=(8, 12),
        save_png='out/test.png'
    )

    orbit.plot(
        'orb_mso',
        savefig='out/test2.png'
    )

    orbit.plot(
        'orb_mbe',
        savefig='out/test3.png'
    )
    return



def test_stft():
    cdf_filepath = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso/2012/01/messenger_mag_mso_20120101.cdf'
    cdf.info(cdf_filepath)
    dict_data = cdf.cdffile_to_dict(cdf_filepath)
    times = dict_data['time']
    mag = dict_data['mag']

    # sampling rate
    sampling_rates = 1 / np.diff(times)
    sampling_rates = np.append(sampling_rates, sampling_rates[-1])
    pytplot.store_data('sampling_rate', {'x': times, 'y': sampling_rates})

    pytplot.store_data('mag_mso', {'x': times, 'y': mag})
    spec.spectrogram_vec('mag_mso', window_second=200, rate_overlap=0.9)
    pytplot.options('mag_mso_x_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True)
    pytplot.options('mag_mso_y_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True)
    pytplot.options('mag_mso_z_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True)

    pytplot.tplot_names()
    pytplot.tplot(
        [
            'sampling_rate',
            'mag_mso',
            'mag_mso_x_dpwrspc_psd',
            'mag_mso_y_dpwrspc_psd',
            'mag_mso_z_dpwrspc_psd',
        ],
        figsize=(12, 10),
        xlim=['2012-01-01 04:00:00', '2012-01-01 06:00:00'],
        save_png='test.png'
    )
    return


def test_quality_flag():
    from messenger_analysis.pl2.quality_flag import (
        get_quality_flag_mag
    )
    trange = ['2011-03-25 00:00:00', '2011-03-25 02:00:00']
    basedir_mag = '/Volumes/SSD4T/messenger/messenger_data/mag_mso'
    getdata.messenger_mag(trange, basedir_cdf_files=basedir_mag)

    dat_mag = pytplot.get_data('mag')
    times = dat_mag.times
    mag = dat_mag.y
    mag_norm = np.linalg.norm(mag, axis=1)
    quality_flag = get_quality_flag_mag(times, mag_norm)

    pytplot.store_data('quality_flag', {'x': times, 'y': quality_flag})
    pytplot.tplot_names()
    pytplot.tplot(
        [
            'mag',
            'mag_norm',
            'quality_flag'
        ],
        # xlim=['2011-03-25 00:18:00', '2011-03-25 00:19:00'],
        save_png='test.png'
    )
    return


def test_pl2():
    from messenger_analysis.pl2.create_pl2_data import (
        create_pl2_data
    )
    from messenger_analysis.pl2.quality_flag import (
        get_quality_flag_outliers,
        get_quality_flag_sampling_rate
    )

    cdf_filepath = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso/2012/01/messenger_mag_mso_20120104.cdf'
    savecdf = 'test.cdf'
    create_pl2_data(cdf_filepath, savecdf)

    cdf.info(savecdf)
    dict_data = cdf.cdffile_to_dict(savecdf)
    pytplot.store_data('mag_mso', {'x': dict_data['times'], 'y': dict_data['mag_mso']})
    pytplot.store_data('quality_flag', {'x': dict_data['times'], 'y': dict_data['quality_flag']})

    # spec
    spec.spectrogram_vec('mag_mso', window_size=4096, rate_overlap=0.9)
    pytplot.options('mag_mso_x_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    pytplot.options('mag_mso_y_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    pytplot.options('mag_mso_z_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])

    pytplot.tplot_names()
    pytplot.tplot(
        [
            'mag_mso',
            'quality_flag',
            'mag_mso_x_dpwrspc_psd',
            'mag_mso_y_dpwrspc_psd',
            'mag_mso_z_dpwrspc_psd',
        ],
        figsize=(12, 16),
        save_png='test.png'
    )


    # def interpolate_small_gaps(times, data, is_invalid, max_gap_size=5):
    #     """
    #     NaNの連続区間を特定し、その個数が max_gap_size 以下の箇所のみ線形補間する。
        
    #     Args:
    #         times: 時間軸 (1D array)
    #         data: データ本体 (2D array: [time, components])
    #         is_invalid: NaNフラグ (1D bool array, Trueが欠損)
    #         max_gap_size: 補間を許可する最大の連続サンプル数
    #     """
    #     filled_data = data.copy()
    #     n_times = len(times)
    #     n_comps = data.shape[1]

    #     # 差分を使ってNaN区間の開始と終了を検出
    #     # padded_invalid: [False, ..., True, True, ..., False] のように前後を固める
    #     padded = np.concatenate(([False], is_invalid, [False]))
    #     diff = np.diff(padded.astype(int))
    #     starts = np.where(diff == 1)[0]    # NaN開始インデックス
    #     ends = np.where(diff == -1)[0]     # NaN終了インデックス (この手前までがNaN)

    #     for s, e in zip(starts, ends):
    #         gap_size = e - s
            
    #         # 1. 配列の端（最初や最後）の欠損は補間できないのでスキップ
    #         if s == 0 or e == n_times:
    #             continue
                
    #         # 2. 隙間が閾値以下の場合のみ補間処理を実行
    #         if gap_size <= max_gap_size:
    #             # 補間に使用する前後のインデックス
    #             idx_before = s - 1
    #             idx_after = e
                
    #             t0, t1 = times[idx_before], times[idx_after]
    #             dt = t1 - t0
                
    #             for c in range(n_comps):
    #                 v0, v1 = filled_data[idx_before, c], filled_data[idx_after, c]
                    
    #                 # 線形補間: y = v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    #                 # 隙間部分の各点について計算
    #                 t_gap = times[s:e]
    #                 filled_data[s:e, c] = v0 + (v1 - v0) * (t_gap - t0) / dt
                    
    #     return filled_data
    
    # def remove_isolated_data(data, min_island_size=2):
    #     """
    #     NaNに囲まれた孤立したデータポイントを除去する。
        
    #     Args:
    #         data: 入力データ (2D array [time, components])。既に品質フラグ等でNaNが挿入されていることを想定。
    #         min_island_size: 有効データがこの数値未満の連続数である場合、NaNに置き換える。
    #     Returns:
    #         cleaned_data: 孤立データが除去されたデータ
    #     """
    #     cleaned_data = data.copy()
    #     # いずれかの成分がNaNであるか、全成分がNaNであるかで判定（ここでは全成分で判定）
    #     is_valid = ~np.isnan(cleaned_data).any(axis=1)
        
    #     # 有効データの区間（島）を検出
    #     padded = np.concatenate(([False], is_valid, [False]))
    #     diff = np.diff(padded.astype(int))
    #     starts = np.where(diff == 1)[0]
    #     ends = np.where(diff == -1)[0]
        
    #     for s, e in zip(starts, ends):
    #         island_size = e - s
    #         if island_size < min_island_size:
    #             # 短すぎる有効データ区間をNaNに置き換え
    #             cleaned_data[s:e, :] = np.nan
                
    #     return cleaned_data
    
    # def resample_and_fill_gaps(
    #     times, 
    #     data, 
    #     is_invalid, 
    #     target_sampling_rate=20.0, 
    #     max_gap_size=5,
    #     max_time_gap=None # 秒単位での制限が必要な場合
    # ):
    #     """
    #     リサンプリングと微小欠損の補間を「一度の補間操作」で行う。
    #     これにより、多重の線形補間によるデータの鈍り（高周波の消失）を最小限に抑える。
    #     """
    #     n_times = len(times)
    #     n_comps = data.shape[1]
        
    #     # 1. ターゲットとなる新しい時間軸を作成
    #     start_t, end_t = times[0], times[-1]
    #     target_dt = 1.0 / target_sampling_rate
    #     resampled_times = np.arange(start_t, end_t + target_dt / 2.0, target_dt)
    #     resampled_data = np.full((len(resampled_times), n_comps), np.nan)

    #     # 2. 欠損区間のリストアップ (元データのインデックスベース)
    #     padded = np.concatenate(([False], is_invalid, [False]))
    #     diff = np.diff(padded.astype(int))
    #     starts = np.where(diff == 1)[0]
    #     ends = np.where(diff == -1)[0]

    #     # 有効な区間をマークする
    #     # 基本は「元データで有効な点」のみをリサンプリングに使う
    #     valid_mask = ~is_invalid
        
    #     # 3. 補間を許可するインデックスを特定
    #     # 元々の interpolate_small_gaps のロジックを反映
    #     allowed_to_interpolate = valid_mask.copy()
    #     for s, e in zip(starts, ends):
    #         gap_size = e - s
    #         if 0 < s and e < n_times and gap_size <= max_gap_size:
    #             # この区間は補間して良いので、リサンプリング時のソースに含める
    #             # ただし、端点は元データにある点を使う必要がある
    #             pass 
    #         else:
    #             # 大きな欠損や端の欠損はリサンプリング後もNaNにする必要がある
    #             pass

    #     # 4. コンポーネントごとにリサンプリング
    #     # 有効な点のみを抽出して補間を行う
    #     for c in range(n_comps):
    #         # np.interp は有効な点の間を線形に結ぶ
    #         # 大きな隙間を勝手に埋めないように、元データのギャップが大きい場所を特定してNaNで上書きする
    #         interp_vals = np.interp(resampled_times, times[valid_mask], data[valid_mask, c])
    #         resampled_data[:, c] = interp_vals

    #     # 5. 「補間を許可しなかった大きな隙間」をリサンプリング後もNaNに戻す
    #     # これを行わないと、リサンプリング（np.interp）が大きな欠損も埋めてしまう
    #     for s, e in zip(starts, ends):
    #         gap_size = e - s
    #         if not (0 < s and e < n_times and gap_size <= max_gap_size):
    #             # 補間不可な区間の時間範囲
    #             t_gap_start = times[s-1] if s > 0 else times[s]
    #             t_gap_end = times[e] if e < n_times else times[e-1]
                
    #             # リサンプリング後の時間軸で該当する箇所をNaNにする
    #             mask = (resampled_times >= t_gap_start) & (resampled_times <= t_gap_end)
    #             resampled_data[mask, :] = np.nan

    #     return resampled_times, resampled_data
    

    # savecdf = 'test.cdf'

    # # create cdf
    # # cdf_filepath = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso/2008/01/messenger_mag_mso_20080112.cdf'
    # # dict_data = cdf.cdffile_to_dict(cdf_filepath)
    # # times = dict_data['time']
    # # mag = dict_data['mag']
    # # mag_norm = np.linalg.norm(mag, axis=1)

    # # quality_flag_outliers = get_quality_flag_outliers(mag_norm)
    # # quality_flag_sampling = get_quality_flag_sampling_rate(times, target_rate=20)

    # # quality_flag = np.stack([quality_flag_outliers, quality_flag_sampling]).T

    # # dict_return = {
    # #     'times': times,
    # #     'mag_mso': mag,
    # #     'quality_flag': quality_flag
    # # }

    # # # savecdf
    # # cdf.dict_to_cdffile(dict_return, savecdf)
    # # -----
    
    # cdf.info(savecdf)

    # dict_data = cdf.cdffile_to_dict(savecdf)
    # pytplot.store_data('mag_mso_orig', {'x': dict_data['times'], 'y': dict_data['mag_mso']})
    # pytplot.store_data('quality_flag', {'x': dict_data['times'], 'y': dict_data['quality_flag']})
    # pytplot.options('mag_mso_orig', legend=True)

    # times = dict_data['times']
    # mag_mso = dict_data['mag_mso']
    # quality_flag = dict_data['quality_flag']

    # # apply quality flag
    # is_invalid = (quality_flag == 1).any(axis=1)
    # mag_mso_with_nan = mag_mso.copy()
    # mag_mso_with_nan[is_invalid] = np.nan
    # pytplot.store_data('mag_mso_with_nan', {'x': times, 'y': mag_mso_with_nan})
    # pytplot.store_data('is_invalid', {'x': times, 'y': is_invalid})

    # # interpolate in case of spike NaN
    # # times_resampled, mag_mso_resampled = resample_and_fill_gaps(
    # #     times, 
    # #     mag_mso_with_nan, # NaNが入ったままのデータ
    # #     is_invalid, 
    # #     target_sampling_rate=20,
    # #     max_gap_size=5
    # # )
    
    # MAX_GAP = 5
    # mag_mso_interpolated = interpolate_small_gaps(
    #     times, 
    #     mag_mso_with_nan, 
    #     is_invalid, 
    #     max_gap_size=MAX_GAP
    # )

    # # times_resampled, mag_mso_resampled = mathpy.resample_data(times, mag_mso_interpolated, target_sampling_rate=20, force_upsampling=True)
    # # pytplot.store_data('mag_mso', {'x': times_resampled, 'y': mag_mso_resampled})
    # pytplot.store_data('mag_mso', {'x': times, 'y': mag_mso_interpolated})

    # spec.spectrogram_vec('mag_mso_orig', window_size=4096, rate_overlap=0.9)
    # spec.spectrogram_vec('mag_mso', window_size=4096, rate_overlap=0.9)
    # pytplot.options('mag_mso_orig_x_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    # pytplot.options('mag_mso_orig_y_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    # pytplot.options('mag_mso_orig_z_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    # pytplot.options('mag_mso_x_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    # pytplot.options('mag_mso_y_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    # pytplot.options('mag_mso_z_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])

    # pytplot.tplot_names()
    # pytplot.tplot(
    #     [
    #         'mag_mso_orig',
    #         'quality_flag',
    #         'mag_mso_with_nan',
    #         'mag_mso',
    #         'mag_mso_orig_x_dpwrspc_psd',
    #         'mag_mso_orig_y_dpwrspc_psd',
    #         'mag_mso_orig_z_dpwrspc_psd',
    #         'mag_mso_x_dpwrspc_psd',
    #         'mag_mso_y_dpwrspc_psd',
    #         'mag_mso_z_dpwrspc_psd',
    #     ],
    #     figsize=(12, 16),
    #     xlim=['2008-01-12 05:00:00', '2008-01-12 07:00:00'],
    #     save_png='test.png'
    # )


    # pytplot.tplot_names()
    # pytplot.tplot(
    #     [
    #         'mag_mso_orig',
    #         'quality_flag',
    #         'mag_mso',
    #         'mag_mso_orig_x_dpwrspc_psd',
    #         'mag_mso_orig_y_dpwrspc_psd',
    #         'mag_mso_orig_z_dpwrspc_psd',
    #         'mag_mso_x_dpwrspc_psd',
    #         'mag_mso_y_dpwrspc_psd',
    #         'mag_mso_z_dpwrspc_psd',
    #     ],
    #     figsize=(12, 16),
    #     # xlim=['2011-03-23 16:00:00', '2011-03-23 18:00:00'],
    #     save_png='test.png'
    # )
    return


def test_pl1():
    cdf_filepath = '/Volumes/SSD4T/messenger/messenger_data/pl1/mag_mso/2012/01/messenger_mag_mso_20120101.cdf'
    cdf.info(cdf_filepath)
    dict_data = cdf.cdffile_to_dict(cdf_filepath)
    pytplot.store_data('mag_mso', {'x': dict_data['time'], 'y': dict_data['mag']})

    spec.spectrogram_vec('mag_mso', window_size=4096, rate_overlap=0.9)
    pytplot.options('mag_mso_x_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    pytplot.options('mag_mso_y_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])
    pytplot.options('mag_mso_z_dpwrspc_psd', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1])

    pytplot.tplot_names()
    pytplot.tplot(
        [
            'mag_mso',
            'mag_mso_x_dpwrspc_psd',
            'mag_mso_y_dpwrspc_psd',
            'mag_mso_z_dpwrspc_psd',
        ],
        figsize=(12, 16),
        save_png='test.png'
    )

    return





def test_download_horizons_data():
    from messenger_analysis import horizons
    from messenger_analysis.horizons.downloader import download_horizons_data
    from astroquery.jplhorizons import Horizons
    import pandas as pd

    trange = ['2011-01-01', '2015-05-01']
    horizons.load_taa(trange)

    # target_id = '199'
    # location = '@sun'
    # start_time = '2011-01-01'
    # end_time = '2012-01-01'
    # time_step = '1d'
    # download_horizons_data(
    #     target_id=target_id,
    #     location=location,
    #     start_time=start_time,
    #     stop_time=end_time,
    #     time_step=time_step,
    #     savecsv='test.csv'
    # )
    # df = pd.read_csv('test.csv')
    # taa = df['true_anom']
    # display.debug(f'{taa=}')


    # def download_horizons_data(target_id, location, start_time, stop_time, time_step):
    #     """
    #     JPL Horizonsからデータを取得する。
    #     エラーが発生した場合（名前の重複など）、詳細なメッセージを表示する。
    #     """
    #     print("\n" + "="*40)
    #     print("--- JPL Horizons Data Downloader ---")
    #     print("="*40)

    #     try:
    #         print(f"Target  : {target_id}")
    #         print(f"Location: {location}")
    #         print(f"Period  : {start_time} to {stop_time}")
    #         print(f"Step    : {time_step}")
    #         print("-" * 40)

    #         # 2. Horizonsオブジェクトの作成
    #         # 名前でエラーが出る場合は ID (水星なら '199') を直接指定するのがベスト
    #         obj = Horizons(
    #             id=target_id,
    #             location=location,
    #             epochs={'start': start_time, 'stop': stop_time, 'step': time_step}
    #         )

    #         # 3. エフェメリスデータの取得
    #         # 注意: 名前が重複しているとここで例外が発生する
    #         eph = obj.ephemerides()

    #         # 4. Pandas DataFrameに変換
    #         df = eph.to_pandas()

    #         # 5. ファイル保存
    #         safe_name = str(target_id).replace(' ', '_').replace('/', '-')
    #         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    #         filename = f"horizons_{safe_name}_{timestamp}.csv"
    #         df.to_csv(filename, index=False)

    #         print(f"\n[SUCCESS] データを取得・保存しました。")
    #         print(f"FILE: {os.path.abspath(filename)}")
    #         print(f"ROWS: {len(df)}")
            
    #         print("\n--- Data Preview (First 5 rows) ---")
    #         print(df.head())

    #     except Exception as e:
    #         print(f"\n[ERROR] データの取得に失敗しました。")
    #         print(f"理由: {e}")
    #         print("-" * 40)
    #         if "Ambiguous target name" in str(e):
    #             print("【解決策】")
    #             print("ターゲット名が重複しています。名前に代わって以下のIDを指定してください。")
    #             print("  - 水星(本体)を指定する場合: '199'")
    #             print("  - 水星系重心を指定する場合: '1'")
    #             print("  - 金星なら '299', 火星なら '499', 木星なら '599'")
    #         elif "Location" in str(e) or "location" in str(e):
    #             print("【解決策】")
    #             print("観測場所の指定を確認してください。太陽中心なら '@sun'、地球中心なら '500@体番号' などが必要です。")
    #     return

    
    return




def test_create_band_flag():
    from messenger_analysis.detect_band.get_band_flag import get_band_flag

    cdf_filepath = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/event_flag_emic/2011/04/messenger_event_flag_emic_2011040208.cdf'
    dict_data = cdf.cdffile_to_dict(cdf_filepath)
    display.print_dict(dict_data)
    times = dict_data['times']
    freqs_norm = dict_data['freqs_norm']
    pytplot.store_data('event_flag_psd', {'x': dict_data['times'], 'y': dict_data['event_flag_psd'], 'v': dict_data['freqs_norm']})
    pytplot.store_data('event_flag_polarization', {'x': dict_data['times'], 'y': dict_data['event_flag_polarization'], 'v': dict_data['freqs_norm']})
    pytplot.store_data('event_flag_wna', {'x': dict_data['times'], 'y': dict_data['event_flag_wna'], 'v': dict_data['freqs_norm']})
    pytplot.store_data('event_flag_planarity', {'x': dict_data['times'], 'y': dict_data['event_flag_planarity'], 'v': dict_data['freqs_norm']})
    pytplot.store_data('event_flag_emic', {'x': dict_data['times'], 'y': dict_data['event_flag_emic'], 'v': dict_data['freqs_norm']})

    pytplot.options('event_flag_psd', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])
    pytplot.options('event_flag_polarization', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])
    pytplot.options('event_flag_wna', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])
    pytplot.options('event_flag_planarity', colormap='binary', yrange=[0, 1.1], zrange=[0, 1])
    pytplot.options('event_flag_emic', colormap='binary', yrange=[0, 0.2], zrange=[0, 1])

    freqs_norm = dict_data['freqs_norm']
    flag_emic = dict_data['event_flag_emic']
    freqs_band = [0, 1/23, 1/16, 1/4, 1/2, 1]
    band_flag = get_band_flag(
        flag_emic,
        freqs_norm,
        freqs_band=freqs_band
    )
    display.debug(f'{band_flag.shape=}')
    # freqs_norm_band_flag = []
    # for i in range(len(freqs_band)-1):
    #     value = (freqs_band[i] + freqs_band[i+1]) / 2
    #     freqs_norm_band_flag.append(value)
    
    pytplot.store_data('band_flag_emic', {'x': dict_data['times'], 'y': band_flag, 'v': np.linspace(0, 1, band_flag.shape[1])})
    pytplot.options('band_flag_emic', colormap='binary', zrange=[0, 1])

    mq16 = 1/16 * np.ones_like(times)
    mq23 = 1/23 * np.ones_like(times)
    pytplot.store_data('mq16', {'x': times, 'y': mq16})
    pytplot.store_data('mq23', {'x': times, 'y': mq23})
    pytplot.options('mq16', color='red', linestyle='dashed')
    pytplot.options('mq23', color='blue', linestyle='dashed')


    pytplot.tplot_names()
    pytplot.tplot(
        [
            'event_flag_psd',
            'event_flag_polarization',
            'event_flag_wna',
            'event_flag_planarity',
            ['event_flag_emic', 'mq16', 'mq23'],
            'band_flag_emic',
        ],
        save_png='out/test/create_band_flag.png'
    )

    return



# def test_getdata_orb():
#     getdata.messenger_orb(
#         ['2012-01-01 00:00:00', '2012-02-01 00:00:00'],
#         basedir_orb='/Volumes/SSD-PGCU3C/messenger/messenger_data/orb'
#     )
#     pytplot.tplot_names()
#     pytplot.tplot(
#         [
#             'orb_mso',
#             'orb_polar',
#             'orb_rmlatmlt',
#         ],
#         save_png='out/test/orb.png'
#     )
#     orbit.plot(
#         'orb_mso',
#         type='xyz',
#         savefig='out/test/orb_mso.png'
#     )
#     orbit.plot(
#         'orb_polar',
#         type='polar',
#         savefig='out/test/orb_polar.png'
#     )
#     orbit.plot(
#         'orb_rmlatmlt',
#         type='rmlatmlt',
#         savefig='out/test/orb_rmlatmlt.png'
#     )
#     return


# def test_create_orb_data():
#     from common.data_process.resampling import resample_data
#     from common.const.const_planets import RM
#     from messenger_analysis.analysis.create_orb import create_orb_data_from_cdf_filepath, create_orb_data

#     trange = ['2011-04-01 00:00:00', '2011-05-01 00:00:00']
#     create_orb_data(
#         trange,
#         basedir_mag_mso='/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso',
#         basedir_savecdf='/Volumes/SSD-PGCU3C/messenger/messenger_data/orb'
#     )

#     # cdf_filepath = '/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso/2011/03/messenger_mag_mso_20110323.cdf'
#     cdf_filepath = '/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso/2012/01/messenger_mag_mso_20120101.cdf'
#     savecdf = 'test.cdf'

#     create_orb_data_from_cdf_filepath(
#         cdf_filepath,
#         savecdf
#     )
#     pytplot.del_data()

#     dict_data = cdf.cdffile_to_dict(savecdf)
#     display.print_dict(dict_data)

#     pytplot.store_data('orb_mso', {'x': dict_data['times'], 'y': dict_data['orb_mso']})
#     pytplot.store_data('orb_polar', {'x': dict_data['times'], 'y': dict_data['orb_polar']})
#     pytplot.store_data('orb_rmlatmlt', {'x': dict_data['times'], 'y': dict_data['orb_rmlatmlt']})


#     # dict_data = cdf.cdffile_to_dict(cdf_filepath)
#     # pytplot.store_data('orb_mso_original', {'x': dict_data['time'], 'y': dict_data['pos']})

#     # # resampling
#     # dat_orb_mso_orig = pytplot.get_data('orb_mso_original')
#     # times_orig = dat_orb_mso_orig.times
#     # orb_mso_orig = dat_orb_mso_orig.y
#     # times, orb_mso = resample_data(times_orig, orb_mso_orig, target_sampling_rate=1/6)
#     # pytplot.store_data('orb_mso', {'x': times, 'y': orb_mso})

#     # orb = orb_mso / (RM * 1e-3)
#     # pytplot.store_data('orb_mso', {'x': times, 'y': orb}, replace=True)
#     # orbit.xyz2polar('orb_mso', 'orb_polar', to='polar')
#     # orbit.rmlatmlt2polar('orb_polar', 'orb_rmlatmlt', to='rmlatmlt')

#     # orb_mso_orig /= RM * 1e-3
#     # pytplot.store_data('orb_mso_original', {'x': times_orig, 'y': orb_mso_orig}, replace=True)
#     # orbit.xyz2polar('orb_mso_original', 'orb_original_polar', to='polar')
#     # orbit.rmlatmlt2polar('orb_original_polar', 'orb_original_rmlatmlt', to='rmlatmlt')

#     pytplot.tplot_names()
#     pytplot.tplot(
#         [
#             'orb_mso',
#             'orb_polar',
#             'orb_rmlatmlt',
#         ],
#         save_png='out/test/test_create_orb_data.png'
#     )

#     orbit.plot(
#         'orb_mso',
#         type='xyz',
#         savefig='out/test/test_create_orb_data_orbit_xyz.png'
#     )

#     orbit.plot(
#         'orb_polar',
#         type='polar',
#         savefig='out/test/test_create_orb_data_orbit_polar.png'
#     )


#     orbit.plot(
#         'orb_rmlatmlt',
#         type='rmlatmlt',
#         savefig='out/test/test_create_orb_data_orbit_rmlatmlt.png'
#     )
#     return


# def test_create_event_flag():
#     from messenger_analysis.analysis.create_event_flag import create_event_flag_emic_trange

#     # create cdf
#     trange = ['2011-03-25 00:00:00', '2011-03-25 02:00:00']
#     basedir_mag_mso = '/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso'
#     basedir_orb = '/Volumes/SSD-PGCU3C/messenger/messenger_data/orb'
#     create_event_flag_emic_trange(
#         trange,
#         basedir_mag_mso=basedir_mag_mso,
#         basedir_orb=basedir_orb,
#         save_all=True,
#         savecdf='test.cdf'
#     )
#     pytplot.tplot_names()
#     pytplot.del_data()

#     # read cdf
#     dict_data = cdf.cdffile_to_dict('test.cdf')
#     display.print_dict(dict_data)

#     times = dict_data['times']
#     freqs_norm = dict_data['freqs_norm']
#     pytplot.store_data('event_flag_psd_intensity', {'x': times, 'y': dict_data['event_flag_psd_intensity'], 'v': freqs_norm})
#     pytplot.store_data('event_flag_psd_ratio', {'x': times, 'y': dict_data['event_flag_psd_ratio'], 'v': freqs_norm})
#     pytplot.store_data('event_flag_psd', {'x': times, 'y': dict_data['event_flag_psd'], 'v': freqs_norm})
#     pytplot.store_data('event_flag_polarization', {'x': times, 'y': dict_data['event_flag_polarization'], 'v': freqs_norm})
#     pytplot.store_data('event_flag_wna', {'x': times, 'y': dict_data['event_flag_wna'], 'v': freqs_norm})
#     pytplot.store_data('event_flag_planarity', {'x': times, 'y': dict_data['event_flag_planarity'], 'v': freqs_norm})
#     pytplot.store_data('event_flag_emic', {'x': times, 'y': dict_data['event_flag_emic'], 'v': freqs_norm})
#     pytplot.options('event_flag_psd_intensity', yrange=[0, 1.1], colormap='binary')
#     pytplot.options('event_flag_psd_ratio', yrange=[0, 1.1], colormap='binary')
#     pytplot.options('event_flag_psd', yrange=[0, 1.1], colormap='binary')
#     pytplot.options('event_flag_polarization', yrange=[0, 1.1], colormap='binary')
#     pytplot.options('event_flag_wna', yrange=[0, 1.1], colormap='binary')
#     pytplot.options('event_flag_planarity', yrange=[0, 1.1], colormap='binary')
#     pytplot.options('event_flag_emic', yrange=[0, 1.1], colormap='binary')
#     pytplot.tplot_names()

#     pytplot.tplot(
#         [
#             'event_flag_psd_intensity',
#             'event_flag_psd_ratio',
#             'event_flag_psd',
#             'event_flag_polarization',
#             'event_flag_wna',
#             'event_flag_planarity',
#             'event_flag_emic',
#         ],
#         figsize=(12, 10),
#         save_png='out/test/create_event_flag.png'
#     )

#     return




# def test_classify_emic_bands(emic_flag, freqs_norm, freqs_band=[0, 0.25, 0.5, 1.0]):
#     """
#     emic_flag を指定された周波数バンドに振り分ける。
    
#     Args:
#         emic_flag (np.ndarray): (n_times, n_freqs) の 0 or 1 配列
#         freqs_norm (np.ndarray): 長さ n_freqs の規格化周波数配列
#         freqs_band (list): バンド境界のリスト (例: [0, 0.25, 0.5, 1])
        
#     Returns:
#         dict: 各バンド名をキーとし、その時間のフラグ (n_times,) を値に持つ辞書
#     """
#     n_times = emic_flag.shape[0]
#     results = {}

#     for i in range(len(freqs_band) - 1):
#         f_min = freqs_band[i]
#         f_max = freqs_band[i+1]
#         band_name = f'band_{f_min}_{f_max}'.replace('.', 'p')
        
#         # 1. 現在のバンドに含まれる周波数インデックスを取得
#         # ※ 境界条件(等号)は解析の目的に合わせて調整してください
#         idx_in_band = np.where((freqs_norm >= f_min) & (freqs_norm < f_max))[0]
        
#         if len(idx_in_band) == 0:
#             results[band_name] = np.zeros(n_times)
#             continue
            
#         # 2. そのバンド内において、いずれかの周波数で emic_flag が 1 であれば 1 とする (Any判定)
#         # もし「バンド内の半分以上が1なら」といった条件にする場合は np.mean > 0.5 などに変更可能
#         band_flag = np.any(emic_flag[:, idx_in_band] == 1, axis=1).astype(int)
        
#         results[band_name] = band_flag
        
#     return results


# def test_event_band():
#     from common import csv
#     from messenger_analysis.analysis.analysis import analysis
#     from messenger_analysis.event_search.get_event_flag import get_event_flag
#     from messenger_analysis.event_search._get_emic_flag import (
#         get_psd_flag,
#         get_polari_flag
#     )
#     from messenger_analysis.detect_band.get_band_flag import (
#         get_band_flag
#     )

#     csv_filepath_event = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/event/emic/2011/emic_event_201103.csv'
#     basedir_cdf = '/Volumes/SSD-PGCU3C/messenger/messenger_data/mag_mso'
#     # ------------------------
#     # create cdf
#     # ---------
#     trange = ['2011-05-19 23:00:00', '2011-05-20 00:00:00']
#     # trange_list = csv.get_trange_list(csv_filepath_event)
#     # display.print_list(trange_list)
#     # trange = trange_list[1]
#     # analysis(
#     #     trange,
#     #     basedir_cdf_files=basedir_cdf,
#     #     outcdf=True,
#     #     savecdf='test.cdf'
#     # )
#     # pytplot.tplot_names()
#     # ---------

#     pytplot.del_data()

#     cdf_filepath = 'test.cdf'
#     dict_data = cdf.cdffile_to_dict(cdf_filepath)
#     display.debug(f'{dict_data.keys()=}')
#     times = dict_data['times']
#     display.debug(f'{times[1] - times[0] =}')
#     freqs_norm = dict_data['freqs_norm']
#     pytplot.store_data('psd_norm_x', {'x': times, 'y': dict_data['psd_norm_x'], 'v': freqs_norm})
#     pytplot.store_data('psd_norm_y', {'x': times, 'y': dict_data['psd_norm_y'], 'v': freqs_norm})
#     pytplot.store_data('psd_norm_z', {'x': times, 'y': dict_data['psd_norm_z'], 'v': freqs_norm})
#     pytplot.store_data('polarization_norm', {'x': times, 'y': dict_data['polarization_norm'], 'v': freqs_norm})
#     pytplot.options('psd_norm_x', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1.1])
#     pytplot.options('psd_norm_y', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1.1])
#     pytplot.options('psd_norm_z', colormap='jet', zrange=[5, 5e3], zlog=True, yrange=[0, 1.1])
#     pytplot.options('polarization_norm', colormap='jet', zrange=[-1, 1], yrange=[0, 1.1])

#     # event
#     # threshold_psd=1e3,
#     # threshold_ratio=10,
#     # threshold_polari=-0.5,
#     # psd_norm_x = pytplot.get_data('psd_norm_x').y
#     # psd_norm_y = pytplot.get_data('psd_norm_y').y
#     # psd_norm_z = pytplot.get_data('psd_norm_z').y
#     # polari_norm = pytplot.get_data('polarization_norm').y
#     # psd_flag = get_psd_flag(
#     #     psd_norm_x,
#     #     psd_norm_y,
#     #     psd_norm_z,
#     #     threshold_psd=threshold_psd,
#     #     threshold_ratio=threshold_ratio
#     # )
#     # polari_flag = get_polari_flag(
#     #     polari_norm,
#     #     threshold_polari=threshold_polari
#     # )

#     get_event_flag(
#         'psd_norm_x',
#         'psd_norm_y',
#         'psd_norm_z',
#         'polarization_norm',
#         threshold_psd=1e3,
#         threshold_ratio=10,
#         threshold_polari=-0.5,
#     )

#     emic_flag = pytplot.get_data('event_flag_emic').y

#     # バンド振り分け実行
#     freqs_band = [0, 0.25, 0.5, 1.0]
#     band_flag = get_band_flag(emic_flag, freqs_norm, freqs_band)
#     # band_results = classify_emic_bands(emic_flag, freqs_norm, freqs_band)

#     mq1_norm = np.ones_like(times)
#     mq2_norm = 1/2 * np.ones_like(times)
#     mq4_norm = 1/4 * np.ones_like(times)
#     mq16_norm = 1/16 * np.ones_like(times)
#     pytplot.store_data('mq1_norm', {'x': times, 'y': mq1_norm})
#     pytplot.store_data('mq2_norm', {'x': times, 'y': mq2_norm})
#     pytplot.store_data('mq4_norm', {'x': times, 'y': mq4_norm})
#     pytplot.store_data('mq16_norm', {'x': times, 'y': mq16_norm})
#     pytplot.options('mq1_norm', color='blue', linestyle='dashed')
#     pytplot.options('mq2_norm', color='green', linestyle='dashed')
#     pytplot.options('mq4_norm', color='red', linestyle='dashed')
#     # pytplot.options('mq16_norm', color='red', linestyle='dashed')
    
#     # pytplot に各バンドの結果を格納 (可視化用)
#     vars_plot = [
#         'psd_norm_x',
#         'psd_norm_y',
#         'psd_norm_z',
#         ['polarization_norm', 'mq1_norm', 'mq2_norm', 'mq4_norm'], 
#         ['event_flag_emic', 'mq1_norm', 'mq2_norm', 'mq4_norm']
#     ]
    
#     # for band_name, flag_data in band_results.items():
#     #     pytplot.store_data(band_name, {'x': times, 'y': flag_data})
#     #     plot_names.append(band_name)

#     for i in range(band_flag.shape[1]):
#         pytplot.store_data(f'band_flag_{i}', {'x': times, 'y': band_flag[:, i]})
#         vars_plot.append(f'band_flag_{i}')

#     pytplot.tplot_names()
        
#     # プロット出力
#     pytplot.tplot(
#         vars_plot,
#         figsize=(12, 15),
#         save_png='out/test/event.png'
#     )
    


#     # pytplot.tplot(
#     #     [
#     #         'psd_norm_x',
#     #         'psd_norm_y',
#     #         'psd_norm_z',
#     #         'polarization_norm',
#     #         'event_flag_emic',
#     #         'event_flag_dense',
#     #     ],
#     #     figsize=(12, 12),
#     #     save_png='out/test/event.png'
#     # )


#     return



# def test_dist_freq_fcp():
#     from messenger_analysis.analysis import (
#         mag_analysis,
#         spec_analysis
#     )
#     from messenger_analysis.distribution.freq_over_fcp import (
#         get_representative_freqs_norm_from_spectrogram
#     )
#     from messenger_analysis.analysis.dist_freq_over_fcp import (
#         get_rmlatmlt_meshgrid_single_step,
#         get_rmlatmlt_meshgrid
#     )
#     display.set_log_level('DEBUG')

#     trange = ['2011-03-23 14:00:00', '2012-01-01 01:00:00']

#     get_rmlatmlt_meshgrid(trange, basedir_savecdf='test_dist_fcp')
#     # pytplot.tplot_names()
#     # pytplot.options('freqs_norm_representative_xy', color='pink')
#     # pytplot.options('freqs_norm_representative_z', color='pink')
#     # pytplot.tplot(
#     #     [
#     #         'psd_norm_xy_below_fcp',
#     #         'psd_norm_z_below_fcp',
#     #         'freqs_norm_representative_xy',
#     #         'freqs_norm_representative_z'
#     #     ],
#     #     save_png='out/test/dist_freq_fcp_represent.png'
#     # )

#     # --------------------------------
#     # getdata.messenger_mag(trange)
#     # getdata.messenger_orb(trange)
#     # mag_analysis(
#     #     resampling_rate=20,
#     #     average_window_mfa_sec=30
#     # )
#     # spec_analysis(
#     #     resampling_rate=20,
#     #     spec_window_size=1024,
#     #     spec_rate_overlap=.9,
#     #     average_window_sec=10
#     # )

#     # dat_psd_norm_x = pytplot.get_data('mag_mfa_x_dpwrspc_psd_norm')
#     # times = dat_psd_norm_x.times
#     # freqs_norm = dat_psd_norm_x.v
#     # psd_norm_x = dat_psd_norm_x.y

#     # idx_fcp = util.get_closest_idx(freqs_norm, 1, mode='over')

#     # freqs_norm_below_fcp = freqs_norm[:idx_fcp]
#     # psd_norm_x_below_fcp = psd_norm_x[:, :idx_fcp]

#     # display.debug(f'{np.max(freqs_norm_below_fcp)=}')

#     # freqs_norm_representative = get_representative_freqs_norm_from_spectrogram(
#     #     times,
#     #     freqs_norm_below_fcp,
#     #     psd_norm_x_below_fcp
#     # )
#     # pytplot.store_data('psd_norm_x_below_fcp', {'x': times, 'y': psd_norm_x_below_fcp, 'v': freqs_norm_below_fcp})
#     # pytplot.options('psd_norm_x_below_fcp', zlog=True, zrange=[5, 5e3], yrange=[0, 1.1], colormap='jet')
#     # pytplot.store_data('freqs_norm_representative', {'x': times, 'y': freqs_norm_representative})

#     # pytplot.tplot_names()

#     # pytplot.tplot(
#     #     [
#     #         'psd_norm_x_below_fcp',
#     #         'freqs_norm_representative'
#     #     ],
#     #     save_png='out/test/dist_freq_fcp.png'
#     # )

#     return



# def test_dist_intensity():
#     from messenger_analysis.distribution.intensity import (
#         get_intensity_dist_trange_list
#     )
#     from common.distribution import plot_rmlatmlt
#     from common.cdf.cdfdata import cdffile_to_dict

#     from messenger_analysis.analysis import (
#         mag_analysis,
#         spec_analysis,
#     )
#     from messenger_analysis.distribution._dwell_time import (
#         get_trange_list_from_csvs,
#         get_dwell_time_trange_list,
#         get_dwell_time_trange_with_ref
#     )

#     display.set_log_level('DEBUG')

#     trange = ['2011-03-01 00:00:00', '2011-04-01 02:00:00']
#     # parameters
#     # ---------------------------------
#     resampling_rate = 20
#     average_window_mfa_sec=30
#     spec_window_size=1024
#     spec_rate_overlap=.9
#     average_window_sec = 10
#     # bins setting
#     r_bins = np.arange(1, 7+.5, .5)
#     mlt_bins = np.arange(0, 24+1, 1)
#     mlat_bins = np.arange(-90, 90+5, 5)
#     # ---------------------------------

#     # event time distribution
#     # csv_filelist = []
#     # base_dir = '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/emic_event/'
#     # time_list = util.make_time_list(trange, 1, 'months')
#     # for time_list_i in time_list:
#     #     dt_start = time.convert(time_list_i[0], frm='str', into='datetime')
#     #     year = dt_start.year
#     #     month = dt_start.month
#     #     csv_filepath = os.path.join(base_dir, f'{year}/emic_event_{year:04}{month:02}.csv')
#     #     csv_filelist.append(csv_filepath)
#     # trange_list = get_trange_list_from_csvs(csv_filelist)

#     # savecdf = os.path.join(
#     #     '/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis', 
#     #     'dist/intensity/dist_intensity_trange_list.cdf'
#     # )

#     # dict_intensity_meshgrid = get_intensity_dist_trange_list(
#     #     trange_list,
#     #     resampling_rate=resampling_rate,
#     #     average_window_mfa_sec=average_window_mfa_sec,
#     #     spec_window_size=spec_window_size,
#     #     spec_rate_overlap=spec_rate_overlap,
#     #     average_window_sec=average_window_sec,
#     #     r_bins=r_bins,
#     #     mlt_bins=mlt_bins,
#     #     mlat_bins=mlat_bins,
#     #     savecdf=savecdf
#     # )

#     dict_intensity_meshgrid = cdffile_to_dict('/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis/dist/intensity/dist_intensity_trange_list.cdf')

#     plot_rmlatmlt(
#         dict_intensity_meshgrid['mesh_theta_rmlt'],
#         dict_intensity_meshgrid['mesh_r_rmlt'],
#         dict_intensity_meshgrid['rmlt_intensity_avg'],
#         dict_intensity_meshgrid['mesh_theta_rmlat'],
#         dict_intensity_meshgrid['mesh_r_rmlat'],
#         dict_intensity_meshgrid['rmlat_intensity_avg'],
#         savefig='out/test/dist_intensity_trange_list.png',
#         suptitle=f'Distribution of intensity in event lists: {trange=}',
#         zlabel_rmlt='Average intensity [$nT^2/Hz$]',
#         zlabel_rmlat='Average intensity [$nT^2/Hz$]',
#         pos_label_rmlat=1.8
#     )

#     plot_rmlatmlt(
#         dict_intensity_meshgrid['mesh_theta_rmlt'],
#         dict_intensity_meshgrid['mesh_r_rmlt'],
#         dict_intensity_meshgrid['rmlt_count'],
#         dict_intensity_meshgrid['mesh_theta_rmlat'],
#         dict_intensity_meshgrid['mesh_r_rmlat'],
#         dict_intensity_meshgrid['rmlat_count'],
#         savefig='out/test/dist_count_trange_list.png',
#         suptitle=f'Distribution of counts in event lists: {trange=}',
#         zlabel_rmlt='Counts',
#         zlabel_rmlat='Counts',
#         pos_label_rmlat=1.8
#     )

#     # # meshgrid
#     # # (r, mlt)
#     # theta_mlt = (mlt_bins / 24) * 2 * np.pi
#     # mesh_theta_rmlt, mesh_r_rmlt = np.meshgrid(theta_mlt, r_bins)
#     # # (r, mlat)
#     # theta_mlat = np.deg2rad(mlat_bins)  # -90度～90度 → -π/2～π/2ラジアン
#     # mesh_theta_rmlat, mesh_r_rmlat = np.meshgrid(theta_mlat, r_bins)

#     # # getdata
#     # getdata.messenger_mag(trange)
#     # getdata.messenger_orb(trange)

#     # mag_analysis(
#     #     resampling_rate=resampling_rate,
#     #     average_window_mfa_sec=average_window_mfa_sec
#     # )

#     # spec_analysis(
#     #     resampling_rate=resampling_rate,
#     #     spec_window_size=spec_window_size,
#     #     spec_rate_overlap=spec_rate_overlap,
#     #     average_window_sec=average_window_sec
#     # )


#     # dict_intenstiy_dist = get_intensity_meshgrid(
#     #     'pos_rmlatmlt',
#     #     'mag_mfa_x_dpwrspc_psd',
#     #     r_bins=r_bins,
#     #     mlt_bins=mlt_bins,
#     #     mlat_bins=mlat_bins,
#     # )

    

#     return


# def test_event_dist():
#     from messenger_analysis.distribution._dwell_time import (
#         get_dwell_time,
#         get_trange_list_from_csv,
#         get_dwell_time_trange_list
#     )
#     from common.distribution._plot import plot_rmlatmlt
    
#     csv_filepath = '/Volumes/SSD-PGCU3C/messenger/emic_event/2011/emic_event_201103.csv'
#     trange_list = get_trange_list_from_csv(csv_filepath)

#     # trange = [trange_list[0][0], trange_list[-1][1]]

#     # bins setting
#     r_bins = np.arange(1, 7+.5, .5)
#     mlt_bins = np.arange(0, 24+1, 1)
#     mlat_bins = np.arange(-90, 90+5, 5)

#     # dwell time in event list
#     dict_orb_meshgrid_event = get_dwell_time_trange_list(
#         trange_list,
#         r_bins=r_bins,
#         mlt_bins=mlt_bins,
#         mlat_bins=mlat_bins
#     )
#     plot_rmlatmlt(
#         dict_orb_meshgrid_event['mesh_theta_rmlt'],
#         dict_orb_meshgrid_event['mesh_r_rmlt'],
#         dict_orb_meshgrid_event['rmlt_grid'],
#         dict_orb_meshgrid_event['mesh_theta_rmlat'],
#         dict_orb_meshgrid_event['mesh_r_rmlat'],
#         dict_orb_meshgrid_event['rmlat_grid'],
#         savefig='out/test/orb_dwell_time_trange_list.png',
#         suptitle='Dwell time in event lists'
#     )
    
#     return


# def test_create_reference_dwell_time():
#     from messenger_analysis.distribution._dwell_time import (
#         create_ref_dwell_cdf
#     )
#     r_bins = np.arange(1, 7+.5, .5)
#     mlt_bins = np.arange(0, 24+1, 1)
#     mlat_bins = np.arange(-90, 90+5, 5)
#     create_ref_dwell_cdf(
#         ['2011-03-01 00:00:00', '2011-08-01 00:00:00'],
#         parent_dir_save_cdf='/Volumes/SSD-PGCU3C/messenger/messenger_data_analysis',
#         savename='ref_dwell',
#         r_bins=r_bins,
#         mlt_bins=mlt_bins,
#         mlat_bins=mlat_bins,
#     )
#     return


# def test_search_emic_events():
#     from messenger_analysis.analysis.search_emic_events import (
#         _search_emic_events_trange
#     )
#     # trange = ['2011-03-25 00:00:00', '2011-03-25 02:00:00']
#     # trange = ['2012-03-05 16:00:00', '2012-03-05 17:00:00']
#     # trange = ['2011-04-01 08:00:00', '2011-04-01 10:00:00']
#     trange = ['2011-09-10 03:00:00', '2011-09-10 04:00:00']
#     threshold_psd = 1000
#     threshold_ratio = 10
#     threshold_polari=-0.5
#     min_event_delta_time=60
#     min_event_delta_freq=0.1
#     merge_timespan=300

#     df = _search_emic_events_trange(
#         trange,
#         threshold_psd=threshold_psd,
#         threshold_ratio=threshold_ratio,
#         threshold_polari=threshold_polari,
#         min_event_delta_time=min_event_delta_time,
#         min_event_delta_freq=min_event_delta_freq,
#         merge_timespan=merge_timespan
#     )
#     print(df)

#     dat_event_flag_dense = pytplot.get_data('event_flag_dense')
#     pytplot.store_data('mq1_norm', {'x': dat_event_flag_dense.times, 'y': np.ones(len(dat_event_flag_dense.times))}, replace=True)
#     pytplot.tplot_names()

#     # plot
#     yrange = [0, 1.1]
#     pytplot.options('mag_mfa_x_dpwrspc_psd_norm', yrange=yrange)
#     pytplot.options('mag_mfa_y_dpwrspc_psd_norm', yrange=yrange)
#     pytplot.options('mag_mfa_z_dpwrspc_psd_norm', yrange=yrange)
#     pytplot.options('polarization_norm', yrange=yrange)
#     pytplot.options('event_flag_psd', yrange=yrange)
#     pytplot.options('event_flag_polari', yrange=yrange)
#     pytplot.options('event_flag', yrange=yrange)
#     pytplot.options('event_flag_dense', yrange=yrange)
#     pytplot.options('event_flag_emic', yrange=yrange)
#     pytplot.options('mq1_norm', color='magenta', linestyle='--', linewidth=[2])

#     suptitle = f'{trange=}\n{threshold_psd=}, {threshold_ratio=}, {threshold_polari=}, {min_event_delta_time=}, {min_event_delta_freq}, {merge_timespan=}'
#     pytplot.tplot(
#         [
#             ['mag_mfa_x_dpwrspc_psd_norm', 'mq1_norm'],
#             ['mag_mfa_y_dpwrspc_psd_norm', 'mq1_norm'],
#             ['mag_mfa_z_dpwrspc_psd_norm', 'mq1_norm'],
#             ['polarization_norm', 'mq1_norm'],
#             ['event_flag_psd', 'mq1_norm'],
#             ['event_flag_polari', 'mq1_norm'],
#             ['event_flag', 'mq1_norm'],
#             ['event_flag_emic', 'mq1_norm'],
#             ['event_flag_dense', 'mq1_norm'],
#         ], 
#         figsize=(12, 10),
#         save_png='out/test/search_emic.png',
#         suptitle=suptitle,
#         xlim=trange,
#     )
#     return


# def test_download_mag_mso():
#     trange = ['2008-01-10 00:00:00', '2008-01-20 00:00:00']

#     getdata.download_mag_mso(
#         trange,
#         download_dir='test_download'
#     )

#     # urls = getdata.build_download_url_by_trange(
#     #     trange
#     # )
#     # for i, url in enumerate(urls):
#     #     print('-' * 20)
#     #     print(f'{i} {url}')
#     #     print('-' * 20)
#     #     getdata._download_pds_tab_file(
#     #         url,
#     #         output_dir='test_download'
#     #     )


#     # url = 'https://pds-ppi.igpp.ucla.edu/ditdos/download?id=urn:nasa:pds:mess-mag-calibrated:data-mso:magmsosci08012::1.0&slot=/data/mess-mag-calibrated/data/mso/2008/001_031_JAN&file_name=MAGMSOSCI08012_V08.xml&data_file=MAGMSOSCI08012_V08.TAB'
#     # url = 'https://pds-ppi.igpp.ucla.edu/ditdos/download?id=urn:nasa:pds:mess-mag-calibrated:data-mso:magmsosci11082::1.0&slot=/data/mess-mag-calibrated/data/mso/2011/060_090_MAR&file_name=MAGMSOSCI11082_V08.xml&data_file=MAGMSOSCI11082_V08.TAB'
#     # getdata._download_pds_tab_file(
#     #     url,
#     #     output_dir='test_download'
#     # )
#     return




# def test_convert_tab_to_cdf():
#     # filepath = 'test_download/MAGMSOSCI08012_V08.TAB'
#     filepath = 'test_download/MAGMSOSCI11082_V08.TAB'
#     getdata.tab_to_cdf(
#         filepath,
#         'test_download/test.cdf'
#     )
#     return



# def test_data_time():
#     filepath = 'messenger_data/mag_mso/2008/01/messenger_mag_mso_20080112.cdf'
#     cdf.info(filepath)
#     times = cdf.get_data(filepath, 'time')
#     mag = cdf.get_data(filepath, 'mag')


#     # trange = ['2012-03-12 00:00:00', '2012-03-12 02:00:00']
#     # getdata.messenger_mag(trange)
#     # dat_mag = pytplot.get_data('mag')
#     # times = dat_mag.times
#     for i in range(len(times)):
#         print(f'{i} {times[i]=}')
#         if i == 100:
#             break

#     pytplot.tplot_names()
#     pytplot.tplot(
#         ['mag'],
#         xlim=['2012-03-12 00:00:00', '2012-03-12 00:01:00']
#     )
#     return



# def test_event_search():
#     trange = ['2011-03-25 00:00:00', '2011-03-25 02:00:00']
#     # trange = ['2012-03-05 16:00:00', '2012-03-05 17:00:00']

#     # df = analysis._search_emic_events_trange(trange)
#     # print(df)

#     threshold_psd = 1e3
#     threshold_ratio = 1


#     # # params
#     params = {
#         'resampling_rate': 20,
#         'spec_window_size': 1024,
#         'spec_rate_overlap': .9,
#         'average_window_sec': 10
#     }

#     # analysis -> output cdf
#     # ----------------------
#     strstart = time.convert(trange[0], frm='str', into='str', out_fmt='%Y%m%d%H')
#     savecdf = f'messenger_data_analysis/event_search/messenger_event_flag_{strstart}.cdf'

#     analysis.analysis(
#         trange,
#         resampling_rate=params['resampling_rate'],
#         spec_window_size=params['spec_window_size'],
#         spec_rate_overlap=params['spec_rate_overlap'],
#         average_window_sec=params['average_window_sec'],
#         outcdf=True,
#         savecdf=savecdf
#     )
#     # ----------------------

#     cdf_filepath = 'messenger_data_analysis\event_search\messenger_event_flag_2011032422.cdf'
#     # cdf_filepath = 'messenger_data_analysis\event_search\messenger_event_flag_2011032500.cdf'
#     # cdf_filepath = 'messenger_data_analysis\event_search\messenger_event_flag_2011032502.cdf'
#     # cdf_filepath = 'messenger_data_analysis\event_search\messenger_event_flag_2011032504.cdf'
#     cdf.info(cdf_filepath)
#     times = cdf.get_data(cdf_filepath, 'times')
#     freqs = cdf.get_data(cdf_filepath, 'freqs_norm')
#     psd_norm_x = cdf.get_data(cdf_filepath, 'psd_norm_x')
#     psd_norm_y = cdf.get_data(cdf_filepath, 'psd_norm_y')
#     psd_norm_z = cdf.get_data(cdf_filepath, 'psd_norm_z')
#     polari_norm = cdf.get_data(cdf_filepath, 'polarization_norm')

#     pytplot.store_data('mag_mfa_x_dpwrspc_psd_norm', {'x': times, 'y': psd_norm_x, 'v': freqs})
#     pytplot.options('mag_mfa_x_dpwrspc_psd_norm', zlog=True, zrange=[5, 5e3], yrange=[0, 1.1], colormap='jet')
#     pytplot.store_data('mag_mfa_y_dpwrspc_psd_norm', {'x': times, 'y': psd_norm_y, 'v': freqs})
#     pytplot.options('mag_mfa_y_dpwrspc_psd_norm', zlog=True, zrange=[5, 5e3], yrange=[0, 1.1], colormap='jet')
#     pytplot.store_data('mag_mfa_z_dpwrspc_psd_norm', {'x': times, 'y': psd_norm_z, 'v': freqs})
#     pytplot.options('mag_mfa_z_dpwrspc_psd_norm', zlog=True, zrange=[5, 5e3], yrange=[0, 1.1], colormap='jet')
#     pytplot.store_data('polarization_norm', {'x': times, 'y': polari_norm, 'v': freqs})
#     pytplot.options('polarization_norm', zrange=[-1, 1], yrange=[0, 1.1], colormap='jet')

#     event_search.get_event_flag(
#         'mag_mfa_x_dpwrspc_psd_norm',
#         'mag_mfa_y_dpwrspc_psd_norm',
#         'mag_mfa_z_dpwrspc_psd_norm',
#         'polarization_norm',
#         threshold_psd=threshold_psd,
#         threshold_ratio=threshold_ratio
#     )

#     flag = pytplot.get_data('event_flag').y
#     flag_dense = pytplot.get_data('event_flag_dense').y
#     # flag_dense = event_search.get_dense_flag(flag, min_density=.5)

#     event_times, event_freqs = event_search.extract_event(
#         times,
#         freqs,
#         flag_dense,
#         # min_event_delta_time=5,
#         # min_event_delta_freq=.01
#     )
#     for i, (event_time, event_freq) in enumerate(zip(event_times, event_freqs)):
#         print(f'{i} {time.convert(event_time, frm='unix', into='str')}, {event_freq}')

#     # plot
#     pytplot.tplot_names()
#     suptitle = f'{threshold_psd=}, {threshold_ratio=}'
#     pytplot.tplot(
#         [
#             'mag_mfa_x_dpwrspc_psd_norm',
#             'mag_mfa_y_dpwrspc_psd_norm',
#             'mag_mfa_z_dpwrspc_psd_norm',
#             'polarization_norm',
#             'event_flag',
#             'event_flag_dense'
#         ],
#         figsize=(12, 8),
#         save_png='out/test/event_search.png',
#         # suptitle=suptitle
#     )


#     return




# def test_emic_event_search():
    
#     # df = analysis._search_emic_events_trange(trange)
#     # print(df)

#     # pytplot.tplot_names()
#     # pytplot.tplot(
#     #     [
#     #         'mag_mfa_x_dpwrspc_psd_norm',
#     #         'mag_mfa_y_dpwrspc_psd_norm',
#     #         'mag_mfa_z_dpwrspc_psd_norm',
#     #         'polarization_norm',
#     #         'event_flag',
#     #         'event_flag_dense'
#     #     ],
#     #     figsize=(12, 8),
#     #     save_png='out/test/emic_event_search.png',
#     #     # suptitle=suptitle
#     # )


#     return



# def rename_files_by_pattern(directory_path, dry_run=True):
#     """
#     ディレクトリ内のPNGファイルの名前を古いパターンから新しいパターンにリネームする。

#     古いパターン: erg_pwe_wfc_l1p_1khz_polarization_{year}{month}{day}{hour}.png
#     新しいパターン: messenger_mag_mso_spectrogram_{year}{month}{day}{hour}.png

#     Parameters:
#     directory_path (str): 対象のディレクトリパス。
#     dry_run (bool): Trueの場合、リネームを実行せずに出力のみ表示する。
#     """
#     # 1. 日時文字列を抽出するための正規表現パターン
#     # {year}{month}{day}{hour} の部分は 8桁の日付 + 2桁の時間の計10桁の数字
#     old_pattern = re.compile(r'^erg_pwe_wfc_l1p_1khz_polarization_(\d{12})\.png$')
    
#     # 新しいファイル名のプレフィックス
#     new_prefix = 'messenger_mag_mso_spectrogram_'
    
#     print(f"--- リネーム処理開始 (Dry Run: {dry_run}) ---")
    
#     # ディレクトリ内のファイルを走査
#     for filename in os.listdir(directory_path):
        
#         # 2. 古いパターンに一致するか確認
#         match = old_pattern.match(filename)
        
#         if match:
#             # 3. 日時文字列を抽出
#             datetime_str = match.group(1) # 例: '2017010112'
            
#             # 4. 新しいファイル名を構築
#             new_filename = f"{new_prefix}{datetime_str}.png"
            
#             old_filepath = os.path.join(directory_path, filename)
#             new_filepath = os.path.join(directory_path, new_filename)
            
#             print(f"  [OLD]: {filename}")
#             print(f"  [NEW]: {new_filename}")
            
#             # 5. リネームの実行 (dry_runがFalseの場合)
#             if not dry_run:
#                 try:
#                     os.rename(old_filepath, new_filepath)
#                     print(f"  Renamed successfully.")
#                 except Exception as e:
#                     print(f"  Error renaming {filename}: {e}")
            
#             print("-" * 20)
            
#     if dry_run:
#         print("--- Dry Run 完了。実際にリネームするには dry_run=False に設定してください。---")
#     else:
#         print("--- リネーム処理完了 ---")


# def rename_files():
#     for year in range(2008, 2016):
#         for month in range(1, 13):
#             dirpath = f"E:/messenger/ql/mag/2h/spectrogram_norm/{year:04}/{month:02}"
#             if not os.path.exists(dirpath):
#                 continue
            
#             rename_files_by_pattern(
#                 dirpath,
#                 dry_run=False
#             )
#     return


# def test_gmail():
#     sender = gmail.GmailSender()

#     # メール送信情報を設定
#     sender_email = 'kikuchi.riku.s2@dc.tohoku.ac.jp'
#     receiver_email = 'kikuchi.riku.s2@dc.tohoku.ac.jp'
#     subject = 'test'
#     body = 'This is test mail via python code'
    
#     # メールを送信
#     if sender.service:
#         sender.send_message(sender_email, receiver_email, subject, body)
#     return


# def test_pytplot():
#     t = np.linspace(0, 100, 1000)
#     dates = pd.date_range('2020-01-01 00:00:00', '2020-01-01 01:00:00', 1000)
#     y = np.sin(t)
#     pytplot.store_data('sin', {'x': dates, 'y': y})

#     dat = pytplot.get_data('sin')
#     print(f'{dat.times=}')

#     ret_stft = spec._stft(t, y, window_size=10)
#     times = ret_stft['times']
#     freqs = ret_stft['freqs']
#     psd = ret_stft['spectrogram_psd']
#     print(f'{psd.shape=}')
#     pytplot.store_data('psd', {'x': times, 'y': psd, 'v': freqs})
#     pytplot.tplot_names()
#     opt = pytplot.get_data('sin', get_options=True)
#     print(f'{opt=}')
#     pytplot.options('sin', linestyle='-', color='orange', legend_names='sin', legend=True)
#     pytplot.tplot(
#         [
#             'sin',
#             # ['psd', 'sin']
#         ],
#         delta_xticks=30,
#         timeunit_xticks='minutes',
#     )


#     return


# def read_tab_file_fixed_width(file_path):
#     """
#     固定幅フォーマットのTABファイルを読み込む
    
#     Parameters:
#     file_path (str): TABファイルのパス
    
#     Returns:
#     pandas.DataFrame: 読み込んだデータ
#     """
#     # フィールド定義（XMLファイルから取得）
#     field_definitions = [
#         ('YEAR', 1, 4, 'i'),           # 整数
#         ('DAY_OF_YEAR', 6, 3, 'i'),    # 整数
#         ('HOUR', 10, 2, 'i'),          # 整数
#         ('MINUTE', 13, 2, 'i'),        # 整数
#         ('SECOND', 16, 6, 'f'),        # 浮動小数点
#         ('TIME_TAG', 23, 13, 'f'),     # 浮動小数点
#         ('X_MSO', 37, 14, 'f'),        # 浮動小数点
#         ('Y_MSO', 52, 14, 'f'),        # 浮動小数点
#         ('Z_MSO', 67, 14, 'f'),        # 浮動小数点
#         ('BX_MSO', 82, 10, 'f'),       # 浮動小数点
#         ('BY_MSO', 93, 10, 'f'),       # 浮動小数点
#         ('BZ_MSO', 104, 10, 'f')       # 浮動小数点
#     ]
    
#     data = []
    
#     with open(file_path, 'r') as file:
#         for line_num, line in enumerate(file, 1):
#             if len(line.strip()) == 0:
#                 continue
                
#             row = {}
#             for field_name, start_pos, length, data_type in field_definitions:
#                 # 1ベースの位置を0ベースに変換
#                 start_idx = start_pos - 1
#                 end_idx = start_idx + length
                
#                 if end_idx > len(line):
#                     print(f"Warning: Line {line_num} is too short. Expected at least {end_idx} characters, got {len(line)}")
#                     break
                
#                 field_value = line[start_idx:end_idx].strip()
                
#                 try:
#                     if data_type == 'i':
#                         row[field_name] = int(field_value)
#                     elif data_type == 'f':
#                         row[field_name] = float(field_value)
#                     else:
#                         row[field_name] = field_value
#                 except ValueError as e:
#                     print(f"Warning: Could not parse field {field_name} at line {line_num}: '{field_value}' - {e}")
#                     row[field_name] = None
            
#             if len(row) == len(field_definitions):
#                 data.append(row)
    
#     return pd.DataFrame(data)

# def read_tab_file_pandas(file_path):
#     """
#     pandasを使用してTABファイルを読み込む（より高速）
    
#     Parameters:
#     file_path (str): TABファイルのパス
    
#     Returns:
#     pandas.DataFrame: 読み込んだデータ
#     """
#     # 固定幅フォーマットの定義
#     colspecs = [
#         (0, 4),    # YEAR
#         (5, 8),    # DAY_OF_YEAR
#         (9, 11),   # HOUR
#         (12, 14),  # MINUTE
#         (15, 21),  # SECOND
#         (22, 35),  # TIME_TAG
#         (36, 50),  # X_MSO
#         (51, 65),  # Y_MSO
#         (66, 80),  # Z_MSO
#         (81, 91),  # BX_MSO
#         (92, 102), # BY_MSO
#         (103, 113) # BZ_MSO
#     ]
    
#     column_names = [
#         'YEAR', 'DAY_OF_YEAR', 'HOUR', 'MINUTE', 'SECOND',
#         'TIME_TAG', 'X_MSO', 'Y_MSO', 'Z_MSO', 'BX_MSO', 'BY_MSO', 'BZ_MSO'
#     ]
    
#     try:
#         df = pd.read_fwf(file_path, colspecs=colspecs, names=column_names)
#         return df
#     except Exception as e:
#         print(f"Error reading file with pandas: {e}")
#         return None

# def create_datetime_column(df):
#     """
#     DataFrameにdatetime列を追加する
    
#     Parameters:
#     df (pandas.DataFrame): 元のデータフレーム
    
#     Returns:
#     pandas.DataFrame: datetime列が追加されたデータフレーム
#     """
#     # datetime列を作成
#     df['datetime'] = pd.to_datetime(
#         df['YEAR'].astype(str) + '-' + 
#         df['DAY_OF_YEAR'].astype(str).str.zfill(3) + ' ' + 
#         df['HOUR'].astype(str).str.zfill(2) + ':' + 
#         df['MINUTE'].astype(str).str.zfill(2) + ':' + 
#         df['SECOND'].astype(str),
#         format='%Y-%j %H:%M:%S.%f',
#         errors='coerce'
#     )
    
#     return df

# def analyze_messenger_data(df):
#     """
#     MESSENGERデータの基本的な分析を行う
    
#     Parameters:
#     df (pandas.DataFrame): 読み込んだデータフレーム
#     """
#     print("=== MESSENGER磁力計データ分析 ===")
#     print(f"データレコード数: {len(df)}")
#     print(f"データ期間: {df['datetime'].min()} から {df['datetime'].max()}")
#     print(f"データ期間の長さ: {df['datetime'].max() - df['datetime'].min()}")
    
#     print("\n=== 磁場データの統計 ===")
#     print(f"BX_MSO - 平均: {df['BX_MSO'].mean():.2f} nT, 標準偏差: {df['BX_MSO'].std():.2f} nT")
#     print(f"BY_MSO - 平均: {df['BY_MSO'].mean():.2f} nT, 標準偏差: {df['BY_MSO'].std():.2f} nT")
#     print(f"BZ_MSO - 平均: {df['BZ_MSO'].mean():.2f} nT, 標準偏差: {df['BZ_MSO'].std():.2f} nT")
    
#     print("\n=== 位置データの統計 ===")
#     print(f"X_MSO - 範囲: {df['X_MSO'].min():.2f} から {df['X_MSO'].max():.2f} km")
#     print(f"Y_MSO - 範囲: {df['Y_MSO'].min():.2f} から {df['Y_MSO'].max():.2f} km")
#     print(f"Z_MSO - 範囲: {df['Z_MSO'].min():.2f} から {df['Z_MSO'].max():.2f} km")

# def detect_and_clean_outliers(df, columns=['BX_MSO', 'BY_MSO', 'BZ_MSO'], method='iqr', threshold=3.0):
#     """
#     磁場データの異常値を検出してNaNに置き換える
    
#     Parameters:
#     df (pandas.DataFrame): データフレーム
#     columns (list): 異常値検出対象の列名
#     method (str): 異常値検出方法 ('iqr', 'zscore', 'mad')
#     threshold (float): 異常値判定の閾値
    
#     Returns:
#     pandas.DataFrame: 異常値をNaNに置き換えたデータフレーム
#     """
#     print("=== 異常値検出とクリーニング ===")
    
#     df_cleaned = df.copy()
#     total_outliers = 0
    
#     for col in columns:
#         if col not in df.columns:
#             print(f"警告: 列 '{col}' が見つかりません")
#             continue
            
#         original_count = len(df_cleaned)
        
#         if method == 'iqr':
#             # IQR法による異常値検出
#             Q1 = df_cleaned[col].quantile(0.25)
#             Q3 = df_cleaned[col].quantile(0.75)
#             IQR = Q3 - Q1
#             lower_bound = Q1 - threshold * IQR
#             upper_bound = Q3 + threshold * IQR
            
#             outliers = (df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)
            
#         elif method == 'zscore':
#             # Z-score法による異常値検出
#             z_scores = np.abs((df_cleaned[col] - df_cleaned[col].mean()) / df_cleaned[col].std())
#             outliers = z_scores > threshold
            
#         elif method == 'mad':
#             # Median Absolute Deviation法による異常値検出
#             median = df_cleaned[col].median()
#             mad = np.median(np.abs(df_cleaned[col] - median))
#             modified_z_scores = 0.6745 * (df_cleaned[col] - median) / mad
#             outliers = np.abs(modified_z_scores) > threshold
            
#         else:
#             print(f"警告: 未知の方法 '{method}' が指定されました。'iqr'を使用します。")
#             continue
        
#         outlier_count = outliers.sum()
#         total_outliers += outlier_count
        
#         if outlier_count > 0:
#             print(f"{col}: {outlier_count}個の異常値を検出 (全体の{outlier_count/len(df_cleaned)*100:.2f}%)")
#             print(f"  範囲: {df_cleaned[col].min():.2f} から {df_cleaned[col].max():.2f}")
            
#             # 異常値をNaNに置き換え
#             df_cleaned.loc[outliers, col] = np.nan
            
#             # 異常値の統計情報
#             outlier_values = df.loc[outliers, col]
#             print(f"  異常値の統計: 平均={outlier_values.mean():.2f}, 標準偏差={outlier_values.std():.2f}")
#         else:
#             print(f"{col}: 異常値なし")
    
#     print(f"\n総異常値数: {total_outliers}個 (全体の{total_outliers/len(df)*100:.2f}%)")
    
#     return df_cleaned

# def plot_magnetic_field_with_outliers(df, df_cleaned=None, save_plot=True):
#     """
#     異常値を含む磁場データをプロットする（異常値を強調表示）
    
#     Parameters:
#     df (pandas.DataFrame): 元のデータフレーム
#     df_cleaned (pandas.DataFrame): 異常値をNaNに置き換えたデータフレーム
#     save_plot (bool): プロットを保存するかどうか
#     """
#     if df_cleaned is None:
#         df_cleaned = df.copy()
    
#     plt.figure(figsize=(15, 12))
    
#     # 磁場の3成分をプロット
#     components = ['BX_MSO', 'BY_MSO', 'BZ_MSO']
#     colors = ['r', 'g', 'b']
    
#     for i, (comp, color) in enumerate(zip(components, colors)):
#         plt.subplot(3, 1, i+1)
        
#         # 正常なデータをプロット
#         normal_mask = ~df_cleaned[comp].isna()
#         if normal_mask.sum() > 0:
#             plt.plot(df_cleaned.loc[normal_mask, 'datetime'], 
#                     df_cleaned.loc[normal_mask, comp], 
#                     color=color, linewidth=0.5, alpha=0.7, label='Normal Data')
        
#         # 異常値を強調表示
#         outlier_mask = df[comp] != df_cleaned[comp]
#         if outlier_mask.sum() > 0:
#             plt.scatter(df.loc[outlier_mask, 'datetime'], 
#                        df.loc[outlier_mask, comp], 
#                        color='red', s=10, alpha=0.8, label='Outliers')
        
#         plt.ylabel(f'{comp} (nT)')
#         plt.title(f'MESSENGER Magnetometer Data - {comp}')
#         plt.grid(True, alpha=0.3)
#         plt.legend()
    
#     plt.xlabel('Time')
#     plt.tight_layout()
    
#     if save_plot:
#         plt.savefig('messenger_magnetic_field_with_outliers.png', dpi=300, bbox_inches='tight')
#         print("Plot saved as 'messenger_magnetic_field_with_outliers.png'")
    
#     # plt.show()

# def plot_magnetic_field_cleaned(df_cleaned, save_plot=True):
#     """
#     異常値を除去した磁場データをプロットする
    
#     Parameters:
#     df_cleaned (pandas.DataFrame): 異常値をNaNに置き換えたデータフレーム
#     save_plot (bool): プロットを保存するかどうか
#     """
#     plt.figure(figsize=(15, 10))
    
#     # 磁場の3成分をプロット
#     components = ['BX_MSO', 'BY_MSO', 'BZ_MSO']
#     colors = ['r', 'g', 'b']
    
#     for i, (comp, color) in enumerate(zip(components, colors)):
#         plt.subplot(3, 1, i+1)
        
#         # NaNを除外してプロット
#         valid_mask = ~df_cleaned[comp].isna()
#         if valid_mask.sum() > 0:
#             plt.plot(df_cleaned.loc[valid_mask, 'datetime'], 
#                     df_cleaned.loc[valid_mask, comp], 
#                     color=color, linewidth=0.5)
        
#         plt.ylabel(f'{comp} (nT)')
#         plt.title(f'MESSENGER Magnetometer Data (Cleaned) - {comp}')
#         plt.grid(True, alpha=0.3)
    
#     plt.xlabel('Time')
#     plt.tight_layout()
    
#     if save_plot:
#         plt.savefig('messenger_magnetic_field_cleaned.png', dpi=300, bbox_inches='tight')
#         print("Plot saved as 'messenger_magnetic_field_cleaned.png'")
    
#     # plt.show()

# def plot_magnetic_field(df, save_plot=True):
#     """
#     Plot magnetic field data
    
#     Parameters:
#     df (pandas.DataFrame): Data frame
#     save_plot (bool): Whether to save the plot
#     """
#     plt.figure(figsize=(15, 10))
    
#     # Generate title based on data period
#     start_date = df['datetime'].min().strftime('%Y-%m-%d')
#     end_date = df['datetime'].max().strftime('%Y-%m-%d')
#     if start_date == end_date:
#         title_date = start_date
#     else:
#         title_date = f"{start_date} to {end_date}"
    
#     # Plot magnetic field components
#     plt.subplot(3, 1, 1)
#     plt.plot(df['datetime'], df['BX_MSO'], 'r-', linewidth=0.5)
#     plt.ylabel('BX_MSO (nT)')
#     plt.title(f'MESSENGER Magnetometer Data - {title_date}')
#     plt.grid(True, alpha=0.3)
    
#     plt.subplot(3, 1, 2)
#     plt.plot(df['datetime'], df['BY_MSO'], 'g-', linewidth=0.5)
#     plt.ylabel('BY_MSO (nT)')
#     plt.grid(True, alpha=0.3)
    
#     plt.subplot(3, 1, 3)
#     plt.plot(df['datetime'], df['BZ_MSO'], 'b-', linewidth=0.5)
#     plt.ylabel('BZ_MSO (nT)')
#     plt.xlabel('Time')
#     plt.grid(True, alpha=0.3)
    
#     plt.tight_layout()
    
#     if save_plot:
#         plt.savefig('messenger_magnetic_field.png', dpi=300, bbox_inches='tight')
#         print("Plot saved as 'messenger_magnetic_field.png'")
    
#     # plt.show()

# def plot_position(df, save_plot=True):
#     """
#     Plot spacecraft position data
    
#     Parameters:
#     df (pandas.DataFrame): Data frame
#     save_plot (bool): Whether to save the plot
#     """
#     plt.figure(figsize=(15, 10))
    
#     # Generate title based on data period
#     start_date = df['datetime'].min().strftime('%Y-%m-%d')
#     end_date = df['datetime'].max().strftime('%Y-%m-%d')
#     if start_date == end_date:
#         title_date = start_date
#     else:
#         title_date = f"{start_date} to {end_date}"
    
#     # Plot position components
#     plt.subplot(3, 1, 1)
#     plt.plot(df['datetime'], df['X_MSO'], 'r-', linewidth=0.5)
#     plt.ylabel('X_MSO (km)')
#     plt.title(f'MESSENGER Spacecraft Position - {title_date}')
#     plt.grid(True, alpha=0.3)
    
#     plt.subplot(3, 1, 2)
#     plt.plot(df['datetime'], df['Y_MSO'], 'g-', linewidth=0.5)
#     plt.ylabel('Y_MSO (km)')
#     plt.grid(True, alpha=0.3)
    
#     plt.subplot(3, 1, 3)
#     plt.plot(df['datetime'], df['Z_MSO'], 'b-', linewidth=0.5)
#     plt.ylabel('Z_MSO (km)')
#     plt.xlabel('Time')
#     plt.grid(True, alpha=0.3)
    
#     plt.tight_layout()
    
#     if save_plot:
#         plt.savefig('messenger_position.png', dpi=300, bbox_inches='tight')
#         print("Plot saved as 'messenger_position.png'")
    
#     # plt.show()

# def debug_orbit_data(df):
#     """
#     軌道データの範囲をデバッグ表示する
    
#     Parameters:
#     df (pandas.DataFrame): データフレーム
#     """
#     print("=== 軌道データの範囲デバッグ ===")
#     print(f"X_MSO 範囲: {df['X_MSO'].min():.2f} から {df['X_MSO'].max():.2f} km")
#     print(f"Y_MSO 範囲: {df['Y_MSO'].min():.2f} から {df['Y_MSO'].max():.2f} km")
#     print(f"Z_MSO 範囲: {df['Z_MSO'].min():.2f} から {df['Z_MSO'].max():.2f} km")
    
#     # 水星の半径
#     mercury_radius = 2439.7
#     print(f"水星半径: {mercury_radius} km")
    
#     # 原点からの距離を計算
#     df['distance_from_origin'] = np.sqrt(df['X_MSO']**2 + df['Y_MSO']**2 + df['Z_MSO']**2)
#     print(f"原点からの最小距離: {df['distance_from_origin'].min():.2f} km")
#     print(f"原点からの最大距離: {df['distance_from_origin'].max():.2f} km")
    
#     # 水星表面に近いデータポイントを確認
#     close_to_mercury = df[df['distance_from_origin'] < mercury_radius * 1.5]
#     print(f"水星表面の1.5倍半径以内のデータポイント数: {len(close_to_mercury)}")
    
#     if len(close_to_mercury) > 0:
#         print(f"水星に最も近い距離: {close_to_mercury['distance_from_origin'].min():.2f} km")
    
#     return df

# def plot_orbit_xy(df, save_plot=True):
#     """
#     x-y平面での軌道プロット（水星中心）
    
#     Parameters:
#     df (pandas.DataFrame): データフレーム
#     save_plot (bool): プロットを保存するかどうか
#     """
#     plt.figure(figsize=(12, 10))
    
#     # 水星の半径（km）
#     mercury_radius = 2439.7
    
#     # データの範囲を取得して軸の範囲を設定
#     x_min, x_max = df['X_MSO'].min(), df['X_MSO'].max()
#     y_min, y_max = df['Y_MSO'].min(), df['Y_MSO'].max()
    
#     # 軸の範囲を少し拡張して水星が見えるようにする
#     margin = max(mercury_radius * 0.5, 1000)  # 少なくとも1000kmのマージン
#     x_min_plot = min(x_min - margin, -mercury_radius * 1.2)
#     x_max_plot = max(x_max + margin, mercury_radius * 1.2)
#     y_min_plot = min(y_min - margin, -mercury_radius * 1.2)
#     y_max_plot = max(y_max + margin, mercury_radius * 1.2)
    
#     # 水星を黒く塗りつぶされた円で表示（最初に描画）
#     theta = np.linspace(0, 2*np.pi, 100)
#     x_mercury = mercury_radius * np.cos(theta)
#     y_mercury = mercury_radius * np.sin(theta)
#     plt.fill(x_mercury, y_mercury, 'black', alpha=0.8, label='Mercury')
#     plt.plot(x_mercury, y_mercury, 'k-', linewidth=1)
    
#     # 軌道プロット（水星の上に描画）
#     plt.plot(df['X_MSO'], df['Y_MSO'], 'b-', linewidth=0.5, alpha=0.7, label='MESSENGER Orbit')
    
#     # 軌道の開始点と終了点をマーク
#     plt.plot(df['X_MSO'].iloc[0], df['Y_MSO'].iloc[0], 'go', markersize=6, label='Start Point')
#     plt.plot(df['X_MSO'].iloc[-1], df['Y_MSO'].iloc[-1], 'mo', markersize=6, label='End Point')
    
#     # 原点（水星中心）をマーク
#     plt.plot(0, 0, 'ko', markersize=3, alpha=0.5)
    
#     # Generate title based on data period
#     start_date = df['datetime'].min().strftime('%Y-%m-%d')
#     end_date = df['datetime'].max().strftime('%Y-%m-%d')
#     if start_date == end_date:
#         title_date = start_date
#     else:
#         title_date = f"{start_date} to {end_date}"
    
#     plt.xlabel('X_MSO (km)')
#     plt.ylabel('Y_MSO (km)')
#     plt.title(f'MESSENGER Orbit - X-Y Plane (Mercury Centered)\n{title_date}')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
    
#     # Set axis limits
#     plt.xlim(x_min_plot, x_max_plot)
#     plt.ylim(y_min_plot, y_max_plot)
#     plt.axis('equal')
    
#     if save_plot:
#         plt.savefig('messenger_orbit_xy.png', dpi=300, bbox_inches='tight')
#         print("Orbit plot (X-Y plane) saved as 'messenger_orbit_xy.png'")
    
#     # plt.show()

# def plot_orbit_xz(df, save_plot=True):
#     """
#     x-z平面での軌道プロット（水星中心）
    
#     Parameters:
#     df (pandas.DataFrame): データフレーム
#     save_plot (bool): プロットを保存するかどうか
#     """
#     plt.figure(figsize=(12, 10))
    
#     # 水星の半径（km）
#     mercury_radius = 2439.7
    
#     # データの範囲を取得して軸の範囲を設定
#     x_min, x_max = df['X_MSO'].min(), df['X_MSO'].max()
#     z_min, z_max = df['Z_MSO'].min(), df['Z_MSO'].max()
    
#     # 軸の範囲を少し拡張して水星が見えるようにする
#     margin = max(mercury_radius * 0.5, 1000)  # 少なくとも1000kmのマージン
#     x_min_plot = min(x_min - margin, -mercury_radius * 1.2)
#     x_max_plot = max(x_max + margin, mercury_radius * 1.2)
#     z_min_plot = min(z_min - margin, -mercury_radius * 1.2)
#     z_max_plot = max(z_max + margin, mercury_radius * 1.2)
    
#     # 水星を黒く塗りつぶされた円で表示（最初に描画）
#     theta = np.linspace(0, 2*np.pi, 100)
#     x_mercury = mercury_radius * np.cos(theta)
#     z_mercury = mercury_radius * np.sin(theta)
#     plt.fill(x_mercury, z_mercury, 'black', alpha=0.8, label='Mercury')
#     plt.plot(x_mercury, z_mercury, 'k-', linewidth=1)
    
#     # 軌道プロット（水星の上に描画）
#     plt.plot(df['X_MSO'], df['Z_MSO'], 'g-', linewidth=0.5, alpha=0.7, label='MESSENGER Orbit')
    
#     # 軌道の開始点と終了点をマーク
#     plt.plot(df['X_MSO'].iloc[0], df['Z_MSO'].iloc[0], 'go', markersize=6, label='Start Point')
#     plt.plot(df['X_MSO'].iloc[-1], df['Z_MSO'].iloc[-1], 'mo', markersize=6, label='End Point')
    
#     # 原点（水星中心）をマーク
#     plt.plot(0, 0, 'ko', markersize=3, alpha=0.5)
    
#     # Generate title based on data period
#     start_date = df['datetime'].min().strftime('%Y-%m-%d')
#     end_date = df['datetime'].max().strftime('%Y-%m-%d')
#     if start_date == end_date:
#         title_date = start_date
#     else:
#         title_date = f"{start_date} to {end_date}"
    
#     plt.xlabel('X_MSO (km)')
#     plt.ylabel('Z_MSO (km)')
#     plt.title(f'MESSENGER Orbit - X-Z Plane (Mercury Centered)\n{title_date}')
#     plt.legend()
#     plt.grid(True, alpha=0.3)
    
#     # Set axis limits
#     plt.xlim(x_min_plot, x_max_plot)
#     plt.ylim(z_min_plot, z_max_plot)
#     plt.axis('equal')
    
#     if save_plot:
#         plt.savefig('messenger_orbit_xz.png', dpi=300, bbox_inches='tight')
#         print("Orbit plot (X-Z plane) saved as 'messenger_orbit_xz.png'")
    
#     # plt.show()

# def plot_3d_orbit(df, save_plot=True):
#     """
#     3D orbit plot (Mercury centered)
    
#     Parameters:
#     df (pandas.DataFrame): Data frame
#     save_plot (bool): Whether to save the plot
#     """
#     print("3D plots are not currently supported. Please use 2D plots.")

# def plot_orbit_with_time_color(df, save_plot=True):
#     """
#     Time color-coded orbit plot
    
#     Parameters:
#     df (pandas.DataFrame): Data frame
#     save_plot (bool): Whether to save the plot
#     """
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
#     # Mercury radius (km)
#     mercury_radius = 2439.7
    
#     # Get data ranges
#     x_min, x_max = df['X_MSO'].min(), df['X_MSO'].max()
#     y_min, y_max = df['Y_MSO'].min(), df['Y_MSO'].max()
#     z_min, z_max = df['Z_MSO'].min(), df['Z_MSO'].max()
    
#     # Extend axis ranges to show Mercury
#     margin = max(mercury_radius * 0.5, 1000)
#     x_min_plot = min(x_min - margin, -mercury_radius * 1.2)
#     x_max_plot = max(x_max + margin, mercury_radius * 1.2)
#     y_min_plot = min(y_min - margin, -mercury_radius * 1.2)
#     y_max_plot = max(y_max + margin, mercury_radius * 1.2)
#     z_min_plot = min(z_min - margin, -mercury_radius * 1.2)
#     z_max_plot = max(z_max + margin, mercury_radius * 1.2)
    
#     # Normalize time for color mapping
#     time_normalized = (df['datetime'] - df['datetime'].min()).dt.total_seconds()
#     time_normalized = time_normalized / time_normalized.max()
    
#     # X-Y plane
#     # Draw Mercury as filled black circle (draw first)
#     theta = np.linspace(0, 2*np.pi, 100)
#     x_mercury = mercury_radius * np.cos(theta)
#     y_mercury = mercury_radius * np.sin(theta)
#     ax1.fill(x_mercury, y_mercury, 'black', alpha=0.8, label='Mercury')
#     ax1.plot(x_mercury, y_mercury, 'k-', linewidth=1)
    
#     # X-Y plane orbit (draw on top of Mercury)
#     scatter1 = ax1.scatter(df['X_MSO'], df['Y_MSO'], c=time_normalized, 
#                            cmap='viridis', s=1, alpha=0.7)
    
#     ax1.set_xlabel('X_MSO (km)')
#     ax1.set_ylabel('Y_MSO (km)')
#     ax1.set_title('MESSENGER Orbit - X-Y Plane (Time Color-coded)')
#     ax1.grid(True, alpha=0.3)
#     ax1.set_xlim(x_min_plot, x_max_plot)
#     ax1.set_ylim(y_min_plot, y_max_plot)
#     ax1.axis('equal')
    
#     # Add colorbar
#     cbar1 = plt.colorbar(scatter1, ax=ax1)
#     cbar1.set_label('Time (Normalized)')
    
#     # X-Z plane
#     # Draw Mercury as filled black circle (draw first)
#     z_mercury = mercury_radius * np.sin(theta)
#     ax2.fill(x_mercury, z_mercury, 'black', alpha=0.8, label='Mercury')
#     ax2.plot(x_mercury, z_mercury, 'k-', linewidth=1)
    
#     # X-Z plane orbit (draw on top of Mercury)
#     scatter2 = ax2.scatter(df['X_MSO'], df['Z_MSO'], c=time_normalized, 
#                            cmap='viridis', s=1, alpha=0.7)
    
#     ax2.set_xlabel('X_MSO (km)')
#     ax2.set_ylabel('Z_MSO (km)')
#     ax2.set_title('MESSENGER Orbit - X-Z Plane (Time Color-coded)')
#     ax2.grid(True, alpha=0.3)
#     ax2.set_xlim(x_min_plot, x_max_plot)
#     ax2.set_ylim(z_min_plot, z_max_plot)
#     ax2.axis('equal')
    
#     # Add colorbar
#     cbar2 = plt.colorbar(scatter2, ax=ax2)
#     cbar2.set_label('Time (Normalized)')
    
#     plt.tight_layout()
    
#     if save_plot:
#         plt.savefig('messenger_orbit_time_color.png', dpi=300, bbox_inches='tight')
#         print("Time color-coded orbit plot saved as 'messenger_orbit_time_color.png'")
    
#     # plt.show()

# def get_magnetic_field_numpy_array(df):
#     """
#     指定されたDataFrameから磁場データ（BX_MSO, BY_MSO, BZ_MSO）をnumpy配列(n_times, 3)で返す
    
#     Parameters:
#     df (pandas.DataFrame): データフレーム
    
#     Returns:
#     numpy.ndarray: 磁場データ配列 (n_times, 3)
#     """
#     return df[["BX_MSO", "BY_MSO", "BZ_MSO"]].to_numpy()

# def create_pytplot_vars_from_df(df):
#     """
#     DataFrameから磁場データ、位置データ、unix時間をnumpy配列で抽出し、pytplot変数として登録する
#     - 'mag': (n_times, 3) 磁場 [BX_MSO, BY_MSO, BZ_MSO]
#     - 'pos': (n_times, 3) 位置 [X_MSO, Y_MSO, Z_MSO]
#     - 'time': (n_times,) unix秒
#     """
#     import numpy as np
#     # unix time (float64)
#     if 'datetime' in df.columns:
#         time_unix = df['datetime'].astype('int64') // 10**9
#         time_unix = time_unix.to_numpy(dtype=np.float64)
#     else:
#         raise ValueError('datetime列が必要です')
#     # magnetic field
#     mag = df[["BX_MSO", "BY_MSO", "BZ_MSO"]].to_numpy(dtype=np.float64)
#     # position
#     pos = df[["X_MSO", "Y_MSO", "Z_MSO"]].to_numpy(dtype=np.float64)
#     # pytplot変数登録
#     pytplot.store_data('mag', data={'x': time_unix, 'y': mag})
#     pytplot.store_data('pos', data={'x': time_unix, 'y': pos})
#     pytplot.store_data('time', data={'x': time_unix, 'y': time_unix})
#     print("pytplot変数 'mag', 'pos', 'time' を登録しました")
#     return {'mag': mag, 'pos': pos, 'time': time_unix}

# class MessengerDataDownloader:
#     """
#     MESSENGER磁場データを期間指定でダウンロードするクラス
#     """
    
#     def __init__(self, base_url="https://pds-ppi.igpp.ucla.edu"):
#         self.base_url = base_url
#         self.session = requests.Session()
#         self.session.headers.update({
#             'User-Agent': 'MESSENGER-Data-Downloader/1.0'
#         })
    
#     def get_available_dates(self):
#         """
#         利用可能なデータの日付範囲を取得
#         """
#         # MESSENGERの運用期間（概算）
#         messenger_start = datetime(2004, 8, 3)  # 打ち上げ
#         messenger_end = datetime(2015, 4, 30)   # 水星表面への衝突
        
#         print(f"MESSENGER mission period: {messenger_start.strftime('%Y-%m-%d')} to {messenger_end.strftime('%Y-%m-%d')}")
#         return messenger_start, messenger_end
    
#     def date_to_product_id(self, date):
#         """
#         日付からプロダクトIDを生成（8桁形式）
#         """
#         year = date.year
#         day_of_year = date.timetuple().tm_yday
#         # 8桁形式: magmsosci08012
#         return f"magmsosci{year % 100:02d}{day_of_year:03d}"

#     def construct_download_url_from_date(self, date):
#         """
#         日付から直接ダウンロードURLを構築（APIを使わない方法）
#         """
#         product_id = self.date_to_product_id(date)
#         urn_id = f"urn:nasa:pds:mess-mag-calibrated:data-mso:{product_id}::1.0"
        
#         # 日付からslotパスを構築
#         year = date.year
#         day_of_year = date.timetuple().tm_yday
        
#         # slotパス: /data/mess-mag-calibrated/data/mso/2008/001_031_JAN
#         # 月の範囲を計算（例：001_031_JAN）
#         month = date.month
#         if month == 1:
#             month_range = "001_031_JAN"
#         elif month == 2:
#             month_range = "032_060_FEB"
#         elif month == 3:
#             month_range = "061_090_MAR"
#         elif month == 4:
#             month_range = "091_120_APR"
#         elif month == 5:
#             month_range = "121_151_MAY"
#         elif month == 6:
#             month_range = "152_181_JUN"
#         elif month == 7:
#             month_range = "182_212_JUL"
#         elif month == 8:
#             month_range = "213_243_AUG"
#         elif month == 9:
#             month_range = "244_273_SEP"
#         elif month == 10:
#             month_range = "274_304_OCT"
#         elif month == 11:
#             month_range = "305_334_NOV"
#         elif month == 12:
#             month_range = "335_365_DEC"
        
#         slot = f"/data/mess-mag-calibrated/data/mso/{year}/{month_range}"
#         file_name = f"MAGMSOSCI{product_id}_V08.xml"
#         data_file = f"MAGMSOSCI{product_id}_V08.TAB"
        
#         download_url = f"{self.base_url}/ditdos/download?id={urn_id}&slot={slot}&file_name={file_name}&data_file={data_file}"
#         print(f"  Constructed download URL from date: {download_url}")
#         return download_url
    
#     def download_zip_file(self, url, output_path, show_progress=True):
#         """
#         ZIPファイルをダウンロードして展開（高速化版）
#         """
#         try:
#             if show_progress:
#                 print(f"  Downloading ZIP file from: {url}")
            
#             response = self.session.get(url, stream=True, timeout=60)
#             response.raise_for_status()
            
#             # ファイルサイズを取得（プログレスバー用）
#             total_size = int(response.headers.get('content-length', 0))
            
#             # 一時ファイルに保存
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
#                 if show_progress and total_size > 0:
#                     with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
#                         for chunk in response.iter_content(chunk_size=32768):  # チャンクサイズを増加
#                             if chunk:
#                                 temp_file.write(chunk)
#                                 pbar.update(len(chunk))
#                 else:
#                     for chunk in response.iter_content(chunk_size=32768):
#                         if chunk:
#                             temp_file.write(chunk)
                
#                 temp_file_path = temp_file.name
            
#             # ZIPファイルを展開
#             if show_progress:
#                 print(f"  Extracting ZIP file to: {output_path}")
#             with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
#                 zip_ref.extractall(output_path)
            
#             # 一時ファイルを削除
#             os.unlink(temp_file_path)
            
#             if show_progress:
#                 print(f"  ✓ Successfully downloaded and extracted to: {output_path}")
#             return True
            
#         except Exception as e:
#             if show_progress:
#                 print(f"  ✗ Error downloading/extracting ZIP file: {e}")
#             return False
    
#     def download_data_for_period(self, start_date, end_date, output_dir="messenger_data", skip_availability_check=False, max_workers=4):
#         """
#         Download data for the specified period (with parallel download support)
#         """
#         print(f"=== MESSENGER Data Download ===")
#         print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
#         print(f"Output directory: {output_dir}")
#         print(f"Max parallel downloads: {max_workers}")
#         print("=" * 50)
        
#         # Create output directory
#         Path(output_dir).mkdir(parents=True, exist_ok=True)
        
#         # ダウンロードタスクを準備
#         download_tasks = []
#         current_date = start_date
        
#         while current_date <= end_date:
#             date_str = current_date.strftime('%Y%m%d')
#             date_dir = Path(output_dir) / date_str
            
#             # Check if already downloaded
#             tab_files = list(date_dir.glob("*.TAB")) if date_dir.exists() else []
#             if tab_files:
#                 print(f"{current_date.strftime('%Y-%m-%d')}: Already downloaded, skipping...")
#                 current_date += timedelta(days=1)
#                 continue
            
#             # ダウンロードURLを構築
#             download_url = self.construct_download_url_from_date(current_date)
            
#             if download_url:
#                 download_tasks.append({
#                     'date': current_date,
#                     'url': download_url,
#                     'output_dir': str(date_dir)
#                 })
#             else:
#                 print(f"Could not construct download URL for {current_date.strftime('%Y-%m-%d')}")
            
#             current_date += timedelta(days=1)
        
#         if not download_tasks:
#             print("No files to download (all files already exist or no valid URLs found)")
#             return True
        
#         print(f"Found {len(download_tasks)} files to download")
        
#         # 並列ダウンロード実行
#         downloaded_count = 0
#         failed_count = 0
        
#         def download_single_file(task):
#             """単一ファイルのダウンロード（並列実行用）"""
#             date = task['date']
#             url = task['url']
#             output_dir = task['output_dir']
            
#             # 日付ディレクトリを作成
#             Path(output_dir).mkdir(parents=True, exist_ok=True)
            
#             # ダウンロード実行（プログレスバーは並列実行時は無効）
#             success = self.download_zip_file(url, output_dir, show_progress=False)
            
#             if success:
#                 print(f"✓ Downloaded: {date.strftime('%Y-%m-%d')}")
#                 return True
#             else:
#                 print(f"✗ Failed: {date.strftime('%Y-%m-%d')}")
#                 return False
        
#         # ThreadPoolExecutorを使用して並列ダウンロード
#         with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
#             # タスクを送信
#             future_to_task = {executor.submit(download_single_file, task): task for task in download_tasks}
            
#             # 結果を収集
#             for future in concurrent.futures.as_completed(future_to_task):
#                 if future.result():
#                     downloaded_count += 1
#                 else:
#                     failed_count += 1
        
#         print(f"\n=== Download Summary ===")
#         print(f"Total files downloaded: {downloaded_count}")
#         print(f"Total files failed: {failed_count}")
#         print(f"Output directory: {output_dir}")
        
#         return downloaded_count > 0

# def download_messenger_data(start_date, end_date, output_dir="messenger_data", max_workers=4):
#     """
#     Download MESSENGER data for the specified period with parallel download support
    
#     Parameters:
#     start_date (datetime): Start date
#     end_date (datetime): End date
#     output_dir (str): Output directory
#     max_workers (int): Maximum number of parallel downloads
    
#     Returns:
#     bool: True if download successful
#     """
#     downloader = MessengerDataDownloader()
#     return downloader.download_data_for_period(start_date, end_date, output_dir, max_workers=max_workers)

# def analyze_period_data(start_date, end_date, data_dir="messenger_data", plot=True):
#     """
#     指定された期間のデータを解析する
    
#     Parameters:
#     start_date (datetime): 開始日
#     end_date (datetime): 終了日
#     data_dir (str): データディレクトリ
#     plot (bool): プロットを作成するかどうか
#     """
#     from datetime import datetime, timedelta
#     from pathlib import Path
#     import os
    
#     print(f"=== MESSENGER Data Analysis for Period ===")
#     print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
#     print(f"Data directory: {data_dir}")
#     print("=" * 50)
    
#     all_data = []
#     current_date = start_date
    
#     while current_date <= end_date:
#         # 日付からディレクトリ名を生成
#         date_str = current_date.strftime('%Y%m%d')
#         dir_path = Path(data_dir) / date_str
        
#         # TABファイルを探す
#         tab_files = list(dir_path.glob("*.TAB"))
        
#         if tab_files:
#             tab_file_path = str(tab_files[0])
#             print(f"\nAnalyzing data for {current_date.strftime('%Y-%m-%d')}...")
#             print(f"File: {tab_file_path}")
            
#             try:
#                 # データ読み込み
#                 df = read_tab_file_pandas(tab_file_path)
#                 if df is None:
#                     df = read_tab_file_fixed_width(tab_file_path)
                
#                 if df is not None and len(df) > 0:
#                     # datetime列を追加
#                     df = create_datetime_column(df)
                    
#                     # データをリストに追加
#                     all_data.append({
#                         'date': current_date,
#                         'data': df,
#                         'file_path': tab_file_path
#                     })
                    
#                     print(f"  ✓ Loaded {len(df)} records")
#                 else:
#                     print(f"  ✗ Failed to load data")
                    
#             except Exception as e:
#                 print(f"  ✗ Error loading data: {e}")
#         else:
#             print(f"\nNo data found for {current_date.strftime('%Y-%m-%d')}")
        
#         current_date += timedelta(days=1)
    
#     if not all_data:
#         print("\nNo data found for the specified period.")
#         return
    
#     # 全データを結合
#     print(f"\n=== Combined Analysis ===")
#     print(f"Total files: {len(all_data)}")
    
#     combined_df = pd.concat([item['data'] for item in all_data], ignore_index=True)
#     print(f"Total records: {len(combined_df)}")
    
#     # データ分析
#     analyze_messenger_data(combined_df)
    
#     # 異常値検出とクリーニング
#     print("\n=== 異常値検出とクリーニング ===")
#     df_cleaned = detect_and_clean_outliers(combined_df, method='iqr', threshold=3.0)
    
#     # デバッグ情報を表示
#     combined_df = debug_orbit_data(combined_df)
    
#     # プロット作成
#     if plot:
#         print("\nプロットを作成しています...")
#         plot_magnetic_field(combined_df)
#         plot_magnetic_field_with_outliers(combined_df, df_cleaned)
#         plot_magnetic_field_cleaned(df_cleaned)
#         plot_position(combined_df)
    
#     # 軌道プロットを追加
#     if plot:
#         print("\n軌道プロットを作成しています...")
#         plot_orbit_xy(combined_df)
#         plot_orbit_xz(combined_df)
#         plot_orbit_with_time_color(combined_df)
    
#     # データの最初の数行を表示
#     print("\n=== データの最初の5行 ===")
#     print(combined_df.head())
    
#     return combined_df

# def analyze_single_date(date, data_dir="messenger_data", plot=True):
#     """
#     指定された日付のデータを解析する
    
#     Parameters:
#     date (datetime): 解析する日付
#     data_dir (str): データディレクトリ
#     plot (bool): プロットを作成するかどうか
#     """
#     from pathlib import Path
    
#     print(f"=== MESSENGER Data Analysis for {date.strftime('%Y-%m-%d')} ===")
#     print(f"Data directory: {data_dir}")
#     print("=" * 50)
    
#     # 日付からディレクトリ名を生成
#     date_str = date.strftime('%Y%m%d')
#     dir_path = Path(data_dir) / date_str
    
#     # TABファイルを探す
#     tab_files = list(dir_path.glob("*.TAB"))
    
#     if not tab_files:
#         print(f"No data found for {date.strftime('%Y-%m-%d')}")
#         print(f"Expected directory: {dir_path}")
#         return None
    
#     tab_file_path = str(tab_files[0])
#     print(f"File: {tab_file_path}")
    
#     try:
#         # データ読み込み
#         df = read_tab_file_pandas(tab_file_path)
#         if df is None:
#             df = read_tab_file_fixed_width(tab_file_path)
        
#         if df is not None and len(df) > 0:
#             print(f"✓ Loaded {len(df)} records")
            
#             # datetime列を追加
#             df = create_datetime_column(df)
            
#             # データ分析
#             analyze_messenger_data(df)
            
#             # 異常値検出とクリーニング
#             print("\n=== 異常値検出とクリーニング ===")
#             df_cleaned = detect_and_clean_outliers(df, method='iqr', threshold=3.0)
            
#             # デバッグ情報を表示
#             df = debug_orbit_data(df)
            
#             # プロット作成
#             if plot:
#                 print("\nプロットを作成しています...")
#                 plot_magnetic_field(df)
#                 plot_magnetic_field_with_outliers(df, df_cleaned)
#                 plot_magnetic_field_cleaned(df_cleaned)
#                 plot_position(df)
            
#             # 軌道プロットを追加
#             if plot:
#                 print("\n軌道プロットを作成しています...")
#                 plot_orbit_xy(df)
#                 plot_orbit_xz(df)
#                 plot_orbit_with_time_color(df)
            
#             # データの最初の数行を表示
#             print("\n=== データの最初の5行 ===")
#             print(df.head())
            
#             return df
#         else:
#             print("Failed to load data")
#             return None
            
#     except Exception as e:
#         print(f"Error loading data: {e}")
#         return None

# # メイン実行部分
# def old_main():
#     print("=== MESSENGER Data Analysis and Download ===")
#     print()
    
#     # ========================================
#     # ここで設定を変更してください
#     # ========================================
    
#     # データダウンロード設定
#     download_data = False  # True: データをダウンロード, False: 既存データを使用
#     # Note: 既存のTABファイルがある場合は自動的にスキップされます
#     start_period = '2011-08-01 09:00:00'
#     end_period = '2011-08-01 10:00:00'
#     start_date = datetime.strptime(start_period, '%Y-%m-%d %H:%M:%S')
#     end_date = datetime.strptime(end_period, '%Y-%m-%d %H:%M:%S')
#     # start_date = datetime(2008, 1, 12)  # 開始日
#     # end_date = datetime(2008, 1, 15)    # 終了日
#     data_dir = "messenger_data"          # データディレクトリ
#     max_workers = 4  # 並列ダウンロード数（高速化のため）
    
#     # 解析設定
#     analysis_type = "period"  # "period": 期間解析, "single": 単一日解析
#     single_date = datetime(2008, 1, 12)  # 単一日解析の場合の日付
    
#     # 異常値検出設定
#     outlier_detection = True  # True: 異常値検出を実行, False: スキップ
#     outlier_method = "iqr"    # "iqr", "zscore", "mad"
#     outlier_threshold = 3.0   # 異常値判定の閾値
    
#     # プロット設定
#     plot = False  # True: プロットを作成, False: プロットをスキップ
#     # ========================================
#     # 設定はここまで
#     # ========================================
    
#     print("=== Settings ===")
#     print(f"Download Data: {download_data}")
#     if download_data:
#         print(f"Download Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
#         print("Note: Existing TAB files will be automatically skipped")
#         print(f"Parallel Downloads: {max_workers} workers")
    
#     print(f"Analysis Type: {analysis_type}")
#     if analysis_type == "period":
#         print(f"Analysis Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
#     else:
#         print(f"Analysis Date: {single_date.strftime('%Y-%m-%d')}")
    
#     print(f"Data Directory: {data_dir}")
#     print(f"Outlier Detection: {outlier_detection}")
#     if outlier_detection:
#         print(f"Outlier Method: {outlier_method}, Threshold: {outlier_threshold}")
#     print(f"Plot: {plot}")
#     print("=" * 50)
#     print()
    
#     # データダウンロード（必要な場合）
#     if download_data:
#         print("Downloading data...")
#         success = download_messenger_data(start_date, end_date, data_dir, max_workers=max_workers)
#         if not success:
#             print("Data download failed or no data available for the specified period. Exiting.")
#             exit(1)
#         print("Data download/skip completed.")
#         print()
    
#     # データ解析
#     if analysis_type == "period":
#         print("Running period analysis...")
#         df = analyze_period_data(start_date, end_date, data_dir, plot=plot)
        
#         if df is not None:
#             print(f"\n=== Analysis Complete ===")
#             print(f"Total records analyzed: {len(df)}")
#             print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
#         else:
#             print("\nAnalysis failed or no data found.")
    
#     else:  # single
#         print("Running single date analysis...")
#         df = analyze_single_date(single_date, data_dir, plot=plot)
        
#         if df is not None:
#             print(f"\n=== Analysis Complete ===")
#             print(f"Total records analyzed: {len(df)}")
#             print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
#         else:
#             print("\nAnalysis failed or no data found.")
    

#     # spectrogram
#     vars = create_pytplot_vars_from_df(df)
#     pytplot.tplot_names()


    
#     print("\n=== Program Complete ===")
#     if plot:
#         print("Generated files:")
#         print("- messenger_magnetic_field.png")
#         print("- messenger_position.png")
#         print("- messenger_orbit_xy.png")
#         print("- messenger_orbit_xz.png")
#         print("- messenger_orbit_time_color.png")
