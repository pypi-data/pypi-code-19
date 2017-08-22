from __future__ import unicode_literals

from wellaware._compat import long_
from wellaware.constants import make_headers, make_default_offset_limit, adjust_offset, chunk_list
from wellaware.base.base_entity import json_collection_to_entity_collection
from wellaware.base.base_resource import BaseResource
from wellaware.resources.assets import Asset
from wellaware.resources.data import DataOrdering
from wellaware.resources.points.resource import Points
from wellaware.resources.data.resource import Data


class AssetPatterns(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/assets'

    @classmethod
    def retrieve_data(cls, token, asset_id, start=None, end=None, limit=None, offset=None, order=None, parameters=None):
        if parameters is None:
            parameters = {}

        asset_id = cls.get_entity_id(asset_id, Asset)

        points = Points.retrieve_all(token=token, site_id=0, asset_id=asset_id, parameters=parameters)
        point_ids = [point.id for point in points]

        del parameters['offset']
        del parameters['limit']

        return Data.retrieve_data(
            token=token, point_ids=point_ids, start=start, end=end, limit=limit, offset=offset, order=order,
            parameters=parameters
        )

    @classmethod
    def find_assets_by_asset_type(cls, token, asset_type_filter, parameters=None):
        if parameters is None:
            parameters = {}

        if asset_type_filter is not None:
            parameters['assetType'] = asset_type_filter

        make_default_offset_limit(parameters)

        def filter_fetch_assets():
            response = cls.REST_CLIENT.get(cls.get_base_uri(cls.endpoint()), headers=make_headers(token), params=parameters)
            cls.REST_CLIENT.handle_response(response=response)

            return json_collection_to_entity_collection(response.json(), Asset)

        assets = filter_fetch_assets()

        if len(assets) == parameters['limit']:   # pragma: no cover
            while True:
                adjust_offset(parameters=parameters)
                next_assets = filter_fetch_assets()
                assets += next_assets
                if len(next_assets) < parameters['limit']:
                    break

        return assets

    @classmethod
    def find_assets_by_parameter_point_value(
        cls, token, asset_type_filter,
        parameter_point_type, parameter_point_value=None,
        parameters=None
    ):
        """
        Find Assets that have a parameter point type and optionally match a specific value.
        
        :param token: API token
        :param asset_type_filter: Asset Type filter 
        :param parameter_point_type: Parameter Point Type filter
        :param parameter_point_value: Parameter Point value filter (default None = no filter)
        :param parameters: 
        :return: 
        """
        if parameters is None:
            parameters = {}

        filtered_assets = cls.find_assets_by_asset_type(
            token=token, asset_type_filter=asset_type_filter, parameters=parameters
        )

        matching_assets = {}  # type: dict(long_, Asset)
        point_ids = []

        for asset in filtered_assets:
            asset_id = cls.get_entity_id(asset, Asset)
            parameters = {'pointType': parameter_point_type}
            make_default_offset_limit(parameters)

            matching_points = Points.retrieve_all(token, site_id=0, asset_id=asset_id, parameters=parameters)

            if matching_points is not None and len(matching_points) >= 1:
                matching_assets[matching_points[0].id] = asset
                point_ids.append(matching_points[0].id)

        assets = {}  # type: dict(Asset, Observation)

        for chunk in chunk_list(point_ids, 50):
            data = Data.retrieve_data(token=token, point_ids=chunk, start=0, limit=1, order=DataOrdering.DESCENDING)
            for point_id, observations in data.observations.items():
                if observations:
                    if parameter_point_value is not None:
                        if observations[-1].value == parameter_point_value:
                            assets[matching_assets[long_(point_id)]] = observations[-1]
                    else:
                        assets[matching_assets[long_(point_id)]] = observations[-1]

        return assets


__all__ = ['AssetPatterns']
