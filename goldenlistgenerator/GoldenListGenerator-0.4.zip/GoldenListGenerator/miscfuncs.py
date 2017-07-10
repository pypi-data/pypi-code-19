
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def removeTrxWithEmptyFields(df,empfields_to_rem):
    """removes rows with empfields_to_rem and return dataframe"""
    for field in empfields_to_rem:
        if field in df:
            df1 = replaceEmptyFields(df, field, np.nan)
            df1.dropna(subset=field.split(), inplace=True)
            return df1
        else:
            return df
def replaceEmptyFields(dataframe, field=None, With=np.nan, InPlace=True):
    """replaces empty rows for specified fields with NaN(default) and return dataframe"""
    if field is not None:
        if field in dataframe:
            dataframe[field].replace('', With, inplace=InPlace)
            logger.info("field %s replaced with %s in dataframe" %(field,With))
        return dataframe
    else:
        logger.info("field %s found returning " % (field))
        return dataframe

def countTrxWithEmptyFields(df,empfields):
    """counts rows with empfields and returns the amount"""
    for field in empfields:
        df1 = replaceEmptyFields(df.copy(), field, np.nan)
        df1.dropna(subset=field.split(), inplace=True)
        logger.info("dropping NAN data for %s" % (field))
    return (len(df.index)-len(df1.index))
def dtypeConsistency(dataframe1, dataframe2, parameter_list):
    """if a paramater exists in both dataframes, try to make the dtype for that parameter in dataframe1
    equal to the dtype of the parameter in dataframe2"""
    for parameter in parameter_list:
        if parameter in dataframe1:
            if parameter in dataframe2:
                dataframe1[parameter] = dataframe1[parameter].astype(dataframe2[parameter])
                logger.info("setting dataframe1 paramater of same type as dataframe 2 parameter for %s" %(parameter))
    return

def FiltDBToFields(dataframe, dataframe_golden, fields,dontmergeonempfield=True,dropcolafter=None, dropduplpar=None, cleanupColnameWith=None):
    """for fields in golden dataframe, find matching values in dataframe only and return the filtered dataframe
    """
    # this is because float types deal better with NaNs and avoids the error of 'cannot convert NA to integer'
    dataframe=convertIntFloat(dataframe.copy())
    logger.info("convert int to float for dataframe")
    dataframe_golden=convertIntFloat(dataframe_golden.copy())
    logger.debug("convert int to float for dataframe")
    #make sure the fields being used to do the merge are of the same dtype
    dtypeConsistency(dataframe,dataframe_golden,fields)
    if dontmergeonempfield == True:  # this should be the normal case
        dataframe_golden = removeTrxWithEmptyFields(dataframe_golden.copy(),fields)

    dataframe = pd.merge(dataframe.copy(),dataframe_golden.copy(),how='inner', on=fields)
    logger.info("dataframe filtered using %s" %(fields))
    if cleanupColnameWith is not None:
        dataframe = cleanUpColumnName(dataframe.copy(),cleanupColnameWith)
    if dropduplpar is not None:
        dataframe.drop_duplicates(subset=dropduplpar, inplace=True)
        logger.info("dropping duplicates for %s" %(dropduplpar))
    if dropcolafter is not None:
        dataframe.drop(dataframe.columns[dropcolafter:], axis=1, inplace=True)
        logger.info("drop columns after %s" %(dropcolafter))
    return dataframe

def cleanUpColumnName(dataframe, what=None):
    """remove specified string from headers in all columns if it exists"""
    tempheaders = list(dataframe.columns.values)
    finalheaders = []
    if what is not None:
        for header in tempheaders:
            if header.endswith(what):
                header = header[:-(len(what))]
                finalheaders.append(header)
            else:
                finalheaders.append(header)
        dataframe.columns = finalheaders
        logger.info("columns cleaned with %s" %(what))
        return dataframe
    else:
        return
def applyFilter(dataframe, field, value):
    """filter the dataframe to the value for field with value only and return"""
    dataframe = dataframe[(dataframe[field] == value)]
    logger.info("filter applied to dataframe for field %s" %(field) )
    return dataframe

def findIndexWhereValue(df,field,value):
    """return index of where the value is located"""
    logger.info("finding index where value %s for field %s" %(value, field))
    return df[field][df[field] == value].index[0]

def convertIntFloat(dataframe):
    """convert int type to float type for dataframe and return dataframe"""
    for column in dataframe:
        if dataframe[column].dtype == np.int64:
            dataframe[column] = dataframe[column].astype(np.float64)
    logger.info("int to float conversion for dataframe")
    return dataframe

def findTrxsInLeftNotInRight(dataframe_left, dataframe_right, field):
    """ finds rows in left dataframe that do NOT exist in right dataframe and returns the
    left dataframe filtered to those rows"""
    logger.info("set index of left dataframe to %s" %(field))
    dataframe_left.set_index(field, inplace=True)
    logger.info("set index of right dataframe to %s" %(field))
    dataframe_right.set_index(field, inplace=True)
    logger.info("finding rows in left dataframe that do NOT exist in right dataframe returning"
                 "left dataframe filtered to those rows")
    return dataframe_left[~dataframe_left.index.isin(dataframe_right.index)].reset_index()


def assertFrameEqual(df1, df2, **kwds ):
    """ Assert that two dataframes are equal, ignoring ordering of columns"""
    from pandas.util.testing import assert_frame_equal
    return assert_frame_equal(df1.sort_index(axis=1), df2.sort_index(axis=1), check_names=True, **kwds )

def appendTimeInfo(filename,dateNtime,duration):
    if None in (dateNtime, duration):
        return filename
    else:
        completeTime = str(filename) + " " + str(dateNtime) + " " + str(duration) + "hrs"
        completeTime = completeTime.replace(':', '_')
        completeTime = completeTime.replace(' ', '_')
        logger.info("filename after appending datetime info %s" %(completeTime))
        return completeTime

def callPassagebitParser(dataframe, using='PASSAGE_BITMAP'):
    x = pd.Series()
    for index, value in dataframe[using].iteritems():
        ans = parsebitmap.passageParser(value)
        x.set_value(index, ans)
    dataframe['PassageBitmap_Decoded'] = x.to_frame()
    return dataframe