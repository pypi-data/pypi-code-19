"""
Utility module to work with MySQL databases.
"""

import MySQLdb

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class MysqlUtils:
    """
    Utility class containing methods for working with MySQL databases.

    This utilizes the functionality provided within the MySQLdb driver module to implement
    application-specific methods for interacting with the database.

    The SQL language is sub-divided into several language elements, including:
    - CLAUSES, which are constituent components of statements and queries (optional in some cases)
    - EXPRESSIONS, which can produce either scalar values or tables consisting of columns and rows of data.
    - PREDICATES, which specify conditions that can be evaluated to SQL three-valued logic (3VL)
      or Boolean (true/false/unknown) truth values and which are used to limit the effects
      of statements and queries, or to change program flow.
    - QUERIES, which retrieve data based on specific criteria.
    - STATEMENTS, which may have a persistent effect on schemas and data, or which may control
      transactions, program flow, connections, sessions, or diagnostics.

    SQL statements also include the semicolon (";") statement terminator. Though not required on every
    platform, it is defined as a standard part of the SQL grammar.
    Insignificant whitespace is generally ignored in SQL statements and queries, making it easier to
    format SQL code for readability.
    """

    def __init__(self, host, user, password, database):
        # connection variables
        self.db_host = host
        self.db_user = user
        self.db_pass = password
        self.db_name = database

        # misc variables
        self.conn_obj = None

    def connect(self):
        """
        Connects to a MySQL database.

        :return: True is connection was successful, ConnectionException if not.
        :rtype: bool

        :raises ConnectionException: Raised if any error occurs during attempt of connection.
        """

        try:
            self.conn_obj = MySQLdb.connect(self.db_host, self.db_user, self.db_pass, self.db_name)
            self.conn_obj.autocommit(True)
            return True
        except Exception:
            return False

    def run_query(self, query_string):
        """
        Runs a user-supplied query on the database.

        :param query_string: The query to be executed on the database.

        :return: Result object of the executed query. False if exception was raised.
        :rtype: str
        """

        try:
            cursor = self.conn_obj.cursor()
            cursor.execute(query_string)

            # extract results of the query from cursor
            query_res = cursor.fetchall()
            cursor.close()

            return str(query_res[0][0])
        except Exception as ex:
            return False

    def fetch_row_count(self, query_string):
        """
        Returns count of rows received after executing supplied query.

        :param query_string: The query to be executed.

        :return: The row count as per obtained result set.
        :rtype: int
        """

        try:
            cursor = self.conn_obj.cursor()
            cursor.execute(query_string)

            # extract results of the query from cursor
            query_res = cursor.fetchall()
            cursor.close()

            return len(query_res)
        except Exception as ex:
            return False

    def fetch_row_by_key(self, table_name, key):
        """
        Retrieves a single row from the database based on supplied key.

        It returns a dictionary after mapping the row values with the corresponding field names.

        :param table_name: The table from which to fetch the row.
        :param key: The primary key required to access the row.

        :return: Dictionary, if the row exists, else returns False.
        :rtype: dict
        """

        pass

    def fetch_row_by_query(self, query_string):
        """
        Retrieves a single row from the database based on supplied query.

        It returns a dictionary after mapping the row values with the corresponding field names.
        The query supplied should ensure that the output returned is a single unique row as otherwise
        the results may be unexpected.

        :param query_string: The query string used to retrieve the row.

        :return: Dictionary, if the row exists, else returns False.
        :rtype: dict

        :raises Exception: Raises a general exception on encountering an error.
        """

        try:
            result_map = {}
            cursor = self.conn_obj.cursor()
            cursor.execute(query_string)

            # obtain field names from the table and store in a list
            name_to_index = [i[0] for i in cursor.description]

            # extract results of the query from cursor
            query_res = cursor.fetchall()
            cursor.close()

            # map query results with field names obtained above
            field_ctr = 0
            for row in query_res:
                for field in name_to_index:
                    result_map[field] = row[field_ctr]
                    field_ctr += 1

                    if field_ctr >= len(name_to_index):
                        field_ctr = 0

            return result_map
        except Exception as ex:
            return False

    def disconnect(self):
        """
        Disconnect from the currently connected database.

        :return: True, if successfully disconnected, False otherwise.
        :rtype: bool
        """

        if self.conn_obj:
            self.conn_obj.close()

            return True

        return False
