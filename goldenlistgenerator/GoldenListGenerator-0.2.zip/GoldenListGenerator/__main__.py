import hostdatadump, argparse, yaml, cx_Oracle, \
    miscfuncs, sys, logging, os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s[%(levelname)s]: %(message)s')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logger.addHandler(console)



def dumpToCSV(dataframe, filename):
    """dumps the dataframe into a csv file
    accepts dataframe and filename as argument"""
    filename = filename + ".csv"
    logger.info("generating %s to %s" %(filename, os.getcwd()))
    dataframe.to_csv(filename)

def config_loader(filepath):
    """configuration file loader
    accepts file as argument"""
    with open(filepath, 'r') as yamlfile:
        cfg = yaml.load(yamlfile)
    return cfg

def main():
    """main function"""

    from pkg_resources import Requirement, resource_filename
    filename = resource_filename(Requirement.parse("GoldenListGenerator"), "config.yaml")

    parser = argparse.ArgumentParser(description="Generates a golden list(CSV file) using user specified fields. "
                                                 "Program takes in two data sets from the database and finds "
                                                 "common fields between them to generate a golden list")
    parser.add_argument("-cfg", help="configuration file to specify Oracle database connection parameters, "
                                    "SQL query parameters, date and time of the two data sets to sample and"
                                    " number of hours to process, Note: by default 'config.yaml' is used", type=str,
                        default=filename)
    # default = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    #                        "config_goldenlistgenerator.yaml"))

    parser.add_argument("-i", "--imageinfo", help="include image information with raw data, "
                                                  "Note: use with raw data option only", action="store_true")
    parser.add_argument("-r", "--rawdata", help="include raw data dump", action="store_true")
    parser.add_argument("-o", "--goldenoutputfile", help="golden list file name, "
                                                         "Note: if not specified the file will be named "
                                                         "'GoldenVehicleList.csv'", default="GoldenVehicleList")
    args = parser.parse_args()

    cfg = config_loader(args.cfg)

    db_connection = cfg['OracleDBConnectionParameters']['username'] + '/' + cfg['OracleDBConnectionParameters'][
    'password'] + \
                '@' + cfg['OracleDBConnectionParameters']['ip'] + '/' + cfg['OracleDBConnectionParameters']['SID']
    try:
        conn = cx_Oracle.connect(db_connection)
    except cx_Oracle.DatabaseError as e:
        logger.error("failed to connect to database. Check network connection and/or parameters")
        sys.exit(1)

    logger.info("Connected to database")

    df_raw1 = hostdatadump.dump(conn, table=cfg['OracleDBConnectionParameters']['table'],
                                                                          queryParms=cfg['SQLQueryParameters'],
                                                                          sTime=cfg['TimePeriod']['Day1'], secs=cfg['TimePeriod']['Hrs'] * 3600)
    logger.info("retrieved data dump from day 1")
    df_raw2 = hostdatadump.dump(conn, table=cfg['OracleDBConnectionParameters']['table'],
                                                                          queryParms=cfg['SQLQueryParameters'],
                                                                          sTime=cfg['TimePeriod']['Day2'], secs=cfg['TimePeriod']['Hrs'] * 3600)
    logger.info("retrieved data dump from day 2")

    assert (df_raw1.empty == False)
    assert (df_raw2.empty == False)

    assert (len(df_raw1.columns) == len(df_raw2.columns))

    logger.info("finding matching entries in the two data sets for %s" %(cfg['GoldenListSelectionParameters']))
    df1_filt_df2_using_golden = miscfuncs.FiltDBToFields(df_raw1.copy(), df_raw2.copy(),
                                                                                                   cfg['GoldenListSelectionParameters'],
                                                                                                   dropcolafter=len(df_raw1.columns),
                                                                                                   dropduplpar=cfg['GoldenListSelectionParameters'],
                                                                                                   cleanupColnameWith="_x")
    if args.imageinfo:  # if image option is selected
        if args.rawdata:
            df_image1 = hostdatadump.imageInfoDump(conn, table=cfg['OracleDBConnectionParameters']['table'],
                                                                                             sTime=cfg['TimePeriod']['Day1'],
                                                                                             secs=cfg['TimePeriod']['Hrs'] * 3600)
            logger.info("retrieved image data dump from day 1")
            df_image2 = hostdatadump.imageInfoDump(conn, table=cfg['OracleDBConnectionParameters']['table'],
                                                                                             sTime=cfg['TimePeriod']['Day2'],
                                                                                             secs=cfg['TimePeriod']['Hrs'] * 3600)
            logger.info("retrieved image data dump from day 2")

            df_raw1_image = df_raw1.copy()
            df_raw2_image = df_raw2.copy()
            logger.info("mapping transaction data to image data")
            if cfg['OracleDBConnectionParameters']['table'] == 'VEHICLE_TRANSACTION':
                df_raw1_image['Image_Found'] = df_raw1_image.TRANSACTION_ID.map(df_image1.IMAGES)
                df_raw2_image['Image_Found'] = df_raw2_image.TRANSACTION_ID.map(df_image2.IMAGES)
            if cfg['OracleDBConnectionParameters']['table'] == 'SIC_PASSAGE':
                df_raw1_image['Image_Found'] = df_raw1_image.TXN_NUMBER.map(df_image1.IMAGES)
                df_raw2_image['Image_Found'] = df_raw2_image.TXN_NUMBER.map(df_image2.IMAGES)
            if args.rawdata:
                dumpToCSV(df_raw1_image, miscfuncs.appendTimeInfo("rawDataDumpSet1withImg", cfg['TimePeriod']['Day1'],
                                                                                                            cfg['TimePeriod']['Hrs']))
                dumpToCSV(df_raw2_image, miscfuncs.appendTimeInfo("rawDataDumpSet2withImg", cfg['TimePeriod']['Day2'],
                                                                                                            cfg['TimePeriod']['Hrs']))
            dumpToCSV(df1_filt_df2_using_golden, args.goldenoutputfile)
            conn.close()
            sys.exit(0)
        else: # image option has to be selected along with the raw data dump option
            parser.error("image argument has to be used with the raw data argument")
    else:
        if args.rawdata:
            dumpToCSV(df_raw1,
                      miscfuncs.appendTimeInfo("rawDataDumpSet1", cfg['TimePeriod']['Day1'], cfg['TimePeriod']['Hrs']))
            dumpToCSV(df_raw2,
                      miscfuncs.appendTimeInfo("rawDataDumpSet2", cfg['TimePeriod']['Day2'], cfg['TimePeriod']['Hrs']))
        dumpToCSV(df1_filt_df2_using_golden, args.goldenoutputfile)
        conn.close()
        sys.exit(0)

if __name__ == '__main__':
    main()