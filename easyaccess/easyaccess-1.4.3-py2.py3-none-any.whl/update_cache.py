import easyaccess as ea

for db in ['dessci','desoper','destest']:
    #
    con = ea.connect(db)
    clean_cache_tables = 'DELETE from DES_ADMIN.CACHE_TABLES'
    clean_cache_cols = 'DELETE from DES_ADMIN.CACHE_COLUMNS'
    
    # empty tables
    con.cur.execute(clean_cache_tables)
    con.cur.execute(clean_cache_cols)
    
    #drop metadata table
    delete_metadata = "drop table fgottenmetadata"
    try:
        con.cur.execute(delete_metadata)
    except:
        pass
    
    # create metadata table
    create_metadata = "create table fgottenmetadata  as  select * from table (fgetmetadata)"
    con.cur.execute(create_metadata)
    
    # get table names
    table_name = """
    select distinct table_name from fgottenmetadata 
    union select distinct t1.owner || '.' || t1.table_name from all_tab_cols t1,
    des_users t2 where upper(t1.owner)=upper(t2.username)
    """

    table_name_destest = """
    select distinct table_name from fgottenmetadata
    union select distinct t1.owner || '.' || t1.table_name from all_tab_cols t1,
    dba_users t2 where upper(t1.owner)=upper(t2.username) and t1.owner not in ('XDB','SYS', 'EXFSYS' ,'MDSYS','WMSYS','ORDSYS')"""
    
    if db == 'destest':
        table_name = table_name_destest
    df = con.query_to_pandas(table_name)
    table_list = df.TABLE_NAME.values.tolist()
    
    # insert bulk
    d = [{'table_name':i} for i in table_list]
    bulk_insert = 'insert into DES_ADMIN.CACHE_TABLES (TABLE_NAME) values (:table_name)'
    con.cur.prepare(bulk_insert)
    con.cur.executemany(None, d)
    
    # get columns
    column_name = """SELECT distinct column_name from fgottenmetadata  order by column_name"""
    
    df = con.query_to_pandas(column_name)
    col_list = df.COLUMN_NAME.values.tolist()
    
    # insert bulk
    d = [{'col_name':i} for i in col_list]
    bulk_insert = 'insert into DES_ADMIN.CACHE_COLUMNS (COLUMN_NAME) values (:col_name)'
    con.cur.prepare(bulk_insert)
    con.cur.executemany(None, d)



