from common import display
from messenger_analysis.messenger_analysis import (
    git_download,
    git_upload,
    git_upload_public,
    # download data
    main_download,
    # create data
    create_taa_data,
    # ql
    ql_specpolari,
    ql_polarization,
    collect_event_ql,
    main_analysis,
    emic_event_search,
    create_band_flag_data_in_event,
    plot_distribution_freq_over_fcp,
    event_distribution_band_flag,
    dwell_time,
    create_event_flag_emic,
    create_reference_dwell_time,
    main_orbit,
    create_orb,
    # event
    create_band_flag_from_event_flag_emic,
    create_distribution_band_flag_from_event_flag_emic,
    distribution_band_flag_from_event_flag_emic,
    testrun_flag_emic,
    create_distribution_band_flag_by_taa,
    distribution_band_flag_by_taa,
    # --- test ---
    test_read_cdf,
    test_mso2mse,
    test_download_horizons_data,
)


display.set_log_level('DEBUG')
# display.set_log_level('WARNING')

# ----------------------------------------------------
# download/update module
# ----------------------------------------------------
# git_download()
# git_upload()
git_upload_public()

# ----------------------------------------------------
# download data
# ----------------------------------------------------
# main_download() # messenger mag mso

# ----------------------------------------------------
# create data
# ----------------------------------------------------
# create_taa_data()


# ----------------------------------------------------
# ql
# ----------------------------------------------------
# ql_polarization()

# ql_spectrogram()
# ql_specpolari()


# ----------------------------------------------------
# Orbit
# ----------------------------------------------------
# create_orb()
# create_reference_dwell_time()
# dwell_time()

# ----------------------------------------------------
# Intensity
# ----------------------------------------------------
# create_reference_intensity_dist()
# distribution_intensity()
# distribution_freq_over_fcp()
# plot_distribution_freq_over_fcp()

# ----------------------------------------------------
# Event
# ----------------------------------------------------
# create_event_flag_emic()
# create_band_flag_from_event_flag_emic()
# create_distribution_band_flag_from_event_flag_emic() # log_level -> 'WARNING'; The program could be interrupted with too much logs
# distribution_band_flag_from_event_flag_emic()

## classification by TAA
# create_distribution_band_flag_by_taa()
# distribution_band_flag_by_taa()

# testrun_flag_emic()
# emic_event_search()
# create_band_flag_data_in_event()
# collect_event_ql()
# event_distribution_band_flag()




# ----------------------------------------------------
# analysis
# ----------------------------------------------------
# main_analysis()
# main_orbit()


########################################################
# test
# test_read_cdf()
# test_mso2mse()
# test_download_horizons_data()
