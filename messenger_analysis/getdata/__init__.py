"""
MESSENGERデータ取得パッケージ

このパッケージはMESSENGER探査機のデータを取得・ダウンロードする機能を提供します。
"""

# from .download import ( # not used
#     download_mag_mso
# )

# from .download_0 import ( # to be deleted
#     MessengerDataDownloader,
#     download_messenger_data,
#     # download_single_date,
#     get_messenger_mission_period,
#     check_data_availability,
#     # download_messenger_data_trange,
#     convert_tab_to_cdf,
#     cleanup_downloaded_files,
# )


from .getdata import (
    load_messenger_to_tplot_by_trange,
    messenger_mag,
    messenger_orb
)


from .donwload_mag_mso import (
    download_mag_mso,
    convert_tab_to_cdf_mag_mso
)

__all__ = [
    'MessengerDataDownloader',
    'download_messenger_data',
    'download_single_date',
    'get_messenger_mission_period',
    'check_data_availability',
    'download_messenger_data_trange',
    'convert_tab_to_cdf',
    'cleanup_downloaded_files',
    'load_messenger_to_tplot_by_trange'
]
