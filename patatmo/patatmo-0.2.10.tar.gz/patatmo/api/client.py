#!/usr/bin/env python3
# system modules
import logging
import time

# internal modules
from .. import utils
from . import authentication
from . import responsetypes
from . import requests
from .variables import *
from .errors import *


class NetatmoClient(object):
    """
    Netatmo api client
    
    Args:
        authentication (Authentication, optional): 
            the authentication used for Oauth2 authentication
    """
    def __init__(self, authentication = None):
        self.authentication = authentication


    ##################
    ### Properties ###
    ##################
    @property
    def logger(self):
        """ the logging.Logger used for logging.
        Defaults to logging.getLogger(__name__).
        """
        try: # try to return the internal property
            return self._logger 
        except AttributeError: # didn't work
            return logging.getLogger(__name__) # return default logger
    
    @logger.setter
    def logger(self, logger): # pragma: no cover
        assert isinstance(logger, logging.Logger), \
            "logger property has to be a logging.Logger"
        self._logger = logger
    
    @property
    def authentication(self): # pragma: no cover
        """ The Authentication used for server authentication
        Defaults to an empty instance of Authentication on first use.
        """
        try: # try to return the internal attribute
            return self._authentication
        except AttributeError: # didn't work
            # set it to new instance
            self._authentication = authentication.Authentication()
        # return internal attribute
        return self._authentication

    @authentication.setter
    def authentication(self, newauth):
        if not isinstance(newauth, authentication.Authentication):
            self.logger.debug("authentication property needs to be of " 
                "class Authentication. Using empty instance instead " 
                "of {}.".format(newauth))

            self._authentication = authentication.Authentication()
        else:
            self._authentication = newauth


    ###############
    ### Methods ###
    ###############
    def Getpublicdata(self,region,required_data=None,filter=False):
        """ Issue a Getpublicdata POST request to the netatmo server

        Args:
            region (dict): dict definig the desired request region. Required
                keys: lat_ne [-85;85], lat_sw [-85;85], lon_ne [-180;180] and
                lon_sw [-180;180] with lat_ne > lat_sw and lon_ne > lon_sw
            required_data (str or None, optional): Defaults to None which means
                no filter.
            filter (bool, optional): server-side filter for stations with
                unusual data. Defaults to False with means no filter

        Returns:
            instance of GetpublicdataResponse with response data

        Raises:
            InvalidApiInputError or derivates if wrong input was provided
            ApiResponseError or derivates if api responded with error

        Returns:
            GetpublicdataResponse: The api response
        """

        ### Check the input ###
        # check the region
        for key,bounds in GETPUBLICDATA_REGION_BOUNDS.items():
            try:
                if region[key] < bounds[0] or region[key] > bounds[1]:
                    raise InvalidRegionError
            except:
                raise InvalidRegionError
        if region["lat_ne"] < region["lat_sw"] \
            or region["lon_ne"] < region["lon_sw"]:
                raise InvalidRegionError
        # check the required_data option
        if required_data not in GETPUBLICDATA_ALLOWED_REQUIRED_DATA \
            and required_data is not None:
            raise InvalidRequiredDataError
        # check the filter option
        if not isinstance(filter,bool):
            raise InvalidApiInputError("'filter' needs to be bool")

            
        ### Create the payload ###
        payload = {} # start with empty dict
        # set the access token
        payload["access_token"] = self.authentication.tokens.get("access_token")
        # set the region
        payload.update(region)
        # set the required_data
        if required_data is not None: 
            payload["required_data"] = str(required_data)
        # set the filter option
        payload["filter"] = str(filter).lower()

        ### issue the request ###
        apirequest = requests.GetpublicdataRequest( payload = payload )
        apiresponse = apirequest.response

        ### check for errors ###
        error = apiresponse.response.get("error",{}).get("message")
        if error: raise API_ERRORS.get(error,ApiResponseError(error))

        return apiresponse


    def Getmeasure(self,device_id,module_id=None,type=None,
        scale=None,date_begin=None,date_end=None,real_time=False,
        optimize=False):
        """ Issue a Getmeasure POST request to the netatmo server
        Taken from API documentation: 
        https://dev.netatmo.com/dev/resources/technical/reference/common/getmeasure

        Args:
            device_id (str): The mac address of the device
            module_id (str, optinal): The mac address of the module of
                interest. If not specified, returns data of the device. If
                specified, returns data from the specified module
            type (list of str, optional): Measures interested in. List of
                "rain","humidity","pressure","wind" and "temperature".
            scale (str, optional): Timelapse between two measurements. "max"
                (every value is returned), "30min" (1 value every 30min),
                "1hour", "3hours", "1day", "1week", "1month". Defaults to "max".
            date_begin,date_end (int, optional): UNIX-timestamp of first/last
                measure to receive. Limit is 1024 measures.
            optimize (bool, optional): Determines the format of the answer.
                Default is False. For mobile apps we recommend True and False if
                bandwidth isn't an issue as it is easier to parse.
            real_time (bool, optional): If scale different than max, timestamps
                are by default offset + scale/2. To get exact timestamps, use
                true. Default is false.  

        Returns:
            GetmeasureResponse: The api response
        """
        ### Check the input ###
        # check device_id
        if not MAC_ADDRESS_REGEX.match(device_id):
            raise InvalidApiInputError("device_id = '{}' doesn't look like " 
                "MAC address".format(device_id))
        # check module_id
        if not module_id is None:
            if not MAC_ADDRESS_REGEX.match(module_id):
                raise InvalidApiInputError("module_id = '{}' doesn't look like " 
                    "MAC address".format(module_id))
        # check scale
        if not scale is None: # specified
            if not scale in GETMEASURE_ALLOWED_TYPES_BY_SCALE.keys():
                raise InvalidApiInputError("scale must be one of {}".format(
                    list(GETMEASURE_ALLOWED_TYPES_BY_SCALE.keys())))
        else: # not specified
            scale = "max" # use all values
        # check type
        allowed_types = GETMEASURE_ALLOWED_TYPES_BY_SCALE.get(scale,[])
        if not type is None: # specified
            if not all([x in allowed_types for x in type]):
                raise InvalidApiInputError("at given scale '{}' type must be a " 
                    "sublist of {}".format(scale,allowed_types))
        else: # not specified
            type = allowed_types # use all
        # check date_begin
        if not date_begin is None: 
            try: 
                date_begin = int(date_begin)
                if date_begin < 0: raise Exception
                if date_begin > time.time():
                    self.logger.warning(
                        "Specified date_begin is in the future!")
            except:
                raise InvalidApiInputError("date_begin must be UNIX-timestamp")
        if not date_end is None: 
            try: 
                date_end = int(date_end)
                if date_end < 0: raise Exception
            except:
                raise InvalidApiInputError("date_end must be UNIX-timestamp")
        try: 
            if date_end < date_begin: # compare begin and end
                raise InvalidApiInputError("date_end must be greater than " 
                    "date_begin")
        except TypeError: pass
        # check the optimize option
        if not isinstance(optimize,bool):
            raise InvalidApiInputError("optimize must be bool")
        # check real_time option
        if not isinstance(real_time,bool):
            raise InvalidApiInputError("real_time must be bool")


        ### Prepare the payload ###
        payload = {} # start with empty dict
        # access token
        payload["access_token"] = self.authentication.tokens.get("access_token")
        # device id
        payload["device_id"] = device_id
        # module id
        if not module_id is None:
            payload["module_id"] = module_id
        # scale
        payload["scale"] = scale
        # type
        payload["type"] = ",".join(type)
        # date_begin
        if not date_begin is None:
            payload["date_begin"] = date_begin
        # date_end
        if not date_end is None:
            payload["date_end"] = date_end
        # optimize
        payload["optimize"] = str(optimize).lower()
        # real_time
        payload["real_time"] = str(real_time).lower()

        ### issue the request ###
        apirequest = requests.GetmeasureRequest( payload = payload )
        apiresponse = apirequest.response

        ### check for errors ###
        error = apiresponse.response.get("error",{}).get("message")
        if error: raise API_ERRORS.get(error,ApiResponseError(error))

        return apiresponse


    def Getstationsdata(self, device_id, get_favourites = False):
        """ Issue a Getstationsdata POST request to the netatmo server
        Taken from API documentation: 

        Args:
            device_id (str): The mac address of the device
            get_favourites (bool): To retrieve user's favorite weather stations.
                Is converted to bool. Default is false.

        Returns:
            GetstationsdataResponse: The api response
        """
        ### Check the input ###
        # check device_id
        if not MAC_ADDRESS_REGEX.match(device_id):
            raise InvalidApiInputError("device_id = '{}' doesn't look like " 
                "MAC address".format(device_id))
        # check get_favourites
        try: get_favourites = bool(get_favourites) # try to convert to bool
        except:
            raise InvalidApiInputError("get_favourites has to be bool or at " 
                "least convertible to bool")

        ### create the payload ###
        payload = {} # start with empty dict
        # access token
        payload["access_token"] = self.authentication.tokens.get("access_token")
        # device id
        payload["device_id"] = device_id
        # get_favourites
        payload["get_favourites"] = str(get_favourites).lower()
        
        ### issue the request ###
        apirequest = requests.GetstationsdataRequest( payload = payload )
        apiresponse = apirequest.response

        ### check for errors ###
        error = apiresponse.response.get("error",{}).get("message")
        if error: raise API_ERRORS.get(error,ApiResponseError(error))

        return apiresponse


    def __repr__(self): # pragma: no cover
        """ python representation of this object
        """
        # self.logger.debug("__repr__ called")
        reprstring = ("{classname}(\n" 
              "authentication = {authentication}\n"
              ")").format(
            classname="{module}.{name}".format(
                name=self.__class__.__name__,module=self.__class__.__module__),
            authentication = self.authentication.__repr__()
            )
        return reprstring



