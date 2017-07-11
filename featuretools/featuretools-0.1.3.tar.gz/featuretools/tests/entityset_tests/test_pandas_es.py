import pytest
from datetime import datetime
from ..testing_utils import make_ecommerce_entityset, save_to_csv
from featuretools.entityset import EntitySet
from featuretools import variable_types
import pandas as pd
import numpy as np
import copy


@pytest.fixture(scope='module')
def entityset():
    return make_ecommerce_entityset()


@pytest.fixture
def entity(entityset):
    return entityset['log']


class TestQueryFuncs(object):
    def test_query_by_id(self, entityset):
        df = entityset.query_entity_by_values(entity_id='log',
                                          instance_vals=[0])
        assert df['id'].values[0] == 0

    def test_query_by_id_with_sort(self, entityset):
        df = entityset.query_entity_by_values(entity_id='log',
                                          instance_vals=[2, 1, 3],
                                          return_sorted=True)
        assert df['id'].values.tolist() == [2, 1, 3]

    def test_query_by_id_with_time(self, entityset):
        df = entityset.query_entity_by_values(
            entity_id='log', instance_vals=[0, 1, 2, 3, 4],
            time_last=datetime(2011, 4, 9, 10, 30, 2 * 6))

        assert df['id'].get_values().tolist() == [0, 1, 2]

    def test_query_by_variable_with_time(self, entityset):
        df = entityset.query_entity_by_values(
            entity_id='log', instance_vals=[0, 1, 2], variable_id='session_id',
            time_last=datetime(2011, 4, 9, 10, 50, 0))

        true_values = [i * 5 for i in range(5)] + [i * 1 for i in range(4)] + [0]
        assert df['id'].get_values().tolist() == range(10)
        assert df['value'].get_values().tolist() == true_values

    def test_query_by_indexed_variable(self, entityset):
        df = entityset.query_entity_by_values(
            entity_id='log', instance_vals=['taco clock'],
            variable_id='product_id')

        assert df['id'].get_values().tolist() == [15, 16]

    def test_query_by_non_unique_sort_raises(self, entityset):
        with pytest.raises(ValueError):
            entityset.query_entity_by_values(
                entity_id='log', instance_vals=[0, 2, 1],
                variable_id='session_id', return_sorted=True)


