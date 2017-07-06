# -*- coding: utf-8 -*-

import os
import re
from uuid import uuid4
from blackfynn.utils import (
    infer_epoch, get_data_type, value_as_type, usecs_to_datetime
)
import datetime
import requests
import numpy as np
import dateutil.parser

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helpers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_package_class(data):
    """
    Determines package type and returns appropriate class.
    """
    content = data.get('content', data)
    ptype = content['packageType'].lower()

    if 'collection' in ptype:
        p = Collection
    elif ptype == 'dataset':
        p = Dataset
    elif ptype == 'timeseries':
        p = TimeSeries
    elif ptype == 'tabular':
        p = Tabular
    else:
        p = DataPackage

    return p


def must_exist(func):
    """
    Helper decorator that ensures the object is created on the platform
    before any operations within the decorated method are called.
    """
    def func_wrapper(self, *args, **kwargs):
        if not self.exists:
            raise Exception('Object must be created on the platform before method is called.') 
        return func(self, *args, **kwargs)
    return func_wrapper


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Basics
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Property(object):
    """
    Property entry applied to a blackfynn object
    """
    _data_types = ['string', 'integer', 'double', 'date', 'user']
    def __init__(self, key, value, fixed=False, hidden=False, category="Blackfynn", data_type=None):
        self.key = key
        self.fixed = fixed
        self.hidden = hidden
        self.category = category

        if data_type is None or (data_type.lower() not in self._data_types):
            dt,v = get_data_type(value)
            self.data_type = dt
            self.value = v
        else:
            self.data_type = data_type
            self.value = value_as_type(value, data_type.lower())

    def as_dict(self):
        """
        Typically used for body when calling API during creation
        """
        return {
            "key": self.key,
            "value": str(self.value), # value needs to be string :-(
            "dataType": self.data_type,
            "fixed": self.fixed,
            "hidden": self.hidden,
            "category": self.category
        }

    @classmethod
    def from_dict(cls, data, category='Blackfynn'):
        return cls(
            key=data['key'],
            value=data['value'],
            category=category,
            fixed=data['fixed'],
            hidden=data['hidden'],
            data_type=data['dataType']
        )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return u"<Property key='{}' value='{}' type='{}' category='{}'>" \
                    .format(self.key, self.value, self.data_type, self.category)


def get_all_class_args(cls):
    # possible class arguments
    if cls == object:
        return set()
    class_args = set()
    for base in cls.__bases__:
        # get all base class argument variables
        class_args.update(get_all_class_args(base))
    # return this class and all base-class variables
    class_args.update(cls.__init__.__func__.func_code.co_varnames)
    return class_args


class BaseNode(object):
    """
    Base class to serve all objects
    """
    _api = None
    _object_key = 'content'

    def __init__(self, id=None):
        self.id = id


    @classmethod
    def from_dict(cls, data, api=None, object_key=None):
        # which object_key are we going to use?
        if object_key is not None:
            obj_key = object_key
        else:
            obj_key = cls._object_key

        # validate obj_key
        if obj_key == '' or obj_key is None:
            content = data
        else:
            content = data[obj_key]

        class_args = get_all_class_args(cls)

        # find overlapping keys
        kwargs = {}
        thing_id = content.pop('id')
        for k,v in content.iteritems():
            # check lower case var names
            if k.lower() in class_args:
                kwargs.update({k.lower(): v})
            # check camelCase --> camel_case
            kk = re.sub(r'[A-Z]', lambda x: '_'+x.group(0).lower(), k)
            if kk in class_args:
                kwargs.update({kk: v})
            # check s3case --> s3_case
            kk = re.sub(r'[0-9]', lambda x: x.group(0)+'_', k)
            if kk in class_args:
                kwargs.update({kk: v})

        # init class with args
        item = cls.__new__(cls)
        cls.__init__(item, **kwargs)

        item.id = thing_id

        if api is not None:
            item._api = api
            item._api.core.set_local(item)

        return item

    def __eq__(self, item):
        if self.exists and item.exists:
            return self.id == item.id
        else:
            return self is item

    @property
    def exists(self):
        return self.id is not None

    def __str__(self):
        return self.__repr__()


class BaseDataNode(BaseNode):
    """
    Base class to serve all data node-types on platform
    """
    _type_name = 'packageType'
    def __init__(self, name, type,
            parent=None,
            owner_id=None,
            id=None,
            provenance_id=None):

        super(BaseDataNode, self).__init__(id=id)
        self.name = name
        self.properties = {}
        if isinstance(parent, basestring) or parent is None:
            self.parent = parent 
        else:
            self.parent = parent.id
        self.type = type
        self.owner_id = owner_id
        self.provenance_id = provenance_id
        self.state = None

    def _set_properties(self, *entries):
        """
        Property is stored as dict of key:properties-entry to enable
        over-write of properties values based on key
        """
        for entry in entries:
            assert type(entry) is Property, "Properties wrong type"
            if entry.category not in self.properties:
                self.properties[entry.category] = {}
            self.properties[entry.category].update({entry.key:entry})

    def _set_property(self, key, value, fixed=False, hidden=False, category="Blackfynn", data_type=None):
        """
        More direct interface to setting properties (do not have to import Property model)
        """
        self._set_properties(
            Property(
                key=key,
                value=value,
                fixed=fixed,
                hidden=hidden,
                category=category,
                data_type=data_type)
        )

    @must_exist
    def add_properties(self, *entries):
        self._set_properties(*entries)

        # update on platform
        self._api.data.update_properties(self)

    @must_exist
    def insert_property(self, key, value, fixed=False, hidden=False, category="Blackfynn", data_type=None):
        self._set_property(
            key=key,
            value=value,
            fixed=fixed,
            hidden=hidden,
            category=category,
            data_type=data_type
        )

        # update on platform
        self._api.data.update_properties(self)

    def get_properties(self):
        """
        Returns flat list of Property objects.
        """
        props = []
        for category in self.properties.values():
            props.extend(category.values())
        return props

    def get_property(self, key, category='Blackfynn'):
        # TODO: Organize properites differently! We need to separate
        #       out categories, so they are not over-written.
        return self.properties[category][key]

    def remove_property(self, key, category='Blackfynn'):
        if key in self.properties[category]:
            # remove by setting blank
            self.properties[category][key].value = ""
            # update remotely
            self._api.data.update_properties(self)
            # get rid of it locally
            self.properties[category].pop(key)

    @must_exist
    def update(self):
        """
        Updates object on the platform (with any local contents) and syncs
        local instance with API response object.
        """
        r = self._api.core.update(self)
        self.__dict__.update(r.__dict__)

    @must_exist
    def delete(self):
        r = self._api.core.delete(self)
        self.id = None

    def set_ready(self):
        self.state = "READY"
        return self.update()

    def set_unavailable(self):
        self.state = "UNAVAILABLE"
        return self.update()

    def set_error(self):
        self.state = "ERROR"
        return self.update()

    def as_dict(self):
        d = {
            "state": self.state,
            "name": self.name,
            self._type_name: self.type,
            "properties": [
                m.as_dict() for m in self.get_properties()
            ]
        }

        if hasattr(self, 'parent') and self.parent is not None:
            d["parent"] = self.parent

        if self.provenance_id is not None:
            d["provenanceId"] = self.provenance_id

        return d

    @classmethod
    def from_dict(cls, data, *args, **kwargs):
        item = super(BaseDataNode,cls).from_dict(data, *args, **kwargs)

        try:
            item.state = data['content']['state']
        except:
            pass

        # parse, store parent (ID only)
        if 'parent' in data:
            parent = data['parent']
            if isinstance(parent, basestring):
                item.parent = parent
            else:
                pkg_cls = get_package_class(parent) 
                p = pkg_cls.from_dict(parent, *args, **kwargs)
                item.parent = p.id

        def cls_add_property(prop):
            cat = prop.category
            if cat not in item.properties:
                item.properties[cat] = {}
            item.properties[cat].update({prop.key: prop})

        # parse properties
        if 'properties' in data:
            for entry in data['properties']:
                if 'properties' not in entry:
                    # flat list of properties: [entry]
                    prop = Property.from_dict(entry, category=entry['category'])
                    cls_add_property(prop)
                else:
                    # nested properties list [ {category,entry} ]
                    category = entry['category']
                    for prop_entry in entry['properties']:
                        prop = Property.from_dict(prop_entry, category=category)
                        cls_add_property(prop)

        return item


class BaseCollection(BaseDataNode):
    """
    Abstract Package -- should never be used directly with API.
    """
    def __init__(self, name, package_type, **kwargs):
        super(BaseCollection, self).__init__(name, package_type, **kwargs)

        # items is None until an API response provides the item objects 
        # to be parsed, which then updates this instance.
        self._items = None

    @must_exist
    def add(self, *items):
        """
        Add items to the collection.
        """
        for item in items:
            # initialize if need be
            if self._items is None:
               self._items = [] 

            item.parent = self.id
            # create, if not already created
            new_item = self._api.core.create(item)
            item.__dict__.update(new_item.__dict__)

            # add item
            self._items.append(item)

    @must_exist
    def remove(self, *items):
        """
        Removes objects from collection, where items can be an object
        or the object's ID (string).
        """
        for item in items:
            if item not in self._items:
                raise Exception('Cannot remove item, not in collection:{}'.format(item))

        self._api.collections.remove_items(*items)
        # force refresh
        self._items = None

    @property
    @must_exist
    def items(self):
        if self._items is None:
            new_self = self._api.core.get(self, update=True)
            new_items = new_self._items
            self._items = new_items if new_items is not None else []

        return self._items

    @must_exist
    def print_tree(self, indent=0):
        if indent==0:
            print self
        for item in self.items:
            print ' '*(indent*2), item
            if isinstance(item, BaseCollection):
                item.print_tree(indent=indent+1)

    @must_exist
    def get_items_by_name(self, name):
        # note: non-hierarchical
        return filter(lambda x: x.name==name, self.items)

    @must_exist
    def get_items_names(self):
        return map(lambda x: x.name, self.items)

    # sequence-like method
    @must_exist
    def __getitem__(self, i):
        return self.items[i]

    # sequence-like method
    @must_exist
    def __len__(self):
        return len(self.items)

    # sequence-like method
    @must_exist
    def __delitem__(self, key):
        self.remove(key)

    @must_exist
    def __iter__(self):
        for item in self.items:
            yield item

    # sequence-like method
    @must_exist
    def __contains__(self, item):
        """
        Tests if item is in the collection, where item can be either
        an object's ID (string) or an object's instance.
        """
        if isinstance(item, basestring):
            some_id = self._api.data._get_id(item)
            item_ids = [x.id for x in self.items]
            contains = some_id in item_ids
        elif self._items is None:
            return False
        else:
            return item in self._items

        return contains

    @classmethod
    def from_dict(cls, data, *args, **kwargs):
        item = super(BaseCollection, cls).from_dict(data, *args, **kwargs)
        children = []
        if 'children' in data:
            for child in data['children']:
                pkg_cls = get_package_class(child)
                kwargs['api'] = item._api
                pkg = pkg_cls.from_dict(child, *args, **kwargs)
                children.append(pkg)
        item.add(*children)

        return item

    def __repr__(self):
        return "<BaseCollection name='{}' id='{}'>".format(self.name, self.id)


