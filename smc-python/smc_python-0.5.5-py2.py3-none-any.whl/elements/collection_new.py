
def describe_task_progress(name=None, exact_match=True):
    """ 
    Describe task_progress entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('task_progress', name, exact_match)
    else:
        return []

def describe_logout(name=None, exact_match=True):
    """ 
    Describe logout entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('logout', name, exact_match)
    else:
        return []

def describe_elements(name=None, exact_match=True):
    """ 
    Describe elements entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('elements', name, exact_match)
    else:
        return []

def describe_vulnerability_type(name=None, exact_match=True):
    """ 
    Describe vulnerability_type entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('vulnerability_type', name, exact_match)
    else:
        return []

def describe_system(name=None, exact_match=True):
    """ 
    Describe system entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('system', name, exact_match)
    else:
        return []

def describe_snapshot(name=None, exact_match=True):
    """ 
    Describe snapshot entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('snapshot', name, exact_match)
    else:
        return []

def describe_certificate_authority(name=None, exact_match=True):
    """ 
    Describe certificate_authority entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('certificate_authority', name, exact_match)
    else:
        return []

def describe_smc_version(name=None, exact_match=True):
    """ 
    Describe smc_version entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('smc_version', name, exact_match)
    else:
        return []

def describe_smc_time(name=None, exact_match=True):
    """ 
    Describe smc_time entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('smc_time', name, exact_match)
    else:
        return []

def describe_last_activated_package(name=None, exact_match=True):
    """ 
    Describe last_activated_package entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('last_activated_package', name, exact_match)
    else:
        return []

def describe_update_package(name=None, exact_match=True):
    """ 
    Describe update_package entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('update_package', name, exact_match)
    else:
        return []

def describe_import_package(name=None, exact_match=True):
    """ 
    Describe import_package entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('import_package', name, exact_match)
    else:
        return []

def describe_engine_upgrade(name=None, exact_match=True):
    """ 
    Describe engine_upgrade entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('engine_upgrade', name, exact_match)
    else:
        return []

def describe_uncommitted(name=None, exact_match=True):
    """ 
    Describe uncommitted entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('uncommitted', name, exact_match)
    else:
        return []

def describe_system_properties(name=None, exact_match=True):
    """ 
    Describe system_properties entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('system_properties', name, exact_match)
    else:
        return []

def describe_empty_trash_bin(name=None, exact_match=True):
    """ 
    Describe empty_trash_bin entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('empty_trash_bin', name, exact_match)
    else:
        return []

def describe_clean_invalid_filters(name=None, exact_match=True):
    """ 
    Describe clean_invalid_filters entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('clean_invalid_filters', name, exact_match)
    else:
        return []

def describe_blacklist(name=None, exact_match=True):
    """ 
    Describe blacklist entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('blacklist', name, exact_match)
    else:
        return []

def describe_licenses(name=None, exact_match=True):
    """ 
    Describe licenses entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('licenses', name, exact_match)
    else:
        return []

def describe_license_fetch(name=None, exact_match=True):
    """ 
    Describe license_fetch entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('license_fetch', name, exact_match)
    else:
        return []

def describe_license_install(name=None, exact_match=True):
    """ 
    Describe license_install entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('license_install', name, exact_match)
    else:
        return []

def describe_license_details(name=None, exact_match=True):
    """ 
    Describe license_details entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('license_details', name, exact_match)
    else:
        return []

def describe_license_check_for_new(name=None, exact_match=True):
    """ 
    Describe license_check_for_new entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('license_check_for_new', name, exact_match)
    else:
        return []

def describe_unlicensed_components(name=None, exact_match=True):
    """ 
    Describe unlicensed_components entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('unlicensed_components', name, exact_match)
    else:
        return []

def describe_license_bind(name=None, exact_match=True):
    """ 
    Describe license_bind entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('license_bind', name, exact_match)
    else:
        return []

def describe_delete_license(name=None, exact_match=True):
    """ 
    Describe delete_license entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('delete_license', name, exact_match)
    else:
        return []

def describe_visible_virtual_engine_mapping(name=None, exact_match=True):
    """ 
    Describe visible_virtual_engine_mapping entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('visible_virtual_engine_mapping', name, exact_match)
    else:
        return []

def describe_references_by_element(name=None, exact_match=True):
    """ 
    Describe references_by_element entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('references_by_element', name, exact_match)
    else:
        return []

def describe_export_elements(name=None, exact_match=True):
    """ 
    Describe export_elements entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('export_elements', name, exact_match)
    else:
        return []

def describe_import_elements(name=None, exact_match=True):
    """ 
    Describe import_elements entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('import_elements', name, exact_match)
    else:
        return []

def describe_api(name=None, exact_match=True):
    """ 
    Describe api entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('api', name, exact_match)
    else:
        return []

def describe_login(name=None, exact_match=True):
    """ 
    Describe login entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('login', name, exact_match)
    else:
        return []

def describe_eia(name=None, exact_match=True):
    """ 
    Describe eia entries on the SMC
    
    ..note :: Requires SMC API version 6.1
    
    :return: :py:class:`smc.base.model.Element`
    """
    if session.api_version >= 6.1:
        return generic_list_builder('eia', name, exact_match)
    else:
        return []
