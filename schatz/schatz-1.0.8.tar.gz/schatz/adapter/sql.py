import sqlalchemy as sa


def get_table_name_with_token(schatz_env, dataset):
    return schatz_env.token + "." + dataset.name


class SqlAlchemyAdapter:

    def __init__(self, schatz_env):
        self.schatz_env = schatz_env
        self._sql_engine = sa.create_engine(self.schatz_env.get_storage_endpoint())

    def connect_sql_alchemy(self):
        return self._sql_engine.connect()