class DataPackage(BaseDataNode):

    def __init__(self, name, package_type, **kwargs):
        """
        DataPackage is the core data object representation on the platform.

        name:          Some clever name
        package_type:  TimeSeries, MRI, etc.

        """
        super(DataPackage, self).__init__(name=name, type=package_type, **kwargs)

        # local-only attribute
        self.session = None

    @must_exist
    def set_view(self, *files):
        """
        Set the object(s) used to view the package, if not the file(s) or source(s).
        """
        ids = self._api.packages.set_view(self, *files)
        # update IDs of file objects
        for i,f in enumerate(files):
            f.id = ids[i]

    @must_exist
    def set_files(self, *files):
        """
        Sets the files of a DataPackage. Files are typically modified 
        source files (e.g. converted to a different format).
        """
        ids = self._api.packages.set_files(self, *files)
        # update IDs of file objects
        for i,f in enumerate(files):
            f.id = ids[i]

    @must_exist
    def set_sources(self, *files):
        """
        Sets the sources of a DataPackage. Sources are the raw, unmodified
        files (if they exist) that contains the package's data.
        """
        ids = self._api.packages.set_sources(self, *files)
        # update IDs of file objects
        for i,f in enumerate(files):
            f.id = ids[i]

    @must_exist
    def append_to_files(self, *files):
        """
        Append to file list of a DataPackage
        """
        files = self._api.packages.set_files(self, *files, append=True)

    @must_exist
    def append_to_sources(self, *files):
        """
        Appends to source list of a DataPackage.
        """
        files = self._api.packages.set_sources(self, *files, append=True)

    @property
    def sources(self):
        """
        Returns the sources of a DataPackage. Sources are the raw, unmodified
        files (if they exist) that contains the package's data.
        """
        return self._api.packages.get_sources(self)

    @property
    def files(self):
        """
        Returns the files of a DataPackage. Files are the possibly modified 
        source files (e.g. converted to a different format), but they could also
        be the source files themselves.
        """
        return self._api.packages.get_files(self)

    @property
    def view(self):
        """
        Returns the object(s) used to view the package. This is typically a set of
        file objects, that may be the DataPackage's sources or files, but could also be
        a unique object specific for the viewer.
        """
        return self._api.packages.get_view(self)

    @classmethod
    def from_dict(cls, data, *args, **kwargs):
        item = super(DataPackage, cls).from_dict(data, *args, **kwargs)

        # parse objects
        if 'objects' in data:
            for otype in ['sources','files','view']:
                if otype not in data['objects']:
                    continue
                odata = data['objects'][otype]
                item.__dict__[otype] = [File.from_dict(x) for x in odata]

        return item

    @classmethod
    def from_id(cls, id):
        return self._api.packages.get(id)

    def __repr__(self):
        return "<DataPackage name='{}' id='{}'>".format(self.name, self.id)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Files
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class File(BaseDataNode):
    """
    File node on the Blackfynn platform
    """
    _type_name = 'fileType'

    def __init__(self, name, s3_key, s3_bucket, file_type, pkg_id=None, **kwargs):
        super(File, self).__init__(name, type=file_type, **kwargs)

        # data
        self.s3_key = s3_key
        self.s3_bucket = s3_bucket
        self.pkg_id = pkg_id
        self.local_path = None

    def as_dict(self):
        """
        Used for creating the file via API call
        """
        d = super(File, self).as_dict()
        d.update({
            "s3bucket": self.s3_bucket,
            "s3key": self.s3_key
        })
        d.pop('parent', None)
        props = d.pop('properties')
        return {
            'objectType': 'file',
            'content': d,
            'properties': props
        }

    @property
    def url(self):
        return self._api.packages.get_presigned_url_for_file(self.pkg_id, self.id)

    def download(self, destination):
        if self.type=="DirectoryViewerData":
            raise NotImplementedError("Downloading S3 directories is currently not supported")

        if os.path.isdir(destination):
            # destination dir
            f_local = os.path.join(destination, os.path.basename(self.s3_key))
        if '.' not in os.path.basename(destination):
            # destination dir + prefix
            f_local = destination + '_' + os.path.basename(self.s3_key)
        else:
            # exact location
            f_local = destination

        r = requests.get(self.url, stream=True)
        with open(f_local, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)

    def __repr__(self):
        return u"<File name='{}' type='{}' key='{}' bucket='{}' id='{}'>" \
                    .format(self.name, self.type, self.s3_key, self.s3_bucket, self.id)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Time series
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TimeSeries(DataPackage):
    """
    Represents a time-series package on the graph DB
    """
    def __init__(self, name, **kwargs):
        kwargs.pop('package_type', None)
        super(TimeSeries,self).__init__(name=name, package_type="TimeSeries", **kwargs)


    def streaming_credentials(self):
        return self._api.timeseries.get_streaming_credentials(self)

    @property
    def start(self):
        return sorted([x.start for x in self.channels])[0]

    @property
    def end(self):
        return sorted([x.end for x in self.channels])[-1]

    def limits(self):
        """
        Returns tuple (start, end) of package.
        """
        channels = self.channels
        start = sorted([x.start for x in channels])[0]
        end   = sorted([x.end   for x in channels])[-1]
        return start, end

    @property
    def channels(self):
        # always dynamically return channel list
        return self._api.timeseries.get_channels(self)

    def get_channel(self, channel):
        return self._api.timeseries.get_channel(self, channel)

    def add_channels(self, *channels):
        for channel in channels:
            ch = self._api.timeseries.create_channel(self, channel)
            channel.__dict__.update(ch.__dict__)

    def remove_channels(self, *channels):
        for channel in channels:
            self._api.timeseries.delete_channel(channel)
            channel.id = None
            channel._pkg = None

    # ~~~~~~~~~~~~~~~~~~
    # Data 
    # ~~~~~~~~~~~~~~~~~~
    def get_data(self, start=None, end=None, length=None, channels=None):
        return self._api.timeseries.get_ts_data(self,start=start, end=end, length=length, channels=channels)

    def get_data_iter(self, channels=None, start=None, end=None, length=None, chunk_size=None):
        return self._api.timeseries.get_ts_data_iter(self, channels=channels, start=start, end=end, length=length, chunk_size=chunk_size)

    def append_files(self, *files):
        return self._api.io.upload_files(self, files, append=True)

    def stream_data(self, data):
        return self._api.timeseries.stream_data(self, data)

    # ~~~~~~~~~~~~~~~~~~
    # Annotations
    # ~~~~~~~~~~~~~~~~~~

    @property
    def layers(self):
        # always dynamically return annotation layers
        return self._api.timeseries.get_annotation_layers(self)

    def get_layer(self, id_or_name):
        layers = self.layers
        matches = filter(lambda x: x.id==id_or_name, layers)
        if len(matches) == 0:
            matches = filter(lambda x: x.name==id_or_name, layers)

        if len(matches) == 0:
            raise Exception("No layers match criteria.")
        if len(matches) > 1:
            raise Exception("More than one layer matched criteria")
            
        return matches[0]

    def add_layer(self,layer,description=None):
        """
        Input:
            (required)
            Layer       :   TimeSeriesAnnotationLayer object or name of annotation layer
            (optional)
            description :   description of layer

        """
        return self._api.timeseries.create_annotation_layer(self,layer=layer,description=description)

    def add_annotations(self,layer,annotations):
        """
        Input:
            Layer - one of:
                TimeSeriesAnnotationLayer object
                name of annotation layer
                (non existing layers will be created)
            Annotations - :
                TimeSeriesAnnotation object(s)

        Output:
            list of annotation objects
        """
        cur_layer = self._api.timeseries.create_annotation_layer(self,layer=layer,description=None)
        return self._api.timeseries.create_annotations(layer=cur_layer, annotations=annotations)

    def insert_annotation(self,layer,annotation,start=None,end=None,channel_ids=None,description=None):
        cur_layer = self._api.timeseries.create_annotation_layer(self,layer=layer,description=None)
        return self._api.timeseries.create_annotation(layer=cur_layer, annotation=annotation,start=start,end=end,channel_ids=channel_ids,description=description)

    def delete_layer(self, layer):
        return self._api.timeseries.delete_annotation_layer(layer)

    def query_annotation_counts(self, channels, start, end, layer=None):
        return self._api.timeseries.query_annotation_counts(
            channels=channels,start=start,end=end,layer=layer)

    def __repr__(self):
        return "<TimeSeries name=\'{}\' id=\'{}\'>".format(self.name, self.id)


