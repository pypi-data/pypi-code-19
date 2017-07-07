__author__ = "alii"
__date__ = 28 / 12 / 2016
__copyright__ = ""
__credits__ = [""]
__license__ = ""
__maintainer__ = "Imran Ali"
__email__ = "imran.ali@kapsch.net"
__status__ = "Development"
__revision__ = ""


import pandas as pd
from datetime import datetime, timedelta, date
import cx_Oracle
from os.path import expanduser
import sys
import os
import logging

logger = logging.getLogger(__name__)

home = os.path.dirname(os.path.realpath(__file__))
os.chdir(home)


def dump(conn, queryParms, table, filename=r"HostTrxDump.csv", sTime= "2016-10-27 21:00:00", dumptocsv=False, secs=3600):
    """uses provided database connection and query string to dump data into
     pandas dataframe. Optionally can also load it into csv"""
    startTime = sTime
    endTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
    endTime+=timedelta(seconds=secs)
    if table == 'VEHICLE_TRANSACTION':
        q = ("select " + ",".join(queryParms) + " from VEHICLE_TRANSACTION where TRANSACTION_TIMESTAMP between TO_DATE('" + startTime + "','YYYY-MM-DD HH24:MI:SS') and TO_DATE('" + endTime.strftime(
            "%Y-%m-%d %H:%M:%S") + "','YYYY-MM-DD HH24:MI:SS')"

                                   " order by TRANSACTION_TIMESTAMP desc")
        # q = ("select " + ",".join(queryParms) + " from VEHICLE_TRANSACTION where TRANSACTION_TIMESTAMP between TO_DATE('" + startTime + "','YYYY-MM-DD HH24:MI:SS') and TO_DATE('" + endTime.strftime(
        #     "%Y-%m-%d %H:%M:%S") + "','YYYY-MM-DD HH24:MI:SS')")
        df = pd.read_sql_query(q, conn, parse_dates=['TRANSACTION_TIMESTAMP'])
    elif table == 'SIC_PASSAGE':
        q = ("select " + ",".join(queryParms) + " from SIC_PASSAGE where TXN_TIMESTAMP between TO_DATE('" + startTime + "','YYYY-MM-DD HH24:MI:SS') and TO_DATE('" + endTime.strftime(
            "%Y-%m-%d %H:%M:%S") + "','YYYY-MM-DD HH24:MI:SS')"
                                   " order by TXN_TIMESTAMP desc")
        df = pd.read_sql_query(q, conn, parse_dates=['TXN_TIMESTAMP'])
    elif table == 'SIC_RAW_DATA':
        q = ("select " + ",".join(
            queryParms) + " from SIC_RAW_DATA where INSERT_TIME between TO_DATE('" + startTime + "','YYYY-MM-DD HH24:MI:SS') and TO_DATE('" + endTime.strftime(
            "%Y-%m-%d %H:%M:%S") + "','YYYY-MM-DD HH24:MI:SS')"

                                   " order by INSERT_TIME desc")
        # q = "SELECT * FROM SIC_RAW_DATA ORDER BY INSERT_TIME DESC"
        df = pd.read_sql_query(q, conn)
    if dumptocsv == True:
        df.to_csv(filename)
    logger.info(
        "datadump obtained using parameters %s, datetime %s, period %s" % (queryParms, sTime, secs))
    return df
def imageInfoDump(conn, table, filename = r"HostImgInfoDump.csv", sTime="2016-10-27 21:00:00", dumptocsv=False, secs=3600, using ='TRANSACTION_ID'):
    """uses provided database connection and query string to dump image data into
         pandas dataframe. Optionally can also load it into csv"""
    # Query to aggregate image information
    startTime = sTime
    endTime = datetime.strptime(startTime, "%Y-%m-%d %H:%M:%S")
    endTime += timedelta(seconds=secs)
    if table == 'VEHICLE_TRANSACTION':
        qry = """
        select
        transaction_id,
          NVL(listagg(camera_type, ' ') within group (order by camera_type), 'No image available') as images
        from vehicle_image where TRIGGER_TIME between TO_DATE('""" + startTime + """','YYYY-MM-DD HH24:MI:SS') and TO_DATE('""" + endTime.strftime(
                "%Y-%m-%d %H:%M:%S") + """','YYYY-MM-DD HH24:MI:SS')
        group by transaction_id"""
        df_imageInfo = pd.read_sql_query(qry,conn,index_col=['TRANSACTION_ID'])
    elif table == 'SIC_PASSAGE':
        qry =  """
        select
        txn_number,
            NVL(listagg(image_type, ',') within group (order by image_type), 'No_image_available') as images
        from sic_image where capture_timestamp between TO_DATE('""" + startTime + """','YYYY-MM-DD HH24:MI:SS') and TO_DATE('""" + endTime.strftime(
                "%Y-%m-%d %H:%M:%S") + """','YYYY-MM-DD HH24:MI:SS')
        group by txn_number"""
        df_imageInfo = pd.read_sql_query(qry,conn,index_col=['TXN_NUMBER'])
    if dumptocsv == True:
        df_imageInfo.to_csv(filename)
        print "files available under: " + str(home)
    logger.info(
        "image dataframe obtained using parameters %s, datetime %s, period %s" % (conn, startTime, secs))
    return df_imageInfo

if __name__ == '__main__':
    print "cannot be used as standalone app as this time, please import this module to use its functionality"

    # filename = r"C:\Users\alii\Desktop\ORB\LSIORB validation documents\HostTrxDump.csv"
    # db_connection_string = 'aetdbuser/hello123@172.30.65.51/aethostdb'
    # conn = cx_Oracle.connect(db_connection_string)
    # csvdump(conn, filename)
