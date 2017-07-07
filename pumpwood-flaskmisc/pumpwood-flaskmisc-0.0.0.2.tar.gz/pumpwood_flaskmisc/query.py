# -*- coding: utf-8 -*-
from sqlalchemy.sql import operators
from sqlalchemy import inspect
from sqlalchemy import desc


class SqlalchemyQueryMisc():
    _underscore_operators = {
        'gt':           operators.gt,
        'lte':          operators.lt,
        'gte':          operators.ge,
        'le':           operators.le,
        'contains':     operators.contains_op,
        'in':           operators.in_op,
        'exact':        operators.eq,
        'iexact':       operators.ilike_op,
        'startswith':   operators.startswith_op,
        'istartswith':  lambda c, x: c.ilike(x.replace('%', '%%') + '%'),
        'iendswith':    lambda c, x: c.ilike('%' + x.replace('%', '%%')),
        'endswith':     operators.endswith_op,
        'isnull':       lambda c, x: x and c != None or c == None,
        'range':        operators.between_op,
        'year':         lambda c, x: extract('year', c) == x,
        'month':        lambda c, x: extract('month', c) == x,
        'day':          lambda c, x: extract('day', c) == x
    }

    @classmethod
    def get_related_models_and_columns(cls, object_model, query_dict, order=False):
        ''' Receive a Django like dictionary and return a dictionary with the related models mapped by query string and the columns and operators to be used.
            Can also be used for order_by arguments where the keys of the query dict especify the joins and the value must be either asc or desc for ascendent
            and decrescent ordenation respectively.
            
            Args:
                object_model (sqlalchemy.DeclarativeModel): Model over which will be performed the queries.
                query_dict (dict): A query dict similar to Django queries, with relations and operator divided
                by "__".
            
            Kwargs:
                No extra arguments

            Returns:
                dict: Key 'models' indicates models to be used in joins and 'columns' returns a list o dictionaries with 
                'column' for model column, 'operation' for operation to be used and 'value' for value in operation.

            Raises:
                Excepiton (It is not permited more tokens after operation underscore (%s). Original query string (%s))
                    If a operation_key is recognized and there is other relations after it. Ex.: attribute__in__database_set
                
                Exception(It is not permited more relations after column underscore (%s). Original query string (%s))
                    If a column field is recognized and new join relations comes after, only operation can go after columns.
                    Ex: attribute__description__database_set

                Exception(It is not possible to continue building query, underscore token ({token}) not found on model columns, relations or operations. Original query string:...)
                    If a token (value separated by "__" is not reconized as neither relations, column and operation)
                    Ex: attribute__description__last_update_at

                Exception('Order value %s not implemented , sup and desc avaiable, for column %s. Original query string %s')
                    If value in query dict when order=True is different from 'asc' and 'desc'
            
            Example:
                >>> filter_query = get_related_models_and_columns(object_model=DataBaseVariable, query_dict={'attribute__description__contains': 'Chubaca' , 'value__gt': 2})
                >>> q = object_model.query.join(*filter_query['models'])
                >>> for fil in filter_query['columns']:
                >>>     q = q.filter( fil['operation'](fil['column'], fil['value']) )
        '''
        #
        join_models           = []
        columns_values_filter = []
        for arg, value in query_dict.items():
            operation_key = None
            column = None
            actual_model = object_model
            q = object_model.query.with_entities(object_model.id)
            #token = arg.split('__')[0]
            for token in arg.split('__'):
                print ('token:', token)
                if operation_key is not None:
                    raise Exception( 'It is not permited more tokens after operation underscore (%s). Original query string (%s)' % (operation_key, arg) )
                #
                mapper = inspect(actual_model)
                relations = dict([ (r.key, r.argument()) for r in list(mapper.relationships) ])
                columns = dict([ (col.key, col) for col in list(mapper.c) ])
                #
                if token in relations.keys():
                    if column is not None:
                        raise Exception( 'It is not permited more relations after column underscore (%s). Original query string (%s)' % (column.key, arg) )
                    q = q.join(token)
                    actual_model = relations[token]
                    join_models.append( actual_model )
                elif token in columns.keys():
                    if column is not None:
                        raise Exception( 'It is not permited more columns after column underscore (%s). Original query string (%s)' % (column.key, arg) )
                    column = columns[token]
                elif token in cls._underscore_operators.keys():
                    operation_key = token
                else:
                    msg = 'It is not possible to continue building query, underscore token ({token}) not found on model columns, relations or operations. Original query string: "{query}".\n'
                    msg = msg + 'Columns: {cols}\n' 
                    msg = msg + 'Relations: {rels}\n'
                    msg = msg + 'Operations: {opers}%s'
                    final_msg = msg.format(token=token
                        , query=arg
                        , cols=str( list(columns.keys()) )
                        , rels=str( list(relations.keys()) )
                        , opers=str(list(cls._underscore_operators.keys())) )
                    raise Exception( final_msg )
            
            if order:
                if value == 'desc':
                    columns_values_filter.append( {'column':column, 'operation':desc} )
                elif value == 'asc':
                    columns_values_filter.append( {'column':column, 'operation':lambda c: c} )
                else:
                    raise Exception( 'Order value %s not implemented , sup and desc avaiable, for column %s. Original query string %s' % (value, column.key, arg) )
            else:
                if operation_key is None:
                    operation_key = 'exact'
                columns_values_filter.append( {'column':column, 'operation':cls._underscore_operators[operation_key], 'value': value} )

        return {'models': join_models, 'columns': columns_values_filter}

    @classmethod
    def sqlalchemy_kward_query(cls, object_model={}, filter_dict={}, exclude_dict={}, order_by=[]):
        ''' Build SQLAlchemy engine string acordind to database parameters.
            
            Args:
                filter_dict (dict): Dictionary to be used in filtering.
                exclude_dict (dict): Dictionary to be used in excluding.
                order_by (list): Dictionary to be used as ordering.
            Kwargs:
                No extra arguments
                
            Raises:
                No raises implemented

            Return:
                sqlalquemy.query: Returns an sqlalchemy with filters applied.
            
            Example:
            >>> query = SqlalchemyQueryMisc.sqlalchemy_kward_query(object_model=DataBaseVariable
            >>>                                                  , filter_dict={'attribute__description__contains': 'Oi' , 'value__gt': 2}
            >>>                                                  , exclude_dict={'modeling_unit__description__exact': 'Mod_3'}
            >>>                                                  , order_by = ['-value', 'attribute__description'])
        '''

        #arg =   'attribute__description__contains'
        #value = 'Oi'
        order_by_dict = {}
        for o in order_by:
            if o[0] == '-':
                order_by_dict[o[1:]] = 'desc'
            else:
                order_by_dict[o] = 'asc'

        filter_query = cls.get_related_models_and_columns(object_model, filter_dict)
        exclude_query = cls.get_related_models_and_columns(object_model, exclude_dict)
        order_query = cls.get_related_models_and_columns(object_model, order_by_dict, order=True)

        unique_models = list(set(filter_query['models'] + exclude_query['models'] + order_query['models']))
        q = object_model.query.join(*unique_models)
        for fil in filter_query['columns']:
            q = q.filter( fil['operation'](fil['column'], fil['value']) )

        for excl in exclude_query['columns']:
            q = q.filter( ~excl['operation'](excl['column'], excl['value']) )

        for ord in order_query['columns']:
            q = q.order_by( ord['operation'](ord['column']) )
        return q