class TimeSeriesChannel(BaseDataNode):
    """
    TimeSeriesChannel represents a single source of time series data. (e.g. electrode)
    """
    def __init__(self, name, rate, start=0, end=0, unit='V', channel_type='continuous', source_type='unspecified', group="default", last_annot=0, spike_duration=None, **kwargs):
        """
        TODO: Remove last_annot as it won't be public
        Create a TimeSeriesChannel

        name      : name of channel
        start     : absolute start time of all data (datetime obj)
        end       : absolute end time of all data (datetime obj)
        unit      : unit of measurement

        """
        self.channel_type = channel_type.upper()

        super(TimeSeriesChannel, self).__init__(name=name, type=self.channel_type,**kwargs)

        self.rate = rate
        self.unit = unit
        self.last_annot = last_annot
        self.group = group
        self.start = start
        self.end = end
        self.spike_duration = spike_duration

        self._set_property("Source Type", source_type.upper(), fixed=True, hidden=True, category="Blackfynn")

        # local-only
        self._pkg = None

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = infer_epoch(start)

    @property
    def start_datetime(self):
        return usecs_to_datetime(self._start)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        self._end = infer_epoch(end)

    @property
    def end_datetime(self):
        return usecs_to_datetime(self._end)

    @must_exist
    def update(self):
        """
        Updates object on platform.
        """
        r = self._api.timeseries.update_channel(self)
        self.__dict__.update(r.__dict__)

    @property
    def segments(self):
        # TODO: query API to get segments
        raise NotImplementedError

    @property
    def gaps(self):
        # TODO: infer gaps from segments
        raise NotImplementedError

    def get_data_iter(self, start=None, end=None, length=None, chunk_size=None):
        """
        Returns an channel iterator over the data. 

        start   : start time of iterator (default: earliest time available).

        end     : end time of iterator (default: latest time avialable).
        -or-
        length  : some time length, e.g. '1s', '5m', '1h'

        chunk   : some time length, e.g. '1s', '5m', '1h'

        """
        return self._api.timeseries.get_ts_data_iter(self, channels=self, start=start, end=end, length=length, chunk_size=chunk_size)

    def as_dict(self):
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "unit": self.unit,
            "rate": self.rate,
            "channelType": self.channel_type,
            "lastAnnotation": self.last_annot,
            "group": self.group,
            "spikeDuration": self.spike_duration,
            "properties": [x.as_dict() for x in self.get_properties()]
        }

    def __repr__(self):
        return "<TimeSeriesChannel name=\'{}\' id=\'{}\'>".format(self.name, self.id)


