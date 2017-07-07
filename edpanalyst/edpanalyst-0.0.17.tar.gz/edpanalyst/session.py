from __future__ import print_function
from collections import defaultdict
import re
from six.moves import urllib
from six.moves.urllib.parse import quote
from typing import Any, Dict, List, Sequence, Set, Union  # NOQA
import collections
import six
import sys
import time
import traceback

from pandas import DataFrame  # type: ignore
# This is imported from `future` so its type checking is wonky
import html  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import tqdm  # type: ignore

from .column_association import ColumnAssociation, Stat
from .edpclient import EdpClient, Visibility, CallableEndpoint
from .edpclient import _artifact_id_from_response
from .population_schema import PopulationSchema  # NOQA
from .session_experimental import PopulationModelExperimental

DEFAULT_LIMIT = 10
# Always refetch a population's schema if this duration has elapsed since the
# last fetch, to pick up changes made outside the edpanalyst session.
SCHEMA_INVALIDATION_SECS = 30


class Session(object):

    def __init__(
            self,
            profile=None,  # type: str
            client=None,  # type: EdpClient
            endpoint=None  # type: CallableEndpoint
    ):  # type: (...) -> None
        if profile and client:
            raise ValueError('`profile` will be ignored if `client` is set.')
        self._client = client or EdpClient(profile=profile)
        if endpoint is None:
            url = (self._client.config.edp_url + '/rpc')
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        # Try and list so we raise an error if you're not auth'd
        self.list_populations()

    def list(self, keyword=None):
        models = self._endpoint.population_model.get().json()
        models_df = DataFrame({
            'id': [pm['id'] for pm in models],
            'name': [pm['name'] for pm in models],
            'parent_id': [pm.get('parent_id') for pm in models],
            'creation_time':
            [pd.to_datetime(pm['creation_time'], unit='s') for pm in models],
            'status': [pm['build_progress']['status'] for pm in models],
        }, columns=['id', 'name', 'parent_id', 'creation_time', 'status'])
        return _filtered(models_df, keyword)

    def list_populations(self, keyword=None):
        pops = self._endpoint.population.get().json()
        pops_df = DataFrame({
            'id': [pop['id'] for pop in pops],
            'name': [pop['name'] for pop in pops],
            'creation_time':
            [pd.to_datetime(pop['creation_time'], unit='s') for pop in pops],
            'num_models': [len(pop['models']) for pop in pops]
        }, columns=['id', 'name', 'creation_time', 'num_models'])
        return _filtered(pops_df, keyword)

    def population(self, pid):  # type: (str) -> Population
        """Returns the Population corresponding to `pid`."""
        return Population(pid, self._client)

    def popmod(self, pmid):  # type: (str) -> PopulationModel
        """Returns the PopulationModel corresponding to `pmid`."""
        return PopulationModel(pmid, self._client)

    def upload(
            self,
            data,  # type: DataFrame
            name,  # type: str
            schema=None,  # type: PopulationSchema
            hints=None,  # type: Dict[str, Any]
            autobuild=True,  # type: bool
    ):  # type: (...) -> Population
        """Create a population in EDP from uploaded data.

        Args:
            data: The data to create a population from.
            name: The name of the newly created population.
            schema: The schema describing the data. If not provided the server
                will attempt to guess one for you.
            hints: Provide hints to the guesser if not providing a schema.
            autobuild: If true, a number of model builds will be started
                automatically after creating the population
        """
        # TODO(asilvers): We require you to upload strings for categoricals so
        # that there's no ambiguity as to the representation as there could be
        # if they were floats. But this auto-conversion doesn't really solve
        # that issue, it just hides it from you. These issues go away when we
        # upload raw data and do assembly server-side, since presumably at that
        # point you're uploading strings anyway (e.g. CSV from a file).
        # TODO(asilvers): Also consider not doing this for numeric columns.
        if schema and hints:
            raise ValueError('At most one of `schema` and `hints` '
                             'can be provided.')
        stringed_df = data.copy()
        for col in data.columns:
            if not _is_sequence_list(stringed_df[col]):
                stringed_df[col] = stringed_df[col].astype(six.text_type)
        nulled_df = stringed_df.where(pd.notnull(data), None)
        json_data = nulled_df.to_dict(orient='list')
        pid = self._client.upload_population(data=json_data, schema=schema,
                                             hints=hints, name=name)
        pop = Population(pid=pid, client=self._client)
        if autobuild:
            pop.build_model(name=name + ' warmup 1m', iterations=500,
                            ensemble_size=16, max_seconds=60)
            pop.build_model(name=name + ' prelim 5m', iterations=500,
                            ensemble_size=32, max_seconds=300)
        return pop

    def send_feedback(self, message, send_traceback=True):
        # type: (str, bool) -> None
        """Report feedback to Empirical's support team.

        Sends `message` along with the most recent exception (unless
        `send_traceback` is False).
        """
        req = {'message': message}
        if send_traceback and hasattr(sys, 'last_traceback'):
            req['traceback'] = ''.join(traceback.format_tb(sys.last_traceback))
        self._endpoint.feedback.post(json=req)


