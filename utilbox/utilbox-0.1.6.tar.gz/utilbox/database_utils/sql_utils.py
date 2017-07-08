"""
Utility module to work with SQL queries.
"""

__author__ = "Jenson Jose"
__email__ = "jensonjose@live.in"
__status__ = "Production"


class SqlUtils:
    """
    Utility class containing methods for working with SQL queries.
    """

    def __init__(self):
        pass

    @staticmethod
    def build_select_query(table_name,
                           column_list=None,
                           clause_map=None,
                           quote_values=False,
                           use_single_quotes=False):
        """
        Combines required components to form an SQL SELECT query.

        :param table_name: The name of table on which query is to be executed.
        :param column_list: The list of columns whose data is to be retrieved.
        :param clause_map: Clauses to be applied within the query.
        :param quote_values:
        :param use_single_quotes:

        :return: The final query string to be executed.
        :rtype: str
        """

        if column_list is None:
            column_list = []

        if clause_map is None:
            clause_map = {}

        query_string = "SELECT "
        column_string = ""
        clause_string = ""

        if len(column_list) > 0:
            item_ctr = 1
            for column in column_list:
                column_string += column

                if item_ctr < len(column_list):
                    column_string += ", "

                item_ctr += 1
        else:
            column_string = "*"

        if len(clause_map) > 0:
            item_ctr = 1
            clause_string = " WHERE "
            clause_condition = " AND "

            for field, value in clause_map.iteritems():
                if quote_values:
                    if use_single_quotes:
                        value = "\'" + str(value) + "\'"
                    else:
                        value = "\"" + str(value) + "\""

                clause_string += str(field) + "=" + str(value)

                if item_ctr < len(clause_map):
                    clause_string += clause_condition

                item_ctr += 1

        if clause_string != "":
            query_string += column_string + " FROM " + str(table_name) + clause_string + ";"
        else:
            query_string += column_string + " FROM " + str(table_name) + ";"

        return query_string

    @staticmethod
    def build_insert_query(table_name,
                           value_list,
                           quote_values=False,
                           use_single_quotes=False):
        """

        :param table_name:
        :param value_list:
        :param quote_values:
        :param use_single_quotes:
        :return:
        """

        if len(value_list) > 0:
            statement_string = "INSERT INTO " + str(table_name) + " VALUES ("
            item_ctr = 1

            for value in value_list:
                if quote_values:
                    if use_single_quotes:
                        value = "\'" + str(value) + "\'"
                    else:
                        value = "\"" + str(value) + "\""

                statement_string += value

                if item_ctr < len(value_list):
                    statement_string += ", "

                item_ctr += 1

            statement_string += ");"

            return statement_string

        return False

    @staticmethod
    def build_insert_query_with_fields(table_name,
                                       field_list,
                                       value_list,
                                       quote_values=False,
                                       use_single_quotes=False):
        """

        :param table_name:
        :param field_list:
        :param value_list:
        :param quote_values:
        :param use_single_quotes:
        :return:
        """

        if len(value_list) > 0:
            statement_string = "INSERT INTO " + \
                               str(table_name) + \
                               " ("
            field_ctr = 1

            for field in field_list:
                if quote_values:
                    if use_single_quotes:
                        field = "\'" + str(field) + "\'"
                    else:
                        field = "\"" + str(field) + "\""

                statement_string += field

                if field_ctr < len(field_list):
                    statement_string += ", "

                field_ctr += 1

            statement_string += ") VALUES ("
            value_ctr = 1

            for value in value_list:
                if quote_values:
                    if use_single_quotes:
                        value = "\'" + str(value) + "\'"
                    else:
                        value = "\"" + str(value) + "\""

                statement_string += value

                if value_ctr < len(value_list):
                    statement_string += ", "

                value_ctr += 1

            statement_string += ");"

            return statement_string

        return False

    @staticmethod
    def build_update_query(table_name,
                           new_value_map,
                           clause_map=None,
                           quote_values=False,
                           use_single_quotes=False):
        """

        :param table_name:
        :param new_value_map:
        :param clause_map:
        :param quote_values:
        :param use_single_quotes:
        :return:
        """

        if clause_map is None:
            clause_map = {}

        clause_string = ""

        if len(new_value_map) > 0:
            statement_string = "UPDATE " + str(table_name) + " SET "
            item_ctr = 1

            for field, new_value in new_value_map.iteritems():
                if quote_values:
                    if use_single_quotes:
                        new_value = "\'" + str(new_value) + "\'"
                    else:
                        new_value = "\"" + str(new_value) + "\""

                statement_string += str(field) + "=" + str(new_value)

                if item_ctr < len(new_value_map):
                    statement_string += ", "

                item_ctr += 1
        else:
            return False

        if len(clause_map) > 0:
            item_ctr = 1
            clause_string = " WHERE "
            clause_condition = " AND "

            for field, value in clause_map.iteritems():
                if quote_values:
                    if use_single_quotes:
                        value = "\'" + str(value) + "\'"
                    else:
                        value = "\"" + str(value) + "\""

                clause_string += str(field) + "=" + str(value)

                if item_ctr < len(clause_map):
                    clause_string += clause_condition

                item_ctr += 1

        statement_string += clause_string + ";"

        return statement_string
