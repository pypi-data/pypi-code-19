def uq_columns(constraint, dummy_table):
    return '_'.join([column.name for column in constraint.columns])

CONVENTION = {
  "ix": "ix_%(table_name)s_%(constraint_name)s",
  "uq": "uq_%(table_name)s_%(uq_columns)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(referred_table_name)s_%(column_0_name)s",
  "pk": "pk_%(table_name)s",

  "uq_columns": uq_columns,
}
