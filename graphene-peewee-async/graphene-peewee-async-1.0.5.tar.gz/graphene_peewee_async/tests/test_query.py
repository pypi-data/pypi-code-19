import datetime

import pytest
from pytest import raises

import graphene
# from graphene import Schema, Scalar, ObjectType, GlobalID, Mutation, Field, Boolean, Int, List, Node, Dynamic, String, Argument, ID, NonNull, Connection
from graphene import Node
from graphql.execution.executors.asyncio import AsyncioExecutor

from graphene_peewee_async.types import PeeweeObjectType
from graphene_peewee_async.tests.models import Article, Reporter, manager


def test_should_query_only_fields():
    with raises(Exception):
        class ReporterType(PeeweeObjectType):

            class Meta:
                model = Reporter
                only_fields = ('articles', )

        schema = graphene.Schema(query=ReporterType)
        query = '''
            query ReporterQuery {
              articles
            }
        '''
        result = schema.execute(query)
        assert not result.errors


def test_should_query_well():
    class ReporterType(PeeweeObjectType):

        class Meta:
            model = Reporter
            interfaces = (Node,)

    class Query(graphene.ObjectType):
        reporter = Node.Field(ReporterType)
        # reporter = graphene.Field(ReporterType)
        #
        # def resolve_reporter(self, *args, **kwargs):
        #     return ReporterType(Reporter(first_name='ABA', last_name='X'))

    import asyncio
    from peewee_async import PostgresqlDatabase
    loop = asyncio.get_event_loop()
    reporter = loop.run_until_complete(manager.create(Reporter, first_name='ABA', last_name='X'))
    # reporter = Reporter(first_name='ABA', last_name='X')

    query = '''
        query ReporterQuery {
          reporter (id: ''' + str(reporter.id) + ''') {
            firstName,
            lastName,
            email
          }
        }
    '''
    expected = {
        'reporter': {
            'firstName': 'ABA',
            'lastName': 'X',
            'email': None
        }
    }
    schema = graphene.Schema(query=Query)
    result = schema.execute(query, executor=AsyncioExecutor())
    assert not result.errors
    assert result.data == expected


def test_should_node():
    class ReporterNode(PeeweeObjectType):

        class Meta:
            model = Reporter

        @classmethod
        def get_node(cls, id, context, info):
            return ReporterNode(Reporter(id=2, first_name='Cookie Monster'))

        def resolve_articles(self, *args, **kwargs):
            return [ArticleNode(Article(headline='Hi!'))]

    class ArticleNode(PeeweeObjectType):

        class Meta:
            model = Article

        @classmethod
        def get_node(cls, id, context, info):
            return ArticleNode(Article(id=1, headline='Article node', pub_date=datetime.date(2002, 3, 11)))

    class Query(graphene.ObjectType):
        node = Node.Field()
        reporter = graphene.Field(ReporterNode)
        article = graphene.Field(ArticleNode)

        def resolve_reporter(self, *args, **kwargs):
            return ReporterNode(
                Reporter(id=1, first_name='ABA', last_name='X'))

    query = '''
        query ReporterQuery {
          reporter {
            id,
            firstName,
            articles {
              edges {
                node {
                  headline
                }
              }
            }
            lastName,
            email
          }
          myArticle: node(id:"QXJ0aWNsZU5vZGU6MQ==") {
            id
            ... on ReporterNode {
                firstName
            }
            ... on ArticleNode {
                headline
                pubDate
            }
          }
        }
    '''
    expected = {
        'reporter': {
            'id': 'UmVwb3J0ZXJOb2RlOjE=',
            'firstName': 'ABA',
            'lastName': 'X',
            'email': None,
            'articles': {
                'edges': [{
                  'node': {
                      'headline': 'Hi!'
                  }
                }]
            },
        },
        'myArticle': {
            'id': 'QXJ0aWNsZU5vZGU6MQ==',
            'headline': 'Article node',
            'pubDate': '2002-03-11',
        }
    }
    schema = graphene.Schema(query=Query)
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
