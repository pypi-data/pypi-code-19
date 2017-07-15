from schatz.adapter.pandas import PandasAdapter
from schatz.adapter.sql import SqlAlchemyAdapter
from schatz.environment import SchatzEnv
from schatz.rest import SchatzRest


class SchatzContext:

    def __init__(self):
        self.schatz_env = SchatzEnv()
        self.sqlalchemy = SqlAlchemyAdapter(self.schatz_env)
        self.pandas = PandasAdapter(self.schatz_env, sqlalchemy_adapter=self.sqlalchemy)
        self.rest = SchatzRest(self.schatz_env)