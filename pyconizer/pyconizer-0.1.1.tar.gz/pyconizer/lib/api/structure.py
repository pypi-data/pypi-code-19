# -*- coding: utf-8 -*-
import base64
import json
import os

from pyconizer.lib.api.image import download_all_legend_icons
from pyconizer.lib.url import add_url_params


class Rule(object):

    def __init__(self, class_name=None, file_name=None, image=None, filter_class=None, url=None,
                 content=None, svg=None):
        self._class_name = class_name
        self._file_name = file_name
        self._image = image
        self._filter_class = filter_class
        self._url = url
        self._content = content
        self._svg = svg

    @property
    def dict(self):
        return {
            'class_name': self._class_name,
            'file_name': self._file_name,
            'image': self._image,
            'filter_class': self._filter_class,
            'url': self._url,
            'content': base64.b64encode(self._content) if self._content is not None else None,
            'svg': self._svg
        }

    @classmethod
    def from_dict(cls, rule_configuration):
        """
        Factory method to instantiate this class directly from a passed configuration dictionary.

        Args:
            rule_configuration (dict): The configuration for the rule.

        Returns:
            pyconizer.lib.api.structure.Rule: The constructed rule instance.
        """
        if rule_configuration.get('content'):
            rule_configuration.update({
                'content': base64.b64decode(rule_configuration.get('content'))
            })
        return cls(**rule_configuration)

    @property
    def svg(self):
        """

        Returns:
            list of pyconizer.lib.api.sld.v1_0_0.classes.SymbolizerType: The symbolizers.
        """
        return self._svg

    def set_svg(self, svg):
        """
        Set the symbolizers as SVG constructed from the SLD.

        Args:
            svg (str): The icon as a XML/SVG.
        """

        self._svg = svg

    @property
    def class_name(self):
        return self._class_name

    def set_url(self, url):
        self._url = url

    def set_content(self, content):
        self._content = content

    def url(self, wms_root_url, named_layer_name):
        return add_url_params(wms_root_url, {
            'layer': named_layer_name,
            'rule': self.class_name.encode('utf-8')
        })

    def create_rule_url(self, wms_root_url, named_layer_name):
        self._url = self.url(wms_root_url, named_layer_name)

    @property
    def rule_url(self):
        return self._url

    @property
    def file_name(self):
        return self._file_name

    def set_file_name(self, file_name):
        self._file_name = file_name

    @property
    def content(self):
        return self._content


class NamedLayer(object):

    def __init__(self, name=None, rules=None):
        """
        The abstract SLD related instance of a so called named layer.

        Args:
            name (str): The name of the named layer. This comes directly from the SLD specification.
            rules (list of pyconizer.lib.api.structure.Rule or None): The rules which's images might be
                downloaded eventually. This is the case when the structure is read from a already persisted
                JSON file.
        """
        self._name = name
        if rules and isinstance(rules, list):
            self._rules = rules
        else:
            self._rules = []

    @property
    def dict(self):
        """
        Delivers the dictionary representation of this instance.

        Returns:
            dict: The representation of this instance as a dictionary
        """
        rules = []
        if self._rules:
            for rule in self._rules:
                rules.append(rule.dict)
        return {
            'name': self._name,
            'rules': rules
        }

    @classmethod
    def from_dict(cls, named_layer_configuration):
        """
        Factory method to instantiate this class directly from a passed configuration dictionary.

        Args:
            named_layer_configuration (dict): The configuration for the named layer.

        Returns:
            pyconizer.lib.api.structure.NamedLayer: The constructed named layer instance.
        """
        rules = []
        if named_layer_configuration.get('rules'):
            for rule_configuration in named_layer_configuration.get('rules'):
                rules.append(Rule.from_dict(rule_configuration))
        named_layer_configuration.update({
            'rules': rules
        })
        return cls(**named_layer_configuration)

    @property
    def name(self):
        return self._name

    @property
    def rules(self):
        return self._rules

    def url(self, wms_root_url):
        return add_url_params(wms_root_url, {'layer': self.name})

    def create_rule_urls(self, wms_root_url):
        for rule in self._rules:
            rule.create_rule_url(wms_root_url, self.name)