class TimeSeriesAnnotationLayer(BaseNode):
    """
    Annotation Layer containing one or more annotations
    """
    _object_key = None

    def __init__(self, name, time_series_id, description=None, **kwargs):
        super(TimeSeriesAnnotationLayer,self).__init__(**kwargs)
        self.name = name
        self.time_series_id= time_series_id
        self.description = description

    def iter_annotations(self, window_size=10, channels=None):
        ts = self._api.core.get(self.time_series_id)
        return self._api.timeseries.iter_annotations(
            ts=ts, layer=self, channels=channels, window_size=window_size)

    def add_annotations(self, annotations):
        return self._api.timeseries.create_annotations(layer=self, annotations=annotations)

    def insert_annotation(self,annotation,start=None,end=None,channel_ids=None,description=None):
        return self._api.timeseries.create_annotation(layer=self, annotation=annotation,start=start,end=end,channel_ids=channel_ids,description=description)

    def annotations(self, start=None, end=None, channels=None):
        ts = self._api.core.get(self.time_series_id)
        return self._api.timeseries.query_annotations(
            ts=ts, layer=self, channels=channels, start=start, end=end)

    def annotation_counts(self, start, end, channels=None, layer=None):
        ts = self._api.core.get(self.time_series_id)
        return self._api.timeseries.query_annotation_counts(
            ts=ts, layer=self, channels=channels, start=start, end=end)

    def delete(self):
        return self._api.timeseries.delete_annotation_layer(self)

    def as_dict(self):
        return {
            "name" : self.name,
            "description" : self.description
        }

    def __repr__(self):
        return "<TimeSeriesAnnotationLayer name=\'{}\' id=\'{}\'>".format(self.name, self.id)


