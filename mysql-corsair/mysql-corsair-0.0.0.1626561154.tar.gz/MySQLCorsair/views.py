from sql_query_helpers import execute_sql, get_sql_result
import random

def create_view(view_name, source_conn_dict, target_conn_dict):
    view_creation_ddl = "SHOW CREATE VIEW {0}".format(view_name)
    view_creation_statement = get_sql_result(
        view_creation_ddl, source_conn_dict
    )[0][1].replace(
        'CREATE', 'CREATE OR REPLACE'
    ).replace(
        'webapp', target_conn_dict['user']
    )
    execute_sql(
        view_creation_statement, target_conn_dict
    )

def list_views(conn_dict):
    return [i[0] for i in get_sql_result(
        "show full tables where table_type = 'VIEW';", conn_dict
    )]

def create_views(source_conn_dict, target_conn_dict):
    remaining_views = list_views(source_conn_dict)
    print(
        "\nWe want the following views from {0}: {1}.\n".format(
            source_conn_dict['db'], remaining_views
        )
    )

    while len(remaining_views) > 0:
        print("Choosing a random view.")
        random_view = random.choice(remaining_views)

        try:
            create_view(random_view, source_conn_dict, target_conn_dict)
            remaining_views.remove(random_view)
            print "Created the view {0}.".format(random_view)
        # Can't figure out how to get _mysql_exceptions explicitly
        except Exception as e:
            print e
            print "Could not create view {0} yet.".format(random_view)


    