class GetStyles(object):

    def __init__(self, request='GetStyles', service='WMS', srs='EPSG:2056', version='1.1.1', content=None):
        """
        The get styles instance.

        Args:
            request (str): The request parameter of WMS to get a legend graphic. Standard is
                'GetLegendGraphic'.
            service: The request parameter of WMS to define the service. Standard is to 'WMS'
            version: The request parameter of WMS to define the Version for the request. Standard is to
                '1.1.1'
            content (str or None): The sld content. It is can be None. This attribute is set when the
                configuration was read from a already existent JSON configuration.
        """
        self._request = request
        self._service = service
        self._srs = srs
        self._version = version
        self._content = content

    @property
    def dict(self):
        """
        Delivers the dictionary representation of this instance.

        Returns:
            dict: The representation of this instance as a dictionary
        """
        return {
            'request': self._request,
            'service': self._service,
            'srs': self._srs,
            'version': self._version,
            'content': self._content
        }

    @classmethod
    def from_dict(cls, get_styles_configuration):
        """
        Factory method to instantiate this class directly from a passed configuration dictionary.

        Args:
            get_styles_configuration (dict): The configuration for the get style.

        Returns:
            pyconizer.lib.api.structure.GetStyles: The constructed get styles instance.
        """
        return cls(**get_styles_configuration)

    def url(self, wms_root_url):
        """
        Adds all parameters stored to this instance to the passed URL to create a valid get styles request.

        Args:
            wms_root_url (str): The URL which the get styles parameters should be added to.

        Returns:
            str: The updated url string
        """
        return add_url_params(wms_root_url, self.dict)

    def set_content(self, content):
        """
        Set the SLD content of this get styles instance.
        Args:
            content (str): The XML string which represents the SLD belonging to this get styles instance.
        """
        self._content = content

    @property
    def content(self):
        return self._content


class GetLegend(object):

    def __init__(self, request='GetLegendGraphic', service='WMS', version='1.1.1', image_format='image/png',
                 width=72, height=36, named_layers=None):
        """
        The get legend instance.

        Args:
            request (str): The request parameter of WMS to get a legend graphic. Standard is
                'GetLegendGraphic'.
            service: The request parameter of WMS to define the service. Standard is to 'WMS'
            version: The request parameter of WMS to define the Version for the request. Standard is to
                '1.1.1'
            image_format: The request parameter of WMS to define the format for the legend images. Standard
                is to 'image/png'.
            width: The request parameter of WMS to define the width of the legend icon in pixel. Standard is
                to 72
            height: The request parameter of WMS to define the height of the legend icon in pixel. Standard
                is to 36
            named_layers (list of pyconizer.lib.api.structure.NamedLayer or None): The named layers which
                might be configured already. This is the case when the structure is read from a already
                persisted JSON file.
        """
        self._request = request
        self._service = service
        self._version = version
        self._image_format = image_format
        self._width = width
        self._height = height
        if named_layers and isinstance(named_layers, list):
            self._named_layers = named_layers
        else:
            self._named_layers = []

    @property
    def dict(self):
        """
        Delivers the dictionary representation of this instance.

        Returns:
            dict: The representation of this instance as a dictionary
        """
        named_layers = []
        if self._named_layers:
            for named_layer in self._named_layers:
                named_layers.append(named_layer.dict)
        return {
            'request': self._request,
            'service': self._service,
            'version': self._version,
            'image_format': self._image_format,
            'width': self._width,
            'height': self._height,
            'named_layers': named_layers
        }

    @classmethod
    def from_dict(cls, get_legend_configuration):
        """
        Factory method to instantiate this class directly from a passed configuration dictionary.

        Args:
            get_legend_configuration (dict): The configuration for the get legend.

        Returns:
            pyconizer.lib.api.structure.GetLegend: The constructed get legend instance.
        """
        named_layers = []
        if get_legend_configuration.get('named_layers'):
            for named_layer_configuration in get_legend_configuration.get('named_layers'):
                named_layers.append(NamedLayer.from_dict(named_layer_configuration))
        get_legend_configuration.update({
            'named_layers': named_layers
        })
        return cls(**get_legend_configuration)

    def url(self, wms_root_url):
        """
        Adds all parameters stored to this instance to the passed URL to create a valid get legend request.

        Args:
            wms_root_url (str): The URL which the get legend parameters should be added to.

        Returns:
            str: The updated url string
        """
        params = self.dict
        params.pop('named_layers')
        params.update({
            'format': params.get('image_format')
        })
        params.pop('image_format')
        return add_url_params(wms_root_url, params)

    def create_rule_urls(self, wms_root_url):
        for named_layer in self._named_layers:
            named_layer.create_rule_urls(self.url(wms_root_url))

    def add_named_layer(self, named_layer):
        """
        Adds a single named layer to this instance if the name does not exist already.

        Args:
            named_layer (pyconizer.lib.api.structure.NamedLayer): Appends a named layer to the instances list
                of named layers
        """
        for layer in self._named_layers:
            if layer.name == named_layer.name:
                raise KeyError('The named layer already exists in this instance. It is only allowed to use '
                               'unique names.')
        self._named_layers.append(named_layer)

    def add_named_layers(self, named_layers):
        """
        Adds a bunch of layers to this instance if the name does not exist already.

        Args:
            named_layers (list of pyconizer.lib.api.structure.NamedLayer): Appends all passed named layers to
                the instances list of named layers.
        """
        for layer in named_layers:
            self.add_named_layer(layer)

    @property
    def named_layers(self):
        return self._named_layers

    def set_named_layers(self, named_layers):
        """
        Adds a bunch of layers to this instance if the name does not exist already.

        Args:
            named_layers (list of pyconizer.lib.api.structure.NamedLayer): Appends all passed named layers to
                the instances list of named layers.
        """
        self._named_layers = named_layers


