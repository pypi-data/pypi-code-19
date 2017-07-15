import pandas as pd

from schatz.adapter.sql import SqlAlchemyAdapter
from schatz.adapter.sql import get_table_name_with_token


class PandasAdapter:

    def __init__(self, schatz_env, sqlalchemy_adapter=None):
        self.schatz_env = schatz_env
        if sqlalchemy_adapter is None:
            self.sql_alchemy_adapter = SqlAlchemyAdapter(schatz_env)
        else:
            self.sql_alchemy_adapter = sqlalchemy_adapter

    def get_dataframe(self, dataset):
        if self.schatz_env.inited:
            table_name = get_table_name_with_token(self.schatz_env, dataset)
            return pd.read_sql_query('select * from ' + table_name, self.sql_alchemy_adapter.connect_sql_alchemy())
        return None