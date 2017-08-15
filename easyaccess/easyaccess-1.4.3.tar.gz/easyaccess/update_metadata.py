import easyaccess as ea

get_tables = """
insert into DES_ADMIN.CACHE_TABLES (TABLE_NAME)
select distinct t1.owner || '.' || t1.table_name as table_name
from all_tables t1,dba_users t2
where upper(t1.owner)=upper(t2.username)
and t1.owner not in
('XDB','SYS', 'EXFSYS' ,'MDSYS','WMSYS','ORDSYS','ORDDATA','SYSTEM',
'APEX_040200','CTXSYS','OLAPSYS','LBACSYS')
union
select distinct synonym_name as table_name from all_synonyms where table_owner = 'DES_ADMIN'
union
select distinct v1.owner || '.' || v1.view_name as table_name
from all_views v1,dba_users v2
where upper(v1.owner)=upper(v2.username)
and v1.owner not in
('XDB','SYS', 'EXFSYS' ,'MDSYS','WMSYS','ORDSYS','ORDDATA','SYSTEM',
'APEX_040200','CTXSYS','OLAPSYS','LBACSYS')
order by table_name
"""

get_cols = """
insert into DES_ADMIN.CACHE_COLUMNS
select distinct(t.column_name)  as column_name
from
all_tab_columns t ,DES_ADMIN.CACHE_TABLES t2
where t.table_name=t2.table_name
"""


for db in ['dessci', 'desoper', 'destest', 'oldsci']:
    con = ea.connect(db)
    clean_cache_tables = 'DELETE from DES_ADMIN.CACHE_TABLES'
    clean_cache_cols = 'DELETE from DES_ADMIN.CACHE_COLUMNS'
    # empty tables
    con.cur.execute(clean_cache_tables)
    con.cur.execute(clean_cache_cols)
    # fill the tables
    con.cur.execute(get_tables)
    con.cur.execute(get_cols)
    con.close()
