import logging
from database_structure import DatabaseStructure
from data_pulling_helpers import get_from_source_and_write_to_target
from command_helpers import get_default_tables, get_most_recent_ids
from data_slices.network_x_graph import NetworkXGraph
from data_slices.graph import Graph
from sql_query_helpers import (
    convert_to_query_ready_string, drop_and_create, 
    get_sql_result, list_tables
)
from views import create_views


logger = logging.getLogger(__name__)


def create_structure(source_db_conn_dict, target_db_conn_dict,
                     config_file_path=None):
    drop_and_create(target_db_conn_dict)
    d = initialize_database_structure(source_db_conn_dict, target_db_conn_dict)
    d.initially_populate(source_db_conn_dict)
    d.recursively_perform_operations('createstructure')
    get_default_tables(source_db_conn_dict, target_db_conn_dict)
    create_views(source_db_conn_dict, target_db_conn_dict)


def delete_data(source_db_conn_dict, target_db_conn_dict):
    d = initialize_database_structure(source_db_conn_dict, target_db_conn_dict)
    d.initially_populate(target_db_conn_dict)
    d.recursively_perform_operations('deletedata')
    get_default_tables(source_db_conn_dict, target_db_conn_dict)


def fill_foreign_keys(source_db_conn_dict, target_db_conn_dict,
    sourcetables):
    d = initialize_database_structure(
        source_db_conn_dict, target_db_conn_dict
    )
    fks = d.foreign_keys

    if sourcetables is not None:
        fks = [
            f for f in fks 
            if f.source_table in sourcetables.split(",")
        ]

    for fk in fks:
        logger.info(
            "Looking at foreign key " \
            "from {0}.{1} to {2}.{3}.".format(
                fk.source_table, fk.source_column,
                fk.target_table, fk.target_column
            )
        )
        first_sql_query = "SELECT DISTINCT {0} FROM {1}".format(
            fk.source_column,
            fk.source_table
        )

        raw_values_we_have = get_sql_result(
            first_sql_query,
            target_db_conn_dict
        )
        values_we_have = convert_to_query_ready_string(
            raw_values_we_have
        )

        logger.info(
            "We have {0} values " \
            "for {1}.{2}.".format(
                len(raw_values_we_have), fk.source_table,
                fk.source_column
            )
        )


        first_where_clause = "{0} IN {1}".format(
            fk.target_column,
            values_we_have
        )

        second_sql_query = "SELECT DISTINCT {0} FROM {1} WHERE {2}".format(
            fk.target_column,
            fk.target_table,
            first_where_clause
        )

        if values_we_have != '()':
            raw_values_we_want = get_sql_result(
                second_sql_query,
                source_db_conn_dict
            )
            values_we_want = convert_to_query_ready_string(
                raw_values_we_want
            )
            
            if values_we_want != '()':
                second_where_clause = "{0} IN {1}".format(
                    fk.target_column, 
                    values_we_want
                )
                logger.info("So, getting {0} corresponding values " \
                    "from {1}.{2}.".format(
                        len(raw_values_we_want),
                        fk.target_table,
                        fk.target_column
                    )
                )
                get_from_source_and_write_to_target(
                    table_name=fk.target_table, 
                    where_clause=second_where_clause,
                    source_conn_dict=source_db_conn_dict,
                    target_conn_dict=target_db_conn_dict,
                    overwrite=False
                )
            else:
                logger.info("No corresponding values to get.")

        logger.info("")


def get_all_from_table(table_name, source_db_conn_dict, 
                       target_db_conn_dict, where="0=0"):
    logger.info(
        "Filling the table {0}{1}.\n".format(
            table_name, '' if not where else " where {}".format(where)
        )
    )
    get_from_source_and_write_to_target(
        table_name, where, source_db_conn_dict, target_db_conn_dict,
        overwrite=True
    )


def get_most_recent(table, column, howmany, where, 
    source_db_conn_dict, target_db_conn_dict, 
    heavy=False, restriction_string='',
    include_only=None, overwrite=False
    ):
        logger.info(
            "Getting the most recent {0} records " \
            "from the table {1} " \
            "that satisfy the condition '{2}' " \
            "(and associated records).\n".format(
                howmany, table, where
            )
        )

        ids = get_most_recent_ids(
            table, column, howmany, where, source_db_conn_dict
        )
        pull_data(
            table, column, ids, source_db_conn_dict, target_db_conn_dict,
            heavy, restriction_string, include_only, overwrite
        )


def initialize_database_structure(source_db_conn_dict, target_db_conn_dict):
    table_list = list_tables(source_db_conn_dict)
    d = DatabaseStructure(
        table_list,
        source_db_conn_dict,
        target_db_conn_dict
    )
    return d


def pull_data(table, column, column_values, source_db_conn_dict,
              target_db_conn_dict, heavy=False, restriction_string='',
              include_only=None, overwrite=False):
    logger.info(
        "Getting all records from table {0} " \
        "that satisfy the condition '{1} IN {2}' " \
        "(and associated records).\n".format(
            table, column, column_values
        )
    )
    structure_data = initialize_database_structure(
        source_db_conn_dict, target_db_conn_dict
    )

    networkx_graph = NetworkXGraph(
        structure_data, restriction_string, include_only
    ).graph_literal

    g = Graph(
        networkx_graph,
        source_db_conn_dict, target_db_conn_dict,
        heavy, overwrite
    )

    logger.info(
        "Traversing the graph.\n"
    )
    g.equip_initial_node(table, column, column_values)

    while g.nodes_left_to_visit():
        current_node = g.next()

        for edge in current_node.get_edges(g):
            if edge in g.edges_visited:
                logger.debug(
                    "Not visiting edge {0}, already been visited".format(
                        edge.to_string()
                    )
                )
            else:
                g.account_for_edge(edge, current_node)
                g.add_edge_visited(edge)
                g.add_node_to_visit(g.get_other_node(edge, current_node))
        logger.debug("Nodes left to visit: {0}\n".format(
            [node.name for node in g.nodes_to_visit]
        ))
    logger.info(
        "Done traversing the graph.\n"
    )

    nodes = g.nodes
    if include_only:
        nodes = [n for n in g.nodes if n.name in include_only]
    for node in nodes:
        row_count = int(node.row_count()[0][0])
        if row_count == 1:
            logger.info("Getting {0} row from {1}.".format(
                row_count, node.name
            ))
        else:
            logger.info("Getting {0} rows from {1}.".format(
                row_count, node.name
            ))

        if row_count > 0 and row_count < 100000:
            get_from_source_and_write_to_target(
                node.name, node.compute_where_clause(), source_db_conn_dict,
                target_db_conn_dict, overwrite
            )
        elif row_count > 0:
            logger.info(
                "Sorry, too many rows in table {0}.".format(node.name)
            )
    logger.info("")