class TimeSeriesAnnotation(BaseNode):
    """
    Annotation is an event on one or more channels in a dataset
    """
    _object_key = None


    def __init__(self, label, channel_ids, start, end, name='',layer_id= None, 
                 time_series_id = None, description=None, **kwargs):
        super(TimeSeriesAnnotation,self).__init__(**kwargs)
        self.name = ''
        self.label = label
        self.channel_ids = channel_ids
        self.start = start
        self.end = end
        self.description = description
        self.layer_id = layer_id
        self.time_series_id = time_series_id

    def delete(self):
        return self._api.timeseries.delete_annotation(annot=self)

    def as_dict(self):
        channel_ids = self.channel_ids
        if type(channel_ids) is not list:
            channel_ids = [channel_ids]
        return {
            "name" : self.name,
            "label" : self.label, 
            "channelIds": channel_ids,
            "start" : self.start, 
            "end" : self.end, 
            "description" : self.description, 
            "layer_id" : self.layer_id, 
            "time_series_id" : self.time_series_id,
        }

    def __repr__(self):
        date = datetime.datetime.fromtimestamp(self.start/1e6)
        return "<TimeSeriesAnnotation label=\'{}\' layer=\'{}\' start=\'{}\'>".format(self.label, self.layer_id, date.isoformat())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Tabular
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Tabular(DataPackage):
    """
    Represents a tabular package on the graph DB
    """
    def __init__(self, name, **kwargs):
        kwargs.pop('package_type',None)
        super(Tabular,self).__init__(
            name=name,
            package_type="Tabular",
            **kwargs)
        self.schema = None

    def get_data(self,limit=1000, offset=0,order_by = None, order_direction='ASC'):
        return self._api.tabular.get_tabular_data(self,limit=limit,offset=offset ,order_by=order_by, order_direction=order_direction)

    def get_data_iter(self, chunk_size=10000, offset=0, order_by = None, order_direction='ASC'):
        return self._api.tabular.get_tabular_data_iter(self,chunk_size=chunk_size,offset=offset,order_by=order_by, order_direction=order_direction)

    def set_schema(self, schema):
        self.schema = schema
        # TODO: parse response
        return self._api.tabular.set_table_schema(self, schema)

    def get_schema(self):
        # TODO: parse response
        return self._api.tabular.get_table_schema(self)

    def __repr__(self):
        return "<Tabular name=\'{}\' id=\'{}\'>".format(self.name, self.id)


class TabularSchema(BaseNode):
    def __init__(self, name, column_schema = [], **kwargs):
        super(TabularSchema, self).__init__(**kwargs)
        self.name = name
        self.column_schema = column_schema

    @classmethod
    def from_dict(cls, data):
        column_schema = []
        for x in data['content']['columns']:
            if 'displayName' not in x.keys():
                x['displayName'] = ''
            column_schema.append(TabularSchemaColumn.from_dict(x))

        return cls(
            name = data['content']['name'],
            id = data['content']['id'],
            column_schema = column_schema
           )

    def as_dict(self):
        column_schema = [dict(
            name = x.name,
            displayName = x.display_name,
            datatype = x.datatype,
            primaryKey = x.primary_key,
            internal = x.internal
        ) for x in self.column_schema]
        return column_schema

    def __repr__(self):
        return "<TabularSchema name=\'{}\' id=\'{}\'>".format(self.name, self.id)