class Layer(object):

    def __init__(self, url, layer_name, get_legend, get_styles):
        """
        The class abstraction of a WMS-Layer. This construction holds everything necessary to query a WMS and
        produce the queries.

        Args:
            url (str): The root URL to reach the WMS.
            layer_name (str): The layer which should be used. This must be a single one.
            get_legend (pyconizer.lib.api.structure.GetLegend): The configuration of the get legend request.
                This mirrors the possible ULR-parameters which are commonly used for a get legend request on
                a WMS.
            get_styles (pyconizer.lib.api.structure.GetStyles): The configuration of the get styles request.
                This mirrors the possible ULR-parameters which are commonly used for a get styles request on
                a WMS.
        """
        self._url = url
        self._layer_name = layer_name
        self._get_legend = get_legend
        self._get_styles = get_styles

    @property
    def dict(self):
        """
        Delivers the dictionary representation of this instance.

        Returns:
            dict: The representation of this instance as a dictionary
        """
        return {
            'url': self._url,
            'layer': self._layer_name,
            'get_legend': self._get_legend.dict,
            'get_styles': self._get_styles.dict
        }

    @classmethod
    def from_dict(cls, layer_configuration):
        """
        Factory method to instantiate this class directly from a passed configuration dictionary.

        Args:
            layer_configuration (dict): The configuration for the layer.

        Returns:
            pyconizer.lib.api.structure.Layer: The constructed layer instance.
        """
        if layer_configuration.get('get_legend'):
            get_legend = GetLegend.from_dict(layer_configuration.get('get_legend'))
        else:
            get_legend = GetLegend()

        if layer_configuration.get('get_styles'):
            get_styles = GetStyles.from_dict(layer_configuration.get('get_styles'))
        else:
            get_styles = GetStyles()

        return cls(
            layer_configuration.get('url'),
            layer_configuration.get('layer'),
            get_legend,
            get_styles
        )

    @property
    def name(self):
        return self._layer_name

    @property
    def url(self):
        return self._url

    @property
    def get_styles_url(self):
        """
        Provides a fully usable URL to query the service.

        Returns:
            str: The URL constructed out of the configuration.
        """

        return self._get_styles.url(add_url_params(self._url, {'layers': self._layer_name}))

    @property
    def get_styles(self):
        return self._get_styles

    @property
    def get_legend(self):
        return self._get_legend

    @property
    def get_legend_url(self):
        """
        Provides a fully usable URL to query the service.

        Returns:
            str: The URL constructed out of the configuration.
        """

        return self._get_legend.url(add_url_params(self._url, {'layer': self._layer_name}))


class Configuration(object):

    def __init__(self, layers):
        """
        The class abstraction of configuration. This holds all the Information for further handling.
        Args:
            layers (list of pyconizer.lib.api.structure.Layer): All the layers which are corresponding to
                the dedicated configuration.
        """

        self._layers = layers

    @property
    def dict(self):
        """
        Delivers the list representation of this instance.

        Returns:
            list of dict: The list of this instance as a dictionary
        """

        configuration = []
        for layer in self._layers:
            configuration.append(layer.dict)
        return configuration

    @classmethod
    def from_dict(cls, configuration):
        """
        Factory method to instantiate this class directly from a passed configuration dictionary.

        Args:
            configuration (list): The configuration for all the layers.

        Returns:
            pyconizer.lib.api.structure.Configuration: The constructed configuration instance.
        """

        layers = []
        for layer in configuration:
            layers.append(Layer.from_dict(layer))
        return cls(layers)

    @property
    def layers(self):
        """
        The layers which are encapsulated in this configuration instance.

        Returns:
            list of pyconizer.lib.api.structure.Layer: All layer instances of this configuration.
        """

        return self._layers