class TestVariableHandling(object):
    # TODO: rewrite now that ds and entityset are seperate
    def test_check_variables_and_dataframe(self):
        # matches
        df = pd.DataFrame({'id': [0, 1, 2], 'category': ['a', 'b', 'a']})
        vtypes = {'id': variable_types.Categorical,
                  'category': variable_types.Categorical}
        entityset = EntitySet(id='test')
        entityset.entity_from_dataframe('test_entity', df, id_variable='id',
                                    variable_types=vtypes)
        assert entityset.entity_stores['test_entity'].variable_types['category'] == variable_types.Categorical

    def test_make_id_variable_ordering(self):
        df = pd.DataFrame({'id': [0, 1, 2], 'category': ['a', 'b', 'a']})
        vtypes = {'id': variable_types.Categorical,
                  'category': variable_types.Categorical}

        entityset = EntitySet(id='test')
        entityset.entity_from_dataframe(entity_id='test_entity',
                                    id_variable='id1',
                                    make_id_variable=True,
                                    variable_types=vtypes,
                                    dataframe=df)
        assert entityset.entity_stores['test_entity'].df.columns[0] == 'id1'

    def test_extra_variable_type(self):
        # more variables
        df = pd.DataFrame({'id': [0, 1, 2], 'category': ['a', 'b', 'a']})
        vtypes = {'id': variable_types.Categorical,
                  'category': variable_types.Categorical,
                  'category2': variable_types.Categorical}

        with pytest.raises(LookupError):
            entityset = EntitySet(id='test')
            entityset.entity_from_dataframe(entity_id='test_entity',
                                            id_variable='id',
                                            variable_types=vtypes, dataframe=df)


    def test_unknown_id_variables(self):
        # more variables
        df = pd.DataFrame({'category': ['a', 'b', 'a']})
        vtypes = {'category': variable_types.Categorical}

        entityset = EntitySet(id='test')
        entityset.entity_from_dataframe(entity_id='test_entity',
                                        id_variable='id',
                                        variable_types=vtypes, dataframe=df)
        assert entityset['test_entity'].id_variable == 'id'
        assert entityset['test_entity'].df['id'].tolist() == range(3)

    # def test_bad_index_variables(self):
        # # more variables
        # df = pd.DataFrame({'id': [0, 1, 2], 'category': ['a', 'b', 'a']})
        # vtypes = {'id': variable_types.Categorical,
                  # 'category': variable_types.Categorical}

        # with pytest.raises(LookupError):
            # entityset = EntitySet(id='test')
            # entityset.entity_from_dataframe(entity_id='test_entity',
                                        # id_variable='di',
                                        # variable_types=vtypes, dataframe=df)

        # with pytest.raises(LookupError):
            # entityset = EntitySet(id='test')
            # entityset.entity_from_dataframe(entity_id='test_entity',
                                        # id_variable='id',
                                        # variable_types=vtypes, dataframe=df,
                                        # time_index='time')

    def test_converts_variable_types_on_init(self):
        df = pd.DataFrame({'id': [0, 1, 2],
                           'category': ['a', 'b', 'a'],
                           'category_int': [1, 2, 3],
                           'ints': ['1', '2', '3'],
                           'floats': ['1', '2', '3.0']})
        df["category_int"] = df["category_int"].astype("category")

        vtypes = {'id': variable_types.Categorical,
                  'ints': variable_types.Numeric,
                  'floats': variable_types.Numeric}
        entityset = EntitySet(id='test')
        entityset.entity_from_dataframe(entity_id='test_entity', id_variable='id',
                                    variable_types=vtypes, dataframe=df)

        entity_df = entityset.get_dataframe('test_entity')
        assert entity_df['ints'].dtype.name in variable_types.PandasTypes._pandas_numerics
        assert entity_df['floats'].dtype.name in variable_types.PandasTypes._pandas_numerics

        # this is infer from pandas dtype
        e = entityset["test_entity"]
        assert isinstance(e['category_int'], variable_types.Categorical)

    def test_converts_variable_type_after_init(self):
        df = pd.DataFrame({'id': [0, 1, 2],
                           'category': ['a', 'b', 'a'],
                           'ints': ['1', '2', '1']})

        df["category"] = df["category"].astype("category")

        entityset = EntitySet(id='test')
        entityset.entity_from_dataframe(entity_id='test_entity', id_variable='id',
                                    dataframe=df)
        e = entityset['test_entity']
        df = entityset.get_dataframe('test_entity')

        e.convert_variable_type('ints', variable_types.Numeric)
        assert isinstance(e['ints'], variable_types.Numeric)
        assert df['ints'].dtype.name in variable_types.PandasTypes._pandas_numerics

        e.convert_variable_type('ints', variable_types.Categorical)
        assert isinstance(e['ints'], variable_types.Categorical)

        e.convert_variable_type('ints', variable_types.Ordinal)
        assert isinstance(e['ints'], variable_types.Ordinal)

        e.convert_variable_type('ints', variable_types.Boolean,
                                true_val=1, false_val=2)
        assert isinstance(e['ints'], variable_types.Boolean)
        assert df['ints'].dtype.name == 'bool'


    def test_converts_datetime(self):
        # string converts to datetime correctly
        # This test fails without defining vtypes.  Entityset
        # infers time column should be numeric type
        times = pd.date_range('1/1/2011', periods=3, freq='H')
        time_strs = times.strftime('%Y-%m-%d')
        df = pd.DataFrame({'id': [0, 1, 2], 'time': time_strs})
        vtypes = {'id': variable_types.Categorical,
                  'time': variable_types.Datetime}

        entityset = EntitySet(id='test')
        entityset._import_from_dataframe(entity_id='test_entity', id_variable='id',
                                     time_index="time", variable_types=vtypes,
                                     dataframe=df)
        pd_col = entityset.get_column_data('test_entity', 'time')
        # assert type(es['test_entity']['time']) == variable_types.Datetime
        assert type(pd_col[0]) == pd.Timestamp

    def test_handles_datetime_format(self):
        # check if we load according to the format string
        # pass in an ambigious date
        datetime_format = "%d-%m-%Y"
        actual = pd.Timestamp('Jan 2, 2011')
        time_strs = [actual.strftime(datetime_format)] * 3
        df = pd.DataFrame({'id': [0, 1, 2], 'time_format': time_strs, 'time_no_format': time_strs})
        vtypes = {'id': variable_types.Categorical,
                  'time_format': (variable_types.Datetime, {"format": datetime_format}),
                  'time_no_format': variable_types.Datetime}

        entityset = EntitySet(id='test')
        entityset._import_from_dataframe(entity_id='test_entity', id_variable='id',
                                     variable_types=vtypes, dataframe=df)

        col_format = entityset.get_column_data('test_entity', 'time_format')
        col_no_format = entityset.get_column_data('test_entity', 'time_no_format')
        # without formatting pandas gets it wrong
        assert (col_no_format != actual).all()

        # with formatting we correctly get jan2
        assert (col_format == actual).all()

    def test_handles_datetime_mismatch(self):
        # can't convert arbitrary strings
        df = pd.DataFrame({'id': [0, 1, 2], 'time': ['a', 'b', 'tomorrow']})
        vtypes = {'id': variable_types.Categorical,
                  'time': variable_types.Datetime}

        with pytest.raises(ValueError):
            entityset = EntitySet(id='test')
            entityset.entity_from_dataframe('test_entity', df, 'id',
                                        time_index='time', variable_types=vtypes)

    def test_calculates_statistics_on_init(self):
        df = pd.DataFrame({'id': [0, 1, 2],
                           'time': [datetime(2011, 4, 9, 10, 31, 3 * i)
                                    for i in range(3)],
                           'category': ['a', 'b', 'a'],
                           'number': [4, 5, 6],
                           'boolean': [True, False, True],
                           'boolean_with_nan': [True, False, np.nan]})
        vtypes = {'id': variable_types.Categorical,
                  'time': variable_types.Datetime,
                  'category': variable_types.Categorical,
                  'number': variable_types.Numeric,
                  'boolean': variable_types.Boolean,
                  'boolean_with_nan': variable_types.Boolean}
        entityset = EntitySet(id='test')
        entityset.entity_from_dataframe('stats_test_entity', df, 'id',
                                    variable_types=vtypes)
        e = entityset["stats_test_entity"]
        # numerics don't have nunique or percent_unique defined
        for v in ['time', 'category', 'number']:
            assert e[v].count == 3

        for v in ['time', 'number']:
            with pytest.raises(AttributeError):
                e[v].nunique
            with pytest.raises(AttributeError):
                e[v].percent_unique
        # 'id' column automatically parsed as categorical
        assert e['id'].nunique == 3
        assert e['id'].percent_unique == 1

        # categoricals have nunique and percent_unique defined
        assert e['category'].nunique == 2
        assert e['category'].percent_unique == 2. / 3

        # booleans have count and number of true/false labels defined
        assert e['boolean'].count == 3
        # assert e['boolean'].num_true == 3
        assert e['boolean'].num_true == 2
        assert e['boolean'].num_false == 1

        # boolean with nan have count and number of true/false labels defined
        assert e['boolean_with_nan'].count == 2

        assert e['boolean_with_nan'].num_true == 1
        assert e['boolean_with_nan'].num_false == 1

    def test_column_funcs(self, entityset):
        # Note: to convert the time column directly either the variable type
        # or convert_date_columns must be specifie
        df = pd.DataFrame({'id': [0, 1, 2],
                           'time': [datetime(2011, 4, 9, 10, 31, 3 * i)
                                    for i in range(3)],
                           'category': ['a', 'b', 'a'],
                           'number': [4, 5, 6]})

        vtypes = {'time': variable_types.Datetime}
        entityset.entity_from_dataframe('test_entity', df, id_variable='id',
                                    time_index='time', variable_types=vtypes)
        assert entityset.get_dataframe('test_entity').shape == df.shape
        assert entityset.get_id_variable('test_entity') == 'id'
        assert entityset.get_time_index('test_entity') == 'time'
        assert set(entityset.get_column_names('test_entity')) == set(df.columns)

        assert entityset.get_column_max('test_entity', 'number') == 6
        assert entityset.get_column_min('test_entity', 'number') == 4
        assert entityset.get_column_std('test_entity', 'number') == 1
        assert entityset.get_column_count('test_entity', 'number') == 3
        assert entityset.get_column_mean('test_entity', 'number') == 5
        assert entityset.get_column_nunique('test_entity', 'number') == 3
        assert entityset.get_column_type('test_entity', 'time') == df['time'].dtype
        assert set(entityset.get_column_data('test_entity', 'id')) == set(df['id'])

    def test_time_index_components(self, entityset):
        df = pd.DataFrame({'id': [0, 1],
                           'date': ['4/9/2015', '4/10/2015'],
                           'time': ['8:30', '13:30']})
        filename = save_to_csv('test_entity', df)

        entityset.entity_from_csv('test_entity', filename, id_variable='id',
                              time_index='datetime',
                              time_index_components=['date', 'time'])
        assert entityset.entity_stores['test_entity'].time_index == 'datetime'
        new_df = entityset.get_dataframe('test_entity')
        assert new_df.shape == (2, 2)
        assert len(new_df.columns) == 2
        assert 'id' in new_df.columns
        assert 'datetime' in new_df.columns
        assert new_df['datetime'][0] == datetime(2015, 4, 9, 8, 30, 0)
        assert new_df['datetime'][1] == datetime(2015, 4, 10, 13, 30, 0)

    def test_combine_variables(self, entityset):
        # basic case
        entityset.combine_variables('log', 'comment+product_id',
                                ['comments', 'product_id'])

        assert entityset['log']['comment+product_id'].dtype == 'categorical'
        assert 'comment+product_id' in entityset['log'].df

        # one variable to combine
        entityset.combine_variables('log', 'comment+',
                                ['comments'])

        assert entityset['log']['comment+'].dtype == 'categorical'
        assert 'comment+' in entityset['log'].df

        # drop columns
        entityset.combine_variables('log', 'new_priority_level',
                                ['priority_level'],
                                drop=True)

        assert entityset['log']['new_priority_level'].dtype == 'categorical'
        assert 'new_priority_level' in entityset['log'].df
        assert 'priority_level' not in entityset['log'].df
        assert 'priority_level' not in entityset['log'].variables

        # hashed
        entityset.combine_variables('log', 'hashed_comment_product',
                                ['comments', 'product_id'],
                                hashed=True)

        assert entityset['log']['comment+product_id'].dtype == 'categorical'
        assert entityset['log'].df['hashed_comment_product'].dtype == 'int64'
        assert 'comment+product_id' in entityset['log'].df

    def test_add_parent_time_index(self, entityset):
        entityset = copy.deepcopy(entityset)
        entityset.add_parent_time_index(entity_id='sessions',
                                        parent_entity_id='customers',
                                        parent_time_index_variable=None,
                                        child_time_index_variable='session_date',
                                        include_secondary_time_index=True,
                                        secondary_time_index_variables=['cancel_reason'])
        sessions = entityset['sessions']
        assert sessions.time_index == 'session_date'
        assert sessions.secondary_time_index == {'cancel_date': ['cancel_reason']}
        true_session_dates = ([datetime(2011, 4, 8)] * 3 +
                              [datetime(2011, 4, 9)] * 2 +
                              [datetime(2011, 4, 6)])
        for t, x in zip(true_session_dates, sessions.df['session_date']):
            assert t == x.to_pydatetime()

        true_cancel_dates = ([datetime(2011, 6, 8)] * 3 +
                             [datetime(2011, 10, 9)] * 2 +
                             [datetime(2012, 1, 6)])

        for t, x in zip(true_cancel_dates, sessions.df['cancel_date']):
            assert t == x.to_pydatetime()
        true_cancel_reasons = (['reason_1'] * 3 +
                               ['reason_2'] * 2 +
                               ['reason_1'])

        for t, x in zip(true_cancel_reasons, sessions.df['cancel_reason']):
            assert t == x


