from commonconf import override_settings


fdao_mylib_override = override_settings(
    RESTCLIENTS_LIBRARIES_DAO_CLASS='Mock')

fdao_subject_guide_override = override_settings(
    RESTCLIENTS_LIBCURRICS_DAO_CLASS='Mock')
