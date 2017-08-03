# -*- coding: UTF-8 -*-
from . import api_base
try:
    from StringIO import StringIO
except:
    from io import StringIO
import pandas as pd
import sys
from datetime import datetime
from .api_base import get_cache_key, get_data_from_cache, put_data_in_cache, pretty_traceback
import inspect
try:
    unicode
except:
    unicode = str

__doc__="家电网"
def HomeAppDistrictCategoryExptJDWGet(beginDate = "", endDate = "", categoryExport = "", area = "", district = "", field = "", pandas = "1"):
    """
    包含家用电器行业分出口地区、分品类的出口数据，如当期出口、累计出口、去年同期出口、去年同期累计出口等数据，具体内容可参见数据样例；历史数据从2011年1月开始，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categoryExport: 家电品类名称，可模糊查询,可空
    :param area: 省市,可空
    :param district: 地区,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppDistrictCategoryExptJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categoryExport, str) and not isinstance(categoryExport, unicode):
        categoryExport = str(categoryExport)

    requestString.append("&categoryExport=%s"%(categoryExport))
    if not isinstance(area, str) and not isinstance(area, unicode):
        area = str(area)

    requestString.append("&area=%s"%(area))
    if not isinstance(district, str) and not isinstance(district, unicode):
        district = str(district)

    requestString.append("&district=%s"%(district))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1372)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1372)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categoryExport', u'area', u'district', u'currentVolume', u'cumulativeVolume', u'currentValue', u'cumulativeValue', u'samePeriodLastYearVolume', u'samePeriodLastYearValue', u'samePeriodLastYearCumulativeVolume', u'samePeriodLastYearCumulativeValue', u'unitVolume', u'unitValue', u'enFrequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categoryExport': 'str','area': 'str','district': 'str','unitVolume': 'str','unitValue': 'str','enFrequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppMSBestSellerJDWGet(beginDate = "", endDate = "", categorySalesLevelTwo = "", field = "", pandas = "1"):
    """
    包含家用电器行业畅销型号在家电大类中占有率以及该型号均价等数据，具体内容可参见数据样例；历史数据从2011年2月开始，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categorySalesLevelTwo: 家电大类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppMSBestSellerJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categorySalesLevelTwo, str) and not isinstance(categorySalesLevelTwo, unicode):
        categorySalesLevelTwo = str(categorySalesLevelTwo)

    requestString.append("&categorySalesLevelTwo=%s"%(categorySalesLevelTwo))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1373)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1373)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categorySalesLevelTwo', u'brand', u'model', u'averagePrice', u'unitAveragePrice', u'marketShare', u'unitMarketShare', u'en_Frequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categorySalesLevelTwo': 'str','brand': 'str','model': 'str','unitAveragePrice': 'str','unitMarketShare': 'str','en_Frequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppMSCategoryLevelOneJDWGet(beginDate = "", endDate = "", categorySalesLevelOne = "", field = "", pandas = "1"):
    """
    包含家用电器行业畅销品牌在家电品类中占有率等数据，具体内容可参见数据样例；历史数据从2011年2月开始，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categorySalesLevelOne: 家电品类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppMSCategoryLevelOneJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categorySalesLevelOne, str) and not isinstance(categorySalesLevelOne, unicode):
        categorySalesLevelOne = str(categorySalesLevelOne)

    requestString.append("&categorySalesLevelOne=%s"%(categorySalesLevelOne))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1374)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1374)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categorySalesLevelOne', u'brand', u'marketShare', u'unitMarketShare', u'frequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categorySalesLevelOne': 'str','brand': 'str','unitMarketShare': 'str','frequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppMSCategoryLevelTwoJDWGet(beginDate = "", endDate = "", categorySalesLevelTwo = "", field = "", pandas = "1"):
    """
    包含家用电器行业畅销品牌在家电大类中占有率等数据，具体内容可参见数据样例；历史数据从2011年2月开始，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categorySalesLevelTwo: 家电大类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppMSCategoryLevelTwoJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categorySalesLevelTwo, str) and not isinstance(categorySalesLevelTwo, unicode):
        categorySalesLevelTwo = str(categorySalesLevelTwo)

    requestString.append("&categorySalesLevelTwo=%s"%(categorySalesLevelTwo))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1375)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1375)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categorySalesLevelTwo', u'brand', u'marketShare', u'unitMarketShare', u'enFrequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categorySalesLevelTwo': 'str','brand': 'str','unitMarketShare': 'str','enFrequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppOutputJDWGet(beginDate = "", endDate = "", categoryOutput = "", region = "", field = "", pandas = "1"):
    """
    包含家用电器行业分地区、分大类的产量数据，如当月产量、累计产量、当月同比、累计同比等数据，具体内容可参见数据样例；历史数据从2011年2月开始，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categoryOutput: 家电大类名称，可模糊查询,可空
    :param region: 地区,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppOutputJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categoryOutput, str) and not isinstance(categoryOutput, unicode):
        categoryOutput = str(categoryOutput)

    requestString.append("&categoryOutput=%s"%(categoryOutput))
    if not isinstance(region, str) and not isinstance(region, unicode):
        region = str(region)

    requestString.append("&region=%s"%(region))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1376)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1376)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categoryOutput', u'region', u'currentVolume', u'cumulativeVolume', u'currentYearOnYear', u'cumulativeYearOnYear', u'unitVolume', u'unitYearOnYear', u'enFrequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categoryOutput': 'str','region': 'str','unitVolume': 'str','unitYearOnYear': 'str','enFrequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppProductCategoryExptJDWGet(beginDate = "", endDate = "", cnProduct = "", categoryExport = "", field = "", pandas = "1"):
    """
    包含家用电器行业分产品、分品类的出口数据，如当期出口、累计出口、去年同期出口、去年同期累计出口等数据，具体内容可参见数据样例；历史数据从2011年1月开始，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param cnProduct: 家电产品名称，可模糊查询,可空
    :param categoryExport: 家电品类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppProductCategoryExptJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(cnProduct, str) and not isinstance(cnProduct, unicode):
        cnProduct = str(cnProduct)

    requestString.append("&cnProduct=%s"%(cnProduct))
    if not isinstance(categoryExport, str) and not isinstance(categoryExport, unicode):
        categoryExport = str(categoryExport)

    requestString.append("&categoryExport=%s"%(categoryExport))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1377)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1377)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDt', u'cnProduct', u'categoryExport', u'currentVolume', u'cumulativeVolume', u'currentValue', u'cumulativeValue', u'samePeriodLastYearVolume', u'samePeriodLastYearValue', u'samePeriodLastYearCumulativeVolume', u'samePeriodLastYearCumulativeValue', u'unit_volume', u'unit_value', u'en_frequency', u'update_time']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'cnProduct': 'str','categoryExport': 'str','unit_volume': 'str','unit_value': 'str','en_frequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppDistrictCategoryExptCJDWGet(beginDate = "", endDate = "", categoryExport = "", area = "", district = "", field = "", pandas = "1"):
    """
    家用电器行业分出口地区、分品类的出口等最近一次公布的数据，如当期出口、累计出口、去年同期出口、去年同期累计出口等数据，具体内容可参见数据样例；仅包含最新一期数据，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categoryExport: 家电品类名称，可模糊查询,可空
    :param area: 省市,可空
    :param district: 地区,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppDistrictCategoryExptCJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categoryExport, str) and not isinstance(categoryExport, unicode):
        categoryExport = str(categoryExport)

    requestString.append("&categoryExport=%s"%(categoryExport))
    if not isinstance(area, str) and not isinstance(area, unicode):
        area = str(area)

    requestString.append("&area=%s"%(area))
    if not isinstance(district, str) and not isinstance(district, unicode):
        district = str(district)

    requestString.append("&district=%s"%(district))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1378)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1378)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categoryExport', u'area', u'district', u'currentVolume', u'cumulativeVolume', u'currentValue', u'cumulativeValue', u'samePeriodLastYearVolume', u'samePeriodLastYearValue', u'samePeriodLastYearCumulativeVolume', u'samePeriodLastYearCumulativeValue', u'unitVolume', u'unitValue', u'enFrequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categoryExport': 'str','area': 'str','district': 'str','unitVolume': 'str','unitValue': 'str','enFrequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppMSBestSellerCJDWGet(beginDate = "", endDate = "", categorySalesLevelTwo = "", field = "", pandas = "1"):
    """
    家用电器行业畅销型号在家电大类中占有率以及该型号均价等最近一次公布的数据，具体内容可参见数据样例；仅包含最新一期数据，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categorySalesLevelTwo: 家电大类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppMSBestSellerCJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categorySalesLevelTwo, str) and not isinstance(categorySalesLevelTwo, unicode):
        categorySalesLevelTwo = str(categorySalesLevelTwo)

    requestString.append("&categorySalesLevelTwo=%s"%(categorySalesLevelTwo))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1379)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1379)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categorySalesLevelTwo', u'brand', u'model', u'averagePrice', u'unitAveragePrice', u'marketShare', u'unitMarketShare', u'en_Frequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categorySalesLevelTwo': 'str','brand': 'str','model': 'str','unitAveragePrice': 'str','unitMarketShare': 'str','en_Frequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppMSCategoryLevelOneCJDWGet(beginDate = "", endDate = "", categorySalesLevelOne = "", field = "", pandas = "1"):
    """
    家用电器行业畅销品牌在家电品类中占有率等最近一次公布的数据，具体内容可参见数据样例；仅包含最新一期数据，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categorySalesLevelOne: 家电品类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppMSCategoryLevelOneCJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categorySalesLevelOne, str) and not isinstance(categorySalesLevelOne, unicode):
        categorySalesLevelOne = str(categorySalesLevelOne)

    requestString.append("&categorySalesLevelOne=%s"%(categorySalesLevelOne))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1380)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1380)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categorySalesLevelOne', u'brand', u'marketShare', u'unitMarketShare', u'frequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categorySalesLevelOne': 'str','brand': 'str','unitMarketShare': 'str','frequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppMSCategoryLevelTwoCJDWGet(beginDate = "", endDate = "", categorySalesLevelTwo = "", field = "", pandas = "1"):
    """
    家用电器行业畅销品牌在家电大类中占有率等最近一次公布的数据，具体内容可参见数据样例；仅包含最新一期数据，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categorySalesLevelTwo: 家电大类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppMSCategoryLevelTwoCJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categorySalesLevelTwo, str) and not isinstance(categorySalesLevelTwo, unicode):
        categorySalesLevelTwo = str(categorySalesLevelTwo)

    requestString.append("&categorySalesLevelTwo=%s"%(categorySalesLevelTwo))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1381)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1381)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categorySalesLevelTwo', u'brand', u'marketShare', u'unitMarketShare', u'enFrequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categorySalesLevelTwo': 'str','brand': 'str','unitMarketShare': 'str','enFrequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppOutputCJDWGet(beginDate = "", endDate = "", categoryOutput = "", region = "", field = "", pandas = "1"):
    """
    家用电器行业分地区、分大类的产量等最近一次公布的数据，如当月产量、累计产量、当月同比、累计同比等数据，具体内容可参见数据样例；仅包含最新一期数据，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param categoryOutput: 家电大类名称，可模糊查询,可空
    :param region: 地区,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppOutputCJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(categoryOutput, str) and not isinstance(categoryOutput, unicode):
        categoryOutput = str(categoryOutput)

    requestString.append("&categoryOutput=%s"%(categoryOutput))
    if not isinstance(region, str) and not isinstance(region, unicode):
        region = str(region)

    requestString.append("&region=%s"%(region))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1382)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1382)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDate', u'categoryOutput', u'region', u'currentVolume', u'cumulativeVolume', u'currentYearOnYear', u'cumulativeYearOnYear', u'unitVolume', u'unitYearOnYear', u'enFrequency', u'updateTime']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'categoryOutput': 'str','region': 'str','unitVolume': 'str','unitYearOnYear': 'str','enFrequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

def HomeAppProductCategoryExptCJDWGet(beginDate = "", endDate = "", cnProduct = "", categoryExport = "", field = "", pandas = "1"):
    """
    家用电器行业分产品、分品类的出口等最近一次公布的数据，如当期出口、累计出口、去年同期出口、去年同期累计出口等数据，具体内容可参见数据样例；仅包含最新一期数据，数据按月更新。
    
    :param beginDate: 开始日期，所查询的数据起始时间，输入格式“YYYYMMDD”,可空
    :param endDate: 截止日期，所查询的数据结束时间，输入格式“YYYYMMDD”,可空
    :param cnProduct: 家电产品名称，可模糊查询,可空
    :param categoryExport: 家电品类名称，可模糊查询,可空
    :param field: 所需字段,可以是列表,可空
    :param pandas: 1表示返回 pandas data frame，0表示返回csv,可空
    :return: :raise e: API查询的结果，是CSV或者被转成pandas data frame；若查询API失败，返回空data frame； 若解析失败，则抛出异常
    """
        
    pretty_traceback()
    frame = inspect.currentframe()
    func_name, cache_key = get_cache_key(frame)
    cache_result = get_data_from_cache(func_name, cache_key)
    if cache_result is not None:
        return cache_result
    split_index = None
    split_param = None
    httpClient = api_base.__getConn__()    
    requestString = []
    requestString.append('/api/HHEA/getHomeAppProductCategoryExptCJDW.csv?ispandas=1&') 
    try:
        beginDate = beginDate.strftime('%Y%m%d')
    except:
        beginDate = beginDate.replace('-', '')
    requestString.append("beginDate=%s"%(beginDate))
    try:
        endDate = endDate.strftime('%Y%m%d')
    except:
        endDate = endDate.replace('-', '')
    requestString.append("&endDate=%s"%(endDate))
    if not isinstance(cnProduct, str) and not isinstance(cnProduct, unicode):
        cnProduct = str(cnProduct)

    requestString.append("&cnProduct=%s"%(cnProduct))
    if not isinstance(categoryExport, str) and not isinstance(categoryExport, unicode):
        categoryExport = str(categoryExport)

    requestString.append("&categoryExport=%s"%(categoryExport))
    requestString.append("&field=")
    if hasattr(field,'__iter__') and not isinstance(field, str):
        if len(field) > 100 and split_param is None:
            split_index = len(requestString)
            split_param = field
            requestString.append(None)
        else:
            requestString.append(','.join(field))
    else:
        requestString.append(field)
    if split_param is None:
        csvString = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
        if csvString is None or len(csvString) == 0 or (csvString[0] == '-' and not api_base.is_no_data_warn(csvString, False)) or csvString[0] == '{':
            api_base.handle_error(csvString, 1383)
        elif csvString[:2] == '-1':
            csvString = ''
    else:
        p_list = api_base.splist(split_param, 100)
        csvString = []
        for index, item in enumerate(p_list):
            requestString[split_index] = ','.join(item)
            temp_result = api_base.__getCSV__(''.join(requestString), httpClient, gw=True)
            if temp_result is None or len(temp_result) == 0 or temp_result[0] == '{' or (temp_result[0] == '-' and not api_base.is_no_data_warn(temp_result, False)):
                api_base.handle_error(temp_result, 1383)
            if temp_result[:2] != '-1':
                csvString.append(temp_result if len(csvString) == 0 else temp_result[temp_result.find('\n')+1:])
        csvString = ''.join(csvString)

    if len(csvString) == 0:
        if 'field' not in locals() or len(field) == 0:
            field = [u'periodDt', u'cnProduct', u'categoryExport', u'currentVolume', u'cumulativeVolume', u'currentValue', u'cumulativeValue', u'samePeriodLastYearVolume', u'samePeriodLastYearValue', u'samePeriodLastYearCumulativeVolume', u'samePeriodLastYearCumulativeValue', u'unit_volume', u'unit_value', u'en_frequency', u'update_time']
        if hasattr(field, '__iter__') and not isinstance(field, str):
            csvString = ','.join(field) + '\n'
        else:
            csvString = field + '\n'
    if pandas != "1":
        put_data_in_cache(func_name, cache_key, csvString)
        return csvString
    try:
        myIO = StringIO(csvString)
        pdFrame = pd.read_csv(myIO, dtype = {'cnProduct': 'str','categoryExport': 'str','unit_volume': 'str','unit_value': 'str','en_frequency': 'str'},  )
        put_data_in_cache(func_name, cache_key, pdFrame)
        return pdFrame
    except Exception as e:
        raise e
    finally:
        myIO.close()