def read(path):
    """
    Creates a configuration instance completely read from the passed JSON-file.

    Args:
        path (str): Path to the JSON which fits the structure.

    Returns:
        pyconizer.lib.api.structure.Configuration: The configuration instance.
    """
    configuration = Configuration.from_dict(json.loads(open(path).read()))
    return configuration


def write_rule_to_image_icon(path, rule):
    """
    Writes a single rules content to its file representation.

    Args:
        path (str): The path where the rule should be persisted.
        rule (pyconizer.lib.api.structure.Rule): The rule which should be consisted.
    """

    icon_file = open(
        '{combined_path}/{file_name}'.format(
            combined_path=path,
            file_name=rule.file_name
        ), 'wb'
    )
    icon_file.write(rule.content)
    icon_file.close()


def write_rule_to_svg_icon(path, rule):
    """
    Writes a single rules content to its file representation.

    Args:
        path (str): The path where the rule should be persisted.
        rule (pyconizer.lib.api.structure.Rule): The rule which should be consisted.
    """

    icon_file = open(
        '{combined_path}/{file_name}'.format(
            combined_path=path,
            file_name='{name}.svg'.format(name=rule.file_name.split('.')[0])
        ), 'wb'
    )
    icon_file.write(rule.svg)
    icon_file.close()


def persist_layer_path(path, layer_name, named_layer_name, path_template='{path}/{layer_name}/{style_name}'):
    """
    Path creation and persisting it in the file system.

    Args:
        path (str): The root folder where the construction should take place in. In this path the output
            file will be saved.
        layer_name (str): This must be the layer name fitting one of the names in the JSON configuration. It
            must not be the name of some named layer.
        named_layer_name (str): This is the SLD dependent named layer. It is some sub category of a WMS
            layer. However, this is used in the construction of paths.
        path_template (str): The pattern how the path is constructed. Normally this must not be adapted.

    Returns:
        str: The constructed and persisted path.
    """
    combined_path = path_template.format(
        path=path,
        layer_name=layer_name,
        style_name=named_layer_name
    )
    try:
        os.makedirs(combined_path)
    except OSError as e:
        print(e)
    return combined_path


def persist_mapping(path, config, file_name='mapping.json'):
    """
    Persists the mapping read from configuration instance to the file system in the path.

    Args:
        path (str): The root folder where the construction should take place in. In this path the output
            file will be saved.
        config (pyconizer.lib.api.structure.Configuration): The configuration which should be serialized
            and be persisted to a file.
        file_name (str): The name of the file which is used to save the configuration in. The files mime
            type is always json. The only thing you can change is the name if you don't like the name
            'mapping.json'.
    """

    try:
        os.makedirs(path)
    except OSError as e:
        print(e)
    mapping_file = open(
        os.path.abspath('{root_dir}/{file_name}'.format(
            root_dir=path,
            file_name=file_name
        )),
        'w+'
    )
    mapping_file.write(json.dumps(config.dict))
    mapping_file.close()
    print('json was created')


def write(path, config, file_name='mapping.json', images=False, svgs=False):
    """
    This is the persisting part of the structure. It the json_only parameter is set to False, there is also a
    folder structure created in file system containing the actual icon files. This is done inside the passed
    path.

    Args:
        path (str): The root folder where the construction should take place in. In this path the output
            file will be saved.
        config (pyconizer.lib.api.structure.Configuration): The configuration which should be serialized
            and be persisted to a file.
        file_name (str): The name of the file which is used to save the configuration in. The files mime
            type is always json. The only thing you can change is the name if you don't like the name
            'mapping.json'.
        images (bool): Switch to create also icon image files.
        svgs (bool): Switch to create also icon svg files.
    """
    download_all_legend_icons(config)
    if images or svgs:
        for layer in config.layers:
            for named_layer in layer.get_legend.named_layers:
                combined_path = persist_layer_path(path, layer.name, named_layer.name)
                for rule in named_layer.rules:
                    if images:
                        write_rule_to_image_icon(combined_path, rule)
                    if svgs:
                        write_rule_to_svg_icon(combined_path, rule)
    persist_mapping(path, config, file_name)