class TabularSchemaColumn():

    def __init__(self, name, display_name, datatype, primary_key = False, internal = False, **kwargs):
        self.name=name
        self.display_name = display_name
        self.datatype = datatype
        self.internal = internal
        self.primary_key = primary_key

    @classmethod
    def from_dict(cls, data):
        return cls(
            name = data['name'],
            display_name = data['displayName'],
            datatype = data['datatype'],
            primary_key = data['primaryKey'],
            internal = data['internal']          
        )

    def __repr__(self):
        return "<TabularSchemaColumn name='{}' display='{}' is-primary='{}'>".format(self.name, self.display_name, self.primary_key)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# User
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class User(BaseNode):

    _object_key = ''

    def __init__(self,
            email,
            first_name,
            last_name,
            organization,
            credential='',
            photo_url='',
            url='',
            authyId=0,
            accepted_terms='',
            is_super_admin=False,
            *args,
            **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.organization = organization
        self.credential = credential
        self.photo_url = photo_url
        self.url = url
        self.authyId = authyId
        self.accepted_terms = ''
        self.is_super_admin = is_super_admin

    def __repr__(self):
        return "<User email=\'{}\' id=\'{}\'>".format(self.email, self.id)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Organizations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Organization(BaseNode):
    _object_key = 'organization'

    def __init__(self,
            name,
            encryption_key_id="", 
            slug=None,
            terms=None,
            *args, **kwargs):
        super(Organization, self).__init__(*args, **kwargs)

        self.name = name
        self.terms = terms
        self.encryption_key_id = encryption_key_id
        self.slug = name.lower().replace(' ','-') if slug is None else slug

    @property
    def datasets(self):
        """
        Return all datasets for user for an organization (current context).
        """
        return self._api.datasets.get_all()

    def __repr__(self):
        return "<Organization name=\'{}\' id=\'{}\'>".format(self.name, self.id)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Datasets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Dataset(BaseCollection):
    def __init__(self, name, package_type=None, **kwargs):
        super(Dataset, self).__init__(name, "DataSet", **kwargs)
        self.__dict__.pop("parent", None)

    def upload_files(self, *files):
        return self._api.io.upload_files(self, files, append=False)

    def __repr__(self):
        return "<Dataset name='{}' id='{}'>".format(self.name, self.id)

    def collaborators(self):
        return self._api.datasets.get_collaborators(self)

    def add_collaborators(self, *collaborator_ids):
        return self._api.datasets.add_collaborators(self, *collaborator_ids)

    def remove_collaborators(self, *collaborator_ids):
        return self._api.datasets.remove_collaborators(self, *collaborator_ids)        

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Collections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Collection(BaseCollection):
    def __init__(self, name, **kwargs):
        kwargs.pop('package_type', None)
        super(Collection, self).__init__(name, package_type="Collection", **kwargs)

    def upload_files(self, *files):
        return self._api.io.upload_files(self, files, append=False)

    def __repr__(self):
        return "<Collection name='{}' id='{}'>".format(self.name, self.id)

class LedgerEntry(BaseNode):
    def __init__(self,
            reference,
            userId,
            organizationId,
            metric,
            value,
            date):

        super(LedgerEntry, self).__init__()
        self.reference = reference
        self.userId = userId
        self.organizationId = organizationId
        self.metric = metric
        self.value = value
        self.date = date

    @classmethod
    def from_dict(self, data):
        return LedgerEntry(data["reference"],
                data["userId"],
                data["organizationId"],
                data["metric"],
                data["value"],
                dateutil.parser.parse(data["date"]))

    def as_dict(self):
        return {
                "reference": self.reference,
                "userId": self.userId,
                "organizationId": self.organizationId,
                "metric": self.metric,
                "value": self.value,
                "date": self.date.replace(microsecond=0).isoformat() + 'Z'
                }

