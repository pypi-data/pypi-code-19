"""
Contains DDL objects which are used for Data Domain Language queries on this database.
"""
import typing

from asyncqlio.orm.schema import table as md_table, column as md_column
from asyncqlio.orm.session import SessionBase


class DDLSession(SessionBase):
    """
    A session for executing DDL statements in.
    """
    def create_table(self, table: 'typing.Union[str, md_table.Table]',
                     *columns: 'md_column.Column',
                     primary_key: 'md_table.PrimaryKey' = None,
                     constraints = None):
        """
        Creates a table in this database.

        :param table: The table to create. This can either be a :class:`.Table` object, \
            or a string representing the name of the table.
        :param columns: The columns to add to the table, if the table object was not provided.
        :param primary_key: A :class:`.PrimaryKey` representing the primary key of a table.
            If none is provided, this will automatically generate one.
        :param constraints: A list of :class:`.Constraint` objects to use when creating the table.
        :param indexes: A list of :class:`.Index` objects to use when creating the table.
        """


