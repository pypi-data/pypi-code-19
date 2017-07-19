import pandas as pd
from pony import orm
from pony.orm import db_session
from pewsql import pearson_corr

"""
You need to create a user for test

1. PostgresSQL
    CREATE DATABASE pewsql_test;
    CREATE USER pewsql WITH PASSWORD '1234'
    GRANT ALL PRIVILEGES ON DATABASE pewsql_test to pewsql;
"""
DATABASE = 'pewsql_test'
DB_USER = 'pewsql'
DB_HOST = 'localhost'
DB_PASSWORD = '1234'


def test_pearson_correlation():
    data = pd.DataFrame({'city': [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
                         'age': [43, 21, 25, 42, 57, 59, 70, 60, 50, 40, 35, 24],
                         'glucose': [99, 65, 79, 75, 87, 81, 1, 3, 6, 10, 20, 22]})

    db = orm.Database()
    db.bind(provider='postgres', user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DATABASE)

    # Create Table
    class Pearson(db.Entity):
        id = orm.PrimaryKey(int, auto=True)
        city = orm.Required(int)
        age = orm.Required(int)
        glucose = orm.Required(int)

    db.generate_mapping(create_tables=True)

    # Insert Data
    @db_session
    def insert_data(data):
        if Pearson.select().count():
            return None

        for i, d in data.iterrows():
            city = int(d.city)
            age = int(d.age)
            glucose = int(d.glucose)
            ent = Pearson(city=city, age=age, glucose=glucose)

        orm.commit()

    insert_data(data)

    # Create a query
    query = pearson_corr(x='pearson.age', y='pearson.glucose', group_by=['pearson.city'])
    with db_session:
        result1 = db.select(query)

    query = pearson_corr(x='pearson.age', y='pearson.glucose')
    with db_session:
        result2 = db.select(query)

    # Test
    assert result1[0] == (1, 0.529808901890174)
    assert result1[1] == (2, -0.945671421044784)
    assert result2[0] == -0.204369399812033