class TestRelatedInstances(object):
    def test_related_instances_backward(self, entityset):
        result = entityset._related_instances(
            start_entity_id='regions', final_entity_id='log',
            instance_ids=['United States'])

        col = entityset.get_column_data('log', 'id').values
        assert len(result['id'].values) == len(col)
        assert set(result['id'].values) == set(col)

        result = entityset._related_instances(
            start_entity_id='regions', final_entity_id='log',
            instance_ids=['Mexico'])

        assert len(result['id'].values) == 0

    def test_related_instances_forward(self, entityset):
        result = entityset._related_instances(
            start_entity_id='log', final_entity_id='regions',
            instance_ids=[0, 1])

        assert len(result['id'].values) == 1
        assert result['id'].values[0] == 'United States'

    def test_related_instances_mixed_path(self, entityset):
        result = entityset._related_instances(
            start_entity_id='customers', final_entity_id='products',
            instance_ids=[1])

        prods = entityset.get_column_data('products', 'id').values
        for i in [0, 3]:
            assert prods[i] in result['id'].values
        for i in [1, 2, 4, 5]:
            assert prods[i] not in result['id'].values

    def test_related_instances_all(self, entityset):
        # test querying across the entityset
        result = entityset._related_instances(
            start_entity_id='customers', final_entity_id='products',
            instance_ids=None)

        for p in entityset.get_column_data('products', 'id').values:
            assert p in result['id'].values

    def test_related_instances_link_vars(self, entityset):
        # test adding link variables on the fly during _related_instances
        frame = entityset._related_instances(
            start_entity_id='customers', final_entity_id='log',
            instance_ids=[1], add_link=True)

        # If we need the forward customer relationship to have it
        # then we can add those too
        assert 'sessions.customer_id' in frame.columns
        for val in frame['sessions.customer_id']:
            assert val == 1

    def test_get_pandas_slice(self, entityset):
        filter_eids = ['products', 'regions', 'customers']
        result = entityset.get_pandas_data_slice(filter_entity_ids=filter_eids,
                                             index_eid='customers',
                                             instances=[0])

        # make sure all necessary filter frames are present
        assert set(result.keys()) == set(filter_eids)
        assert set(result['products'].keys()), set(['products', 'log'])
        assert set(result['customers'].keys()) == set(['customers', 'sessions', 'log'])
        assert set(result['regions'].keys()) == set(['regions', 'stores', 'customers', 'sessions', 'log'])

        # make sure different subsets of the log are included in each filtering
        assert set(result['customers']['log']['id'].values) == set(range(10))
        assert set(result['products']['log']['id'].values) == set(range(10) + range(11, 15))
        assert set(result['regions']['log']['id'].values) == set(range(17))

    def test_get_pandas_slice_times(self, entityset):
        # todo these test used to use time first time last. i remvoed and it
        # still passes,but we should double check this okay
        filter_eids = ['products', 'regions', 'customers']
        start = np.datetime64(datetime(2011, 4, 1))
        end = np.datetime64(datetime(2011, 4, 9, 10, 31, 10))
        result = entityset.get_pandas_data_slice(filter_entity_ids=filter_eids,
                                             index_eid='customers',
                                             instances=[0],
                                             time_last=end)

        # make sure no times outside range are included in any frames
        for eid in filter_eids:
            for t in result[eid]['log']['datetime'].values:
                assert t >= start and t < end

            # the instance ids should be the same for all filters
            for i in range(7):
                assert i in result[eid]['log']['id'].values

    def test_get_pandas_slice_times_include(self, entityset):
        # todo these test used to use time first time last. i remvoed and it
        # still passes,but we should double check this okay
        filter_eids = ['products', 'regions', 'customers']
        start = np.datetime64(datetime(2011, 4, 1))
        end = np.datetime64(datetime(2011, 4, 9, 10, 31, 10))
        result = entityset.get_pandas_data_slice(filter_entity_ids=filter_eids,
                                             index_eid='customers',
                                             instances=[0],
                                             time_last=end)

        # make sure no times outside range are included in any frames
        for eid in filter_eids:
            for t in result[eid]['log']['datetime'].values:
                assert t >= start and t <= end

            # the instance ids should be the same for all filters
            for i in range(7):
                assert i in result[eid]['log']['id'].values

    def test_get_pandas_slice_secondary_index(self, entityset):
        filter_eids = ['products', 'regions', 'customers']
        # this date is before the cancel date of customers 1 and 2
        end = np.datetime64(datetime(2011, 10, 1))
        all_instances = [0, 1, 2]
        result = entityset.get_pandas_data_slice(filter_entity_ids=filter_eids,
                                             index_eid='customers',
                                             instances=all_instances,
                                             time_last=end)

        # only customer 0 should have values from these columns
        customers_df = result["customers"]["customers"]
        for col in ["cancel_date", "cancel_reason"]:
            nulls = customers_df.iloc[all_instances][col].isnull() == [False, True, True]
            assert nulls.all(), "Some instance has data it shouldn't for column %s" % col

    def test_add_link_vars(self, entityset):
        eframes = {e_id: entityset.get_dataframe(e_id)
                   for e_id in ["log", "sessions", "customers", "regions"]}

        entityset._add_multigenerational_link_vars(frames=eframes,
                                               start_entity_id='regions',
                                               end_entity_id='log')

        assert 'sessions.customer_id' in eframes['log'].columns
        assert 'sessions.customers.region_id' in eframes['log'].columns


class TestNormalizeEntity(object):
    def test_normalize_entity(self, entityset):
        entityset.normalize_entity('sessions', 'device_types', 'device_type',
                               additional_variables=['device_name'],
                               make_time_index=False)

        assert len(entityset.get_forward_relationships('sessions')) == 2
        assert entityset.get_forward_relationships('sessions')[1].parent_entity.id == 'device_types'
        assert 'device_name' in entityset['device_types'].df.columns
        assert 'device_name' not in entityset['sessions'].df.columns
        assert 'device_type' in entityset['device_types'].df.columns
