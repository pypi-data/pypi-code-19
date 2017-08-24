import json
import asyncio

import inflection
import peewee
import peewee_async
from graphene_peewee_async.fields import PeeweeConnectionField
from graphene_peewee_async.types import PeeweeObjectType
from graphene import Schema, Scalar, ObjectType, GlobalID, Mutation, Field, Boolean, Int, List, Node, Dynamic, String, Argument, ID, NonNull, Connection
from graphene_peewee_async.registry import Registry
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql.execution import ExecutionResult
from graphene_peewee_async.fields import TOTAL_FIELD


loop = asyncio.get_event_loop()
db = peewee_async.PooledPostgresqlDatabase('graphene_test', user='postgres', host='localhost')
manager = peewee_async.Manager(db, loop=loop)


class BaseModel(peewee.Model):

    class Meta:
        database = db
        manager = manager


class Race(BaseModel):

    name = peewee.CharField()
    power = peewee.IntegerField()


class Monster(BaseModel):

    name = peewee.CharField()
    age = peewee.IntegerField(null=True)
    race = peewee.ForeignKeyField(Race)


class Author(peewee.Model):

    name = peewee.CharField()


class Book(peewee.Model):

    name = peewee.CharField()
    author = peewee.ForeignKeyField(Author)


class NonLeakAsyncioExecutor(AsyncioExecutor):

    def execute(self, fn, *args, **kwargs):
        result = super().execute(fn, *args, **kwargs)
        self.futures = []
        return result


class PeeweeConnection():

    # count = Int()
    # total = Int()

    def resolve_count(self, args, context, info=None):
        return len(self.edges)

    def resolve_total(self, args, context, info=None):
        if self.edges:
            result = getattr(self.edges[0].node, TOTAL_FIELD, None)
            if result is None:
                return len(self.edges)
            return result
        return 0


def get_many_field_name(one_field_name):
    return '{}s'.format(one_field_name)


def get_node(model, registry):
    meta_class = type('Meta', (), {'registry': registry, 'model': model, 'interfaces': (Node,)})
    node_class = type(model.__name__,
                      (PeeweeObjectType,),
                      {meta_class.__name__: meta_class})
    connection_meta_class = type('Meta', (), {'node': node_class})
    connection_class = type('{}Connection'.format(model.__name__),
                            (Connection,),
                            {connection_meta_class.__name__: connection_meta_class,
                             'count': Int(),
                             'total': Int(),
                             'resolve_count': PeeweeConnection.resolve_count,
                             'resolve_total': PeeweeConnection.resolve_total
                             })
    field_name = inflection.underscore(model.__name__)
    many_field_name = get_many_field_name(field_name)
    return node_class, {field_name: Node.Field(node_class),
                        many_field_name: PeeweeConnectionField(connection_class)}


def generate_schema(models):
    node_classes = {}
    # models = sorted(models, key=lambda x: x.__name__)
    registry = Registry()
    for model in models:
        node_class, fields = get_node(model, registry)
        node_classes.update(fields)
    query_class = type('Query',
                       (ObjectType,),
                       node_classes)
    executor = NonLeakAsyncioExecutor()
    schema = Schema(query=query_class,
                    auto_camelcase=False)
    return schema, executor


async def _test_select():
    print('\n')
    await manager.connect()
    # schema, executor = generate_schema([Race])
    schema, executor = generate_schema([Race, Monster])
    query = '''
        query {
            monsters (race__power: 0) {
                edges {
                    node {
                        id
                        name
                        race {id
                            power
                        }
                    }
                }
            }
        }
    '''
    pre_result = schema.execute(
        query,
        return_promise=True,
        executor=executor
    )
    if isinstance(pre_result, ExecutionResult):
        result = pre_result
    else:
        result = await pre_result
    # TODO: better way to convert OrderedDict to simple dict
    dumped_data = json.dumps(result.data)
    result.data = json.loads(dumped_data)
    print(result.data)
    print(result.errors)


async def _test_sql():
    print('\n')
    query = (Book
             .select(Book.name)
             .join(Author, peewee.JOIN_LEFT_OUTER)
             .filter(author__name='someone'))
    # author_alias = Author.alias()
    # query = (Book
    #          .select(Book.name)
    #          .join(author_alias, peewee.JOIN_LEFT_OUTER)
    #          .where(author_alias.name == 'someone'))
    print(query.sql()[0])


def test_select():
    loop.run_until_complete(_test_select())


def test_sql():
    loop.run_until_complete(_test_sql())