def _filtered(items, keyword):
    """Filter a data frame of population / population models."""
    if not keyword:
        return items

    idx = []
    for r in range(items.shape[0]):
        if (items.name[r].lower().find(keyword.lower()) != -1):
            idx.append(r)
    return items.loc[idx]


class Population(object):

    def __init__(
            self,
            pid,  # type: str
            client,  # type: EdpClient
            endpoint=None,  # type: CallableEndpoint
            time_fn=time.time):  # type: (...) -> None
        self._pid = pid
        self._client = client
        if endpoint is None:
            url = (self._client.config.edp_url +
                   '/rpc/population/%s' % quote(self._pid))
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        self.name  # Cause an error if this population doesn't exist
        self._schema = None  # type: PopulationSchema
        self._schema_fetch_time = None  # type: float
        self._time_fn = time_fn

    def __str__(self):  # type: () -> str
        return ('Population(id=%r, name=%r)' % (self._pid, self.name))

    def __repr__(self):  # type: () -> str
        return str(self)

    def _repr_html_(self):  # type: () -> str
        return (('<span>%s</span><br>' %
                 (html.escape(self.name),)) + '<span>Models:</span>'
                '<ul>' + ''.join([('<li>' + m._repr_html_() + '</li>')
                                  for m in self.models]) + '</ul>')

    def rename(self, name):  # type: (str) -> None
        """Rename this population."""
        self._endpoint.rename.post(json=name)

    def _metadata(self):  # type: () -> Dict[str, Any]
        # TODO(asilvers): Half of this metadata (e.g. creation_time) doesn't
        # ever change, so making a call for each access is unnecessary and
        # wasteful. But if it's causing problems we probably have bigger
        # problems. Think about this at some point.
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pid

    @property
    def name(self):  # type: () -> str
        return self._metadata()['name']

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def models(self):  # type: () -> List[PopulationModel]
        return [
            PopulationModel(model['id'], self._client)
            for model in self._metadata()['models']
        ]

    @property
    def schema(self):  # type: () -> PopulationSchema
        if self._schema is None or self._time_fn(
        ) - self._schema_fetch_time > SCHEMA_INVALIDATION_SECS:
            resp = self._endpoint.schema.get()
            self._schema = PopulationSchema.from_json(resp.json())
            self._schema_fetch_time = self._time_fn()

        return self._schema

    def visibility(self):  # type: () -> Visibility
        """Fetches visibility for this population."""
        resp = self._endpoint.visibility.get()
        return Visibility.from_json(resp.json())

    def delete(self):  # type: () -> None
        """Delete this population.

        This Population object will become invalid after deletion.
        """
        self._endpoint.delete()

    def make_public(self):  # type: () -> Visibility
        """Make this population public.

        Returns the ACL for the population after the modification.
        """
        req = {'public': True}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader(self, reader,
                   send_email=False):  # type: (str, bool) -> Visibility
        """Add `reader` to this population's reader list.

        Args:
            reader: The email of the user who should have read access to the
                population.
            send_email: Whether to send an email to the new reader.

        Returns the ACL for this model after the modification.
        """
        req = {'readers': [reader], 'send_email': send_email}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader_domain(self, domain):  # type): (str) -> Visibility
        """Give all users on `domain` read access to this population.

        Args:
            domain: The domain to grant read access to. Must begin with '@'.

        Returns the ACL for this model after the modification.
        """
        req = {'reader_domain': domain}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def remove_reader(self, reader):  # type: (str) -> Visibility
        """Remove `reader` from this population's reader list.

        Args:
            reader: The email of the user whose read access to remove.

        Returns the ACL for this model after the modification. If the given
        user does not already have read access, this method will return
        successfully but have no effect.
        """
        req = {'remove_readers': [reader]}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def remove_reader_domain(self, domain):  # type: (str) -> Visibility
        """Remove domain-wide read access from `domain`.

        Users in `domain` whose emails were individually added will not have
        their read access removed.

        Args:
            reader: The domain to remove read access from. Must begin with '@'.

        Returns the ACL for this model after the modification. If the given
        domain does not already have read access, this method will return
        successfully but have no effect.
        """
        req = {'remove_reader_domain': domain}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def _find_latest(self, models):
        """Return the latest built model, or None if none exist."""
        if len(models) == 0:
            # If no models are being built then it's probably silly to wait
            raise ValueError('This population has no models')

        built = [m for m in models if m['build_progress']['status'] == 'built']
        if len(built) > 0:
            # TODO(asilvers): This is actually looking at models' creation
            # times, not how recently they finished building. That's probably
            # not quite right.
            latest = max(built, key=lambda m: m['creation_time'])
            return PopulationModel(latest['id'], self._client)
        else:
            return None

    # Wait 70 seconds by default. 60 seconds for the 1 minute model build, and
    # an extra 10 for post-build finish-up stuff.
    def latest(self, wait=70):  # type: (int) -> PopulationModel
        """Returns this population's most recently built model.

        This will wait up to `wait` seconds for a model to finish building.

        Raises `ValueError` if `wait` is 0 (or falsey) and this model has no
        already-built models, or if `wait` seconds have elapsed and no models
        have finished.
        """
        timeout_time = time.time() + wait
        with tqdm.tqdm(unit='', leave=False) as progress_bar:
            current_pb_state = 0
            while True:
                models = self._metadata()['models']
                latest = self._find_latest(models)
                if latest:
                    return latest
                if time.time() > timeout_time:
                    break

                # TODO(asilvers): Just bail if we think we're not gonna make
                # it?
                build_progress = _min_seconds_remaining(models)
                if build_progress:
                    progress_bar.total = build_progress.total
                    # `tqdm.update` adds its argument to progress, not sets it,
                    # and doesn't provide a way to do so. Which means we need
                    # to do this silly runaround. Why not pick a different
                    # progress bar then? Because asilvers@ already wasted
                    # enough time on this.
                    to_add = build_progress.elapsed - current_pb_state
                    progress_bar.update(to_add)
                    current_pb_state = current_pb_state + to_add
                # TODO(asilvers): Am I going to regret the number of
                # metadata REST calls this puts out?
                time.sleep(1)
        # Don't mention timeouts if we didn't wait
        if not wait:
            raise ValueError('This population has no built models')
        raise ValueError('Timed out waiting for models to finish building')

    def build_model(
            self,
            name=None,  # type: str
            ensemble_size=16,  # type: int
            iterations=100,  # type: int
            max_seconds=None,  # type: int
            builder='crosscat',  # type: str
            random_seed=None,  # type: int
            clusters=None,  # type: int
    ):  # type: (...) -> PopulationModel
        """Build a model from this population.

        Args:
            name: The name of the newly built model
            ensemble_size: How many sub-models to build in the model ensemble.
            iterations: The number of iterations to build for
            max_seconds: If set, the model build will attempt to take no longer
                than this many seconds to build. This is not a hard limit.
            builder: Which builder to use. Currently only 'crosscat'
            random_seed: A random seed to make the build deterministic.
            clusters: Number of clusters when `builder` is "cv" (experimental).
        """
        name = name or self.name
        req = {
            'name': name,
            'build_def': {
                'num_models': ensemble_size,
                'builder': builder,
                'duration': {
                    'iterations': iterations
                }
            }
        }  # type: Dict[str, Any]
        if random_seed is not None:
            req['build_def']['random_seed'] = random_seed
        if max_seconds is not None:
            req['build_def']['duration']['max_seconds'] = max_seconds
        if clusters is not None:
            req['build_def']['clusters'] = clusters
        resp = self._endpoint.build.post(json=req)
        pmid = _artifact_id_from_response(resp)
        return PopulationModel(pmid, self._client)

    def set_column_display_name(self, column,
                                display_name):  # type(str, str) -> None
        """Sets the display name for a column.

        Passing None or an empty string removes a previously set display name.
        """
        display_name = display_name or ''
        # URL path components need to be escaped twice in order for embedded
        # slashes to be handled correctly.
        endpoint = CallableEndpoint('%s/column/%s/display_name' %
                                    (self._endpoint.url,
                                     _double_encode(column)),
                                    self._client._session)
        endpoint.post(json=display_name)
        # Clear cached schema so we pick up the new value.
        self._schema = None

    def set_column_description(self, column,
                               description):  # type(str, str) -> None
        """Sets the description for a column.

        Passing None or an empty string removes a previously set description.
        """
        description = description or ''
        endpoint = CallableEndpoint('%s/column/%s/description' %
                                    (self._endpoint.url,
                                     _double_encode(column)),
                                    self._client._session)
        endpoint.post(json=description)
        self._schema = None

    def set_categorical_display_value(
            self, column, categorical_value,
            display_value):  # type(str, str, str) -> None
        """Sets the display value for a value of a categorical column.

        Passing None or an empty string removes a previously set display value.
        """
        display_value = display_value or ''
        endpoint = CallableEndpoint(
            '%s/column/%s/values/%s/display_value' %
            (self._endpoint.url, _double_encode(column),
             _double_encode(categorical_value)), self._client._session)
        endpoint.post(json=display_value)
        self._schema = None

    def set_categorical_value_description(
            self, column, categorical_value,
            description):  # type(str, str, str) -> None
        """Sets the description for a value of a categorical column.

        Passing None or an empty string removes a previously set description.
        """
        description = description or ''
        endpoint = CallableEndpoint(
            '%s/column/%s/values/%s/description' %
            (self._endpoint.url, _double_encode(column),
             _double_encode(categorical_value)), self._client._session)
        endpoint.post(json=description)
        self._schema = None

    def column_groups(self):  # type () -> Dict[str, Set[str]]
        """Returns a dict describing the population's column groups.

        Column groups are defined by including an identifier starting with a
        '#' character in the descriptions of all columns in the group. The
        keys of the returned dict are the group identifiers and the values
        are sets of column names in that group.
        """
        s = self.schema
        groups = defaultdict(set)  # type: Dict[str, Set[str]]
        group_id_regex = re.compile(r'#\w+')
        for col in s.columns():
            desc = s[col].description
            if desc:
                for group_id in group_id_regex.findall(desc):
                    groups[group_id].add(col)
        return groups


class PopulationModel(object):

    def __init__(
            self,
            pmid,  # type: str
            client,  # type: EdpClient
            endpoint=None  # type: CallableEndpoint
    ):  # type: (...) -> None
        self._pmid = pmid
        self._client = client
        if endpoint is None:
            url = (self._client.config.edp_url +
                   '/rpc/population_model/%s' % quote(self._pmid))
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint

        self.name  # Cause an error if this population model doesn't exist
        self._parent = None  # type: Population

        # We frequently need a list of all the rowids. Save one.
        self._cached_rowids = None  # type: List[int]

        self._return_identifying_columns = True

        self.experimental = PopulationModelExperimental(self)
        """Access to experimental methods on this PopulationModel."""

    @property
    def schema(self):  # type: () -> PopulationSchema
        return self.parent.schema

    def _metadata(self):  # type: () -> Dict[str, Any]
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pmid

    @property
    def parent(self):  # type: () -> Population
        if self._parent is None:
            parent_id = self._metadata().get('parent_id')
            self._parent = Population(parent_id, self._client)
        return self._parent

    @property
    def name(self):  # type: () -> str
        return self._metadata()['name']

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def build_progress(self):  # type: () -> Dict[str, Any]
        return self._metadata()['build_progress']

    def _modeled_columns(self):
        return [
            cname for cname in self.schema.columns()
            if self.schema[cname].stat_type != 'void'
        ]

    def __str__(self):  # type: () -> str
        return ('PopulationModel(id=%r, name=%r, %d columns)' %
                (self._pmid, self.name, len(self.schema.columns())))

    def __repr__(self):  # type: () -> str
        return str(self)

    def _repr_html_(self):  # type: () -> str
        url = '%s/explorer/population_model/%s' % (
            self._client.config.edp_url, urllib.parse.quote(self._pmid))
        text = html.escape(self.name)
        # TODO(asilvers): This isn't ideal, because unbuilt models will just
        # 400 when you open explorer.
        if self.build_progress['status'] != 'built':
            text += ' (unbuilt)'
        build_duration = self._metadata().get('build_duration')
        if build_duration is not None:
            minutes = int(self._metadata()['build_duration'] / 60)
            text += ' (%d %s)' % (minutes, ('minute'
                                            if minutes == 1 else 'minutes'))
        return ('<a href="%s" target="_blank">Explore %s</a>' %
                (html.escape(url), text))

    def delete(self):  # type: () -> None
        """Delete this population model.

        This PopulationModel object will become invalid after deletion.
        """
        self._endpoint.delete()

    def describe_columns(self):  # type: () -> DataFrame
        """Returns a data frame describing the columns in this population model.
        """
        return DataFrame([(self.schema[c].name, self.schema[c].stat_type,
                           _abbreviate_values(self.schema[c].values))
                          for c in self.schema.columns()],
                         columns=['name', 'stat_type', 'values'])

    def _columns_from_arg(self, columns):
        """Given a columns argument, return a list of column names. Handles
        None and non-list sequences, and expands column group identifiers."""
        self._check_column_list(columns)
        if columns is None:
            return list(self._modeled_columns())
        # Check if there are possible column group identifiers.
        if not any(c.startswith('#') for c in columns):
            return list(columns)
        # Expand column group identifiers to the corresponding column names.
        column_groups = self.parent.column_groups()
        all_columns = self.schema.columns()
        expanded_columns = []  # type: List[str]
        for c in columns:
            if c in column_groups:
                if c in all_columns:
                    print('"%s" is both a column name and a column group '
                          'identifier. Using the single column' % (c,),
                          file=sys.stderr)
                    expanded_columns.append(c)
                else:
                    expanded_columns.extend(column_groups[c])
            else:
                expanded_columns.append(c)
        return list(expanded_columns)

    def _check_column_list(self, columns):
        """Make sure someone didn't accidentally pass a string as a list."""
        if isinstance(columns, six.string_types):
            raise ValueError('`columns` takes a sequence, not a single string')
        return columns

    def _all_rowids(self):  # type: () -> List[int]
        if self._cached_rowids is None:
            self._cached_rowids = self.select(targets=[]).index
        return self._cached_rowids

    def _rowids_from_arg(self, rowids):
        # type: (List[int]) -> Union[str, List[int]]
        """Return `rowids` if non-None or the 'all' selector if None."""
        if rowids is None or rowids == 'all':
            return 'all'
        else:
            return _ensure_rowids_are_real_ints(rowids)

    def _id_cols(self):
        """Returns identifying columns if we have them and we want to be using
        them, or an empty list otherwise.
        """
        if self._return_identifying_columns:
            return self.schema.identifying_columns or []
        else:
            return []

    def return_identifying_columns(self, return_them=True):
        # type: (bool) -> None
        """Set whether methods add identifying_columns to data frames."""
        self._return_identifying_columns = return_them

    def select(
            self,
            targets=None,  # type: List[str]
            where=None,  # type: Dict[str, Union[str, int, float]]
            rowids=None,  # type: List[int]
            limit=None,  # type: int
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Return a subset of a population's data.

        The response DataFrame's index corresponds to the population's rowids.

        Args:
            targets: The list of columns to select. If not specified, returns
                all columns.
            where: Limit the results to those rows where the values of the
                specified columns match the values in `where`. If not
                specified, `select` returns all rows.
            rowids: The rowids to restrict results to. If not specified
                returns all rows.
            limit: Return at most `limit` rows. If this would otherwise return
                more than that, the rows to return are chosen randomly.
            random_seed: Optional random seed between 0 and 2**32-1; only
                meaningful if `limit` is specified.
        """
        targets = self._columns_from_arg(targets)
        req = {'target': targets}  # type: Dict[str, Any]
        if rowids is not None:
            req['rowids'] = self._rowids_from_arg(rowids)
        if where:
            req['where'] = where
        if limit is not None:
            req['limit'] = int(limit)
        if random_seed is not None:
            req['random_seed'] = random_seed
        resp = self._endpoint.select.post(json=req)
        respjson = resp.json()
        return DataFrame(respjson['columns'], index=respjson['rowids'])

    def simulate(
            self,
            targets=None,  # type: List[str]
            rowid=None,  # type: int
            given=None,  # type: Dict[str, Union[str, float, List[float]]]
            n=DEFAULT_LIMIT,  # type: int
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Draw a sample of size `n` from the population model.

        Each returned row is a random draw from the posterior predictive. To
        the extent that there is model uncertainty, drawn rows come from
        independent draws from the model's posterior.

        Args:
            targets: The list of columns to simulate.
            rowid: If present, the simulation will be conditioned on all values
                present in that row except for columns specified in `targets`.
                Givens specified in `given` will also take precedence.
            given: Values to condition the simulation on. If a column is in
                both `target` and a key in `given` that column will be the
                given value in every resulting row.
            n: The number of results to simulate.
            random_seed: optional random seed between 0 and 2**32-1
        """
        targets = self._columns_from_arg(targets)
        given = given or {}
        effective_givens = {}
        # TODO(asilvers): I am uncomfortable with this magic
        if rowid:
            df = self.select(rowids=[rowid])
            # Each column is only length 1 since we only requested a single row
            # If you specified a rowid and that row has values for the target
            # columns, you probably don't mean to condition on those targets
            # and get boring deterministic results back. So we do the right
            # thing and drop them from the givens. This kind of magic is
            # coincidentally why I'm wary of handling rowids server-side.
            givens_from_row = {
                col: df[col][rowid]
                for col in df
                if pd.notnull(df[col][rowid]) and col not in targets
            }
            effective_givens.update(givens_from_row)
        # Have existing givens take precedence
        effective_givens.update(given)

        req = {'target': targets, 'n': n}
        if effective_givens:
            req['given'] = effective_givens
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.simulate_row.post(json=req)
        respjson = resp.json()
        assert 'rowids' not in respjson
        return DataFrame(respjson['columns'])

    def mutual_information(
            self,
            columns=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            random_seed=None,  # type: int
    ):
        # type: (...) -> DataFrame
        """Returns the mutual information between a collection of columns.

        See `column_association` for documentation about column association
        calls in general.
        """
        return self.column_association(
            columns, Stat.MI, given_columns=given_columns,
            given_values=given_values, random_seed=random_seed)

    def column_relevance(
            self,
            columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            distribution=0.1,  # type: float
            given_columns=None,  # type: List[str]
            random_seed=None,  # type: int
    ):
        # type: (...) -> DataFrame
        """Return the MI-based dep prob of a collection of columns.

        See `column_association` for documentation about column association
        calls in general.

        This MI-based dep prob is the probability that the MI is greater than
        `distribution`.
        """
        mi_cdf = self.column_association(
            columns, Stat.MI, given_columns=given_columns,
            given_values=given_values, distribution=distribution,
            random_seed=random_seed)
        # This returns a CDF-like probability of MI being less than
        # `distribution`. But we want the probability that it's greater, so
        # reverse it.
        mi_cdf = 1 - mi_cdf
        return mi_cdf

    def classic_dep_prob(
            self,
            columns=None  # type: List[str]
    ):  # type: (...) -> DataFrame
        """Returns the "classic dep prob" of a collection of columns.

        See `column_association` for documentation about column association
        calls in general.
        """
        # Conditional classic dep prob doesn't make sense.
        return self.column_association(columns,
                                       statistic=Stat.CLASSIC_DEP_PROB)

    def correlation_squared(
            self,
            columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Return a DataFrame containing R-squared.

        See `column_association` for documentation about column association
        calls in general.
        """
        return self.column_association(columns, Stat.R2,
                                       given_values=given_values,
                                       random_seed=random_seed)

    def column_association(
            self,
            columns,  # type: List[str]
            statistic,  # type: Stat
            given_columns=None,  # type: List[str]
            given_values=None,  # type: Dict[str, Any]
            distribution=None,  # type: float
            random_seed=None,  # type: int
    ):  # type: (...) -> pd.Series
        """Return a measure of the column association for a list of columns.

        Returns a Series of the column association between all columns or
        the provided `columns`. The series has a multi-index of (X, Y) which
        are the column names for that row, and the value of the series at that
        index is the value of the chosen column association measure between
        those columns.

        Args:
            columns: The columns to find the column association of. If None,
                return all non-given columns.
            statistic: Which column association statistic to use.
            given_columns: The columns to condition on. That is, compute
                `col_assoc(X, Y | G_1, G_2, ..., G_n)` where
                `given_columns = {G_1, G_2, ..., G_n}`.
            given_values: The column values to condition on. That is, compute
                `col_assoc(X, Y | G_1 = g_1, G_2 = g_2, ..., G_n = g_n)` where
                `given_values = {G_1: g_1, G_2: g_2, ..., G_n: g_n}`.
            distribution: If None, the returned values will be the mean of the
                column association across models. If not None, the return
                values will be the probability that the column association is
                less than `distribution`.
            random_seed: An optional seed to make the results deterministic.
        """
        cols_used_in_givens = (set(given_columns or []) |
                               set(given_values or []))
        # Use `columns` if provided, otherwise use all non-given columns
        if columns is not None:
            columns = self._columns_from_arg(columns)
        else:
            columns = [
                c for c in self._modeled_columns()
                if c not in cols_used_in_givens
            ]

        overlapping_cols = set(columns).intersection(given_columns or [])
        if overlapping_cols:
            raise ValueError('%s in both `columns` and `given_columns`' %
                             (overlapping_cols,))
        overlapping_cols = set(columns).intersection(given_values or [])
        if overlapping_cols:
            raise ValueError('%s in both `columns` and `given_values`' %
                             (overlapping_cols,))

        req = {
            'statistic': statistic.api_value,
            'target': columns
        }  # type: Dict[str, Any]

        if given_columns:
            req['given_columns'] = given_columns
        if given_values:
            req['given'] = given_values
        if distribution is not None:
            req['distribution'] = distribution
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.column_association.post(json=req)
        return ColumnAssociation(resp.json()).as_series()

    def relevant_columns(
            self,
            target_column,  # type: str
            num_cols=10,  # type: int
            statistic=Stat.CLASSIC_DEP_PROB,  # type: Stat
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Return the `num_cols` columns with the highest column association
        (based on the chosen statistic) relative to `target_column`.
        """
        cols = self._modeled_columns()
        ca = self.column_association(cols, statistic=statistic,
                                     random_seed=random_seed)
        col_dependence = [(c, ca.loc[target_column, c]) for c in cols]
        col_dependence.sort(key=lambda v: -v[1])  # descending by dependence
        return DataFrame(col_dependence[0:num_cols],
                         columns=['column', 'depprob'])

    def joint_probability(
            self,
            targets,  # type: Dict[str, List[Any]]
            given=None,  # type: Dict[str, Any]
            givens=None,  # type: Dict[str, List[Any]]
            probability_column='p'  # type: str
    ):  # type: (...) -> DataFrame
        """The joint probability of a list of hypothetical rows.

        Returns a data frame with a column for each key in `targets` containing
        the target values, plus a column, `probability_column`.
        `probability_column`'s value represents the (possibly conditional)
        joint probability of the values in that row.

        If `given` is specified it is a single row of values on which to
        condition each row's probability.

        If `givens` is specified it is a table of values such that the results
        for `targets[k]` is conditioned on the values of `givens[k]`. Its
        columns must be the same length as the columns of `targets`.

        Passing `given` is equivalent to passing a table containing `given`
        for every row as `givens`.
        """
        if given is not None and givens is not None:
            raise ValueError(
                'At most one of `given` or `givens` can be specified')
        overlapping_cols = set(targets).intersection(given or [])
        if overlapping_cols:
            raise ValueError('%s in both `targets` and `given`' %
                             (overlapping_cols,))
        overlapping_cols = set(targets).intersection(givens or [])
        if overlapping_cols:
            raise ValueError('%s in both `targets` and `givens`' %
                             (overlapping_cols,))
        req = {'targets': targets}
        if given:
            req['given'] = given
        if givens:
            req['givens'] = givens
        resp = self._endpoint.logpdf_rows.post(json=req)
        lps = [lp if lp is not None else float('nan') for lp in resp.json()]
        resp_vals = targets.copy()
        resp_vals[probability_column] = np.exp(lps)
        return DataFrame(resp_vals)

    def _internal_probability(
            self,
            targets,  # type: List[str]
            given_columns,  # type: List[str]
            rowids  # type: Union[str, List[int]]
    ):  # (...) -> type: List[float]
        req = {'targets': targets, 'givens': given_columns, 'rowids': rowids}
        resp = self._endpoint.logpdf_observed.post(json=req)
        lps = [lp if lp is not None else float('nan') for lp in resp.json()]
        return np.exp(lps)

    def row_probability(
            self,
            targets=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            probability_column='p',  # type: str
            omit_target_columns=False  # type: bool
    ):  # type: (...) -> DataFrame
        """Returns the probabilities of a collection of rows from the data.

        TODO(asilvers): Somehow emphasize that this is the joint probability of
        each row individually, vectorized, not the probability of all of them
        occurring together.

        Returns a data frame containing the data in columns and rowids and
        a single additional column, `probability_column`, containing the joint
        probability of the values in that row, conditional on the values in the
        in the given columns. The given columns are `given_columns` if
        provided, or all modeled columns not in `targets` otherwise. It is an
        error to pass a column in both `targets` and `given_columns`.

        If you want one probability column per column, you want
        `element_probability`.

        Args:
            targets: The list of columns to find the probability of.
            given_columns: The list of columns to condition the probability on.
                Defaults to all non-target columns.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            probability_column: The name of the column in which to return the
                probabilities.
            omit_target_columns: If True, don't return the data from the
                target columns. This is useful when calling this method from a
                tight loop since it should be slightly faster.
        """
        targets = self._columns_from_arg(targets)
        if probability_column in targets:
            raise ValueError(
                "Probability column, %r, is already a column in targets." %
                (probability_column,))
        # Use the given columns if provided, otherwise use all non-target
        # columns
        given_cols = (self._columns_from_arg(given_columns)
                      if given_columns is not None else
                      [c for c in self._modeled_columns() if c not in targets])
        overlapping_cols = set(targets).intersection(given_cols)
        if overlapping_cols:
            raise ValueError('%s in both `targets` and `given_columns`' %
                             (overlapping_cols,))

        row_selector = self._rowids_from_arg(rowids)

        p = self._internal_probability(targets, given_cols, row_selector)

        # logpdf_observed doesn't return rowids, so we're sort of taking it on
        # faith that they come back in the same order as the select query's
        # rowids. There's a test for this, though.
        idx = (row_selector if row_selector != 'all' else self._cached_rowids)
        probs_df = DataFrame({probability_column: p}, index=idx)
        res = probs_df
        if not omit_target_columns:
            select_df = self.select(targets=targets, rowids=rowids)
            column_order = targets + [probability_column]
            res = pd.concat([probs_df, select_df], axis=1)[column_order]
        return self.add_data_columns(res, select)

    def element_probability(
            self,
            targets=None,  # type: List[str]
            given_columns=None,  # type: List[str]
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            probability_suffix='_p'  # type: str
    ):  # type: (...) -> DataFrame
        """The probability of the individual values in a list of observed rows.

        Returns a data frame containing marginal probabilities for the values
        in the requested columns and rowids, conditional on the values in the
        given columns. The given columns are `given_columns` if provided, or
        all modeled columns not in `targets` otherwise, minus the single target
        column. It is _not_ an error to pass a column in both `targets` and
        `given_columns`.

        The data frame will have 2*len(columns) columns, one for each column,
        and one for each column's values' probabilities.  These are the
        marginal conditional probabilities of each cell's value, not a joint
        conditional probability across all columns for a given row.

        If you want a single probability per row, you want `row_probability`.

        Args:
            targets: The list of columns to find the probability of.
            given_columns: The list of columns to condition the probability on.
                Defaults to all non-target columns.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            probability_suffix: The string to append to each column name to
                generate its corresponding probability column's name.
        """
        targets = self._columns_from_arg(targets)
        given_columns = self._columns_from_arg(given_columns)
        if isinstance(rowids, six.string_types):
            raise ValueError('`rowids` takes a sequence, not a single string')
        for col in targets:
            if (col + probability_suffix) in targets:
                raise ValueError(
                    "Column %r's probability column would clash with %r" %
                    (col, col + probability_suffix))
        df = self.select(targets=targets, rowids=rowids)
        # Pull the rowids back out of the select results in case they were None
        rowids = df.index.tolist()

        for col in targets:
            given_cols = sorted([c for c in given_columns if c != col])
            p = self._internal_probability(
                targets=[col], given_columns=given_cols, rowids=rowids)
            df[col + probability_suffix] = p

        # Re-order the columns so the confidence columns are next to the data.
        column_order = []  # type: List[str]
        for c in targets:
            column_order.extend((c, c + probability_suffix))
        res = df[column_order]
        return self.add_data_columns(res, select)

    # TODO(asilvers): I don't think this really belongs on PopulationModel.
    # Maybe we return a DataFrame extended with this method?
    def add_data_columns(
            self,
            df,  # type: DataFrame
            columns=None,  # type: List[str]
            return_identifying_columns=None  # type: bool
    ):  # type: (...) -> DataFrame
        """Return a DataFrame with additional columns from the population.

        Args:
            df: The data frame to add columns to.
            columns: The columns to fetch.
            return_identifying_columns: An optional override to the
                return_identifying_columns optional on this instance.
        """
        self._check_column_list(columns)
        return_id_cols = (return_identifying_columns
                          if return_identifying_columns is not None else
                          self._return_identifying_columns)
        id_cols = self.schema.identifying_columns if return_id_cols else []
        cols_to_fetch = id_cols + (columns or [])
        # It's reasonable to call this and not have any columns to fetch.
        if not cols_to_fetch:
            return df

        # Filter out columns we already have
        cols_to_fetch = [col for col in cols_to_fetch if col not in df.columns]
        rowids = df.index.tolist()
        select_results = self.select(targets=cols_to_fetch, rowids=rowids)
        # Put our columns first, except don't re-order id columns that we
        # didn't re-fetch.
        column_order = cols_to_fetch + list(df.columns)
        return df.join(select_results)[column_order]

    def infer(
            self,
            targets=None,  # type: List[str]
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            infer_present=False,  # type: bool
            confidence_suffix='_conf',  # type: str
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Infer values from this population model.

        Infer values for the columns in `targets` for `rowids`, given the other
        values in that row. If `infer_present` is False, this will only infer
        values for cells which are missing in the data. If `infer_present` is
        True, this will act as though each column in `targets` is missing
        across all rows and so infer a value for every row.

        Args:
            targets: The list of columns to infer.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            infer_present: True to infer results for values which are present
                in the underlying data. False will cause them to be returned as
                NA.
            confidence_suffix: The string to append to each column name to
                generate its corresponding confidence column's name.
            random_seed: optional random seed between 0 and 2**32-1

        Returns:
            A data frame containing 2*len(targets) columns, one for each column
            and one for each column's confidence. If a cell is present in the
            data and `infer_present` is false, both the cell and its
            corresponding confidence cell will contain NA.
        """
        targets = self._columns_from_arg(targets)

        for col in targets:
            if (col + confidence_suffix) in targets:
                raise ValueError(
                    "Column %r's confidence column would clash with %r" %
                    (col, col + confidence_suffix))

        req = {
            'target': targets,
            'rowids': self._rowids_from_arg(rowids),
            'infer_present': infer_present
        }  # type: Dict[str, Any]
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.infer_observed.post(json=req)
        res = self._infer_response(resp.json(), targets, confidence_suffix)
        return self.add_data_columns(res, select)

    # TODO(asilvers): What are we doing with naming this?
    def infer_unobserved(
            self,
            df,  # type: DataFrame
            confidence_suffix='_conf',  # type: str
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Infer the missing values in a hypothetical data set.

        Infer values for any missing cells in `df` given the other values in
        that row.

        Args:
            df: A dataframe with missing data to infer.
            confidence_suffix: The string to append to each column name to
                generate its corresponding confidence column's name.
            random_seed: optional random seed between 0 and 2**32-1

        Returns:
            A data frame containing 2*len(df.columns) columns, one for each
            column and one for each column's confidence. If a cell is present
            in the data, both the cell and its corresponding confidence cell
            will contain NA.
        """
        for col in df.columns:
            if (col + confidence_suffix) in df.columns:
                raise ValueError(
                    "The confidence column for %r would clash with %r" %
                    (col, col + confidence_suffix))

        nulled_df = df.where(pd.notnull(df), None)
        json_data = nulled_df.to_dict(orient='list')
        req = {'data': json_data}
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._endpoint.infer.post(json=req)
        return self._infer_response(resp.json(), df.columns, confidence_suffix)

    def _infer_response(self, respjson, target_order, suffix):
        # Pass `target_order` because who knows what order respjson is in.

        # `infer_unobserved` doesn't return rowids
        df = DataFrame(respjson['columns'], index=respjson.get('rowids'))
        for colname, uncertainty in respjson['uncertainty'].items():
            df[colname + suffix] = uncertainty

        # Re-order the columns so the confidence columns is next to the data
        column_order = []  # type: List[str]
        for c in target_order:
            column_order.extend((c, c + suffix))
        return df[column_order]

    def wait(self, seconds=60):  # type: (float) -> Dict[str, Any]
        """Waits until this model is built, up to `seconds` seconds.

        The return value is similar to `build_progress`.
        """
        resp = self._endpoint.wait.post(json={'seconds': seconds})
        return resp.json()


def _ensure_rowids_are_real_ints(rowids):
    # numpy int64s aren't JSON serializable, even though they look like
    # ints in pretty much every other way. Convert them. Yes, this also
    # casts strings, but if they successfully cast, so be it.
    return [int(r) for r in rowids]


def _abbreviate_values(values, max_len=40):
    if values is None:
        return None
    values_str = ''
    for i, d in enumerate(values):
        v = d.value
        vv = v if i == 0 else ', ' + v
        if len(values_str + vv) < (max_len - 7):
            values_str += vv
        elif i == 0:
            return '{...}'
        else:
            return '{%s, ...}' % (values_str,)
    return '{%s}' % (values_str,)


def _double_encode(val):
    return quote(quote(val))


def _is_sequence_list(column):  # type: (Sequence[Any]) -> bool
    return all(elem is None or isinstance(elem, list) for elem in column)


def _min_seconds_remaining(models):
    # Find the model we think is closest to being done, then return the number
    # of seconds left in its build.
    min_seconds = None  # type: BuildProgress
    for m in models:
        # TODO(asilvers): Rather than forcing clients to write this themselves
        # (edpclient.js also has this code) we should probably compute this
        # server-side.
        progress = m['build_progress']
        if progress['status'] == 'in_progress':
            start_time = progress['start_time']
            now = time.time()
            elapsed_seconds = now - start_time
            fraction_done = progress.get('fraction_done', 0)
            if fraction_done > .01:
                expected_total_seconds = elapsed_seconds / fraction_done
                remaining_seconds = expected_total_seconds - elapsed_seconds
                if (min_seconds is None or
                        remaining_seconds < min_seconds.remaining):
                    min_seconds = BuildProgress(
                        int(elapsed_seconds), int(expected_total_seconds))

    return min_seconds


class BuildProgress(
        collections.namedtuple('BuildProgress', ['elapsed', 'total'])):

    @property
    def remaining(self):
        return self.total - self.elapsed
