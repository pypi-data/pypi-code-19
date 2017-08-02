from flask_nemo.plugin import PluginPrototype
from pkg_resources import resource_filename
from flask import url_for, send_from_directory, Markup, request, jsonify, Response
import requests
import re
from nemo_oauth_plugin import NemoOauthPlugin

PROXY = "/plokamos/proxy"

class PlokamosPlugin(PluginPrototype):
    """ Perseids Plokamos Annotator Plugin for Nemo

    :param annotation_update_endpoint
    :type URL of the annotation store's update endpoint

    :param annotation_select_endpoint
    :type URL of the annotation store's select endpoint

    :ivar interface: QueryInterface used to retrieve annotations
    :cvar HAS_AUGMENT_RENDER: (True) Adds a stack of render

    """
    HAS_AUGMENT_RENDER = True
    TEMPLATES = {
        "main": resource_filename("nemo_plokamos_plugin", "data/templates")
    }

    ROUTES = PluginPrototype.ROUTES + [
        ("/plokamos/assets/<path:filename>", "r_plokamos_assets", ["GET"]),
        (PROXY, "r_plokamos_proxy", ["GET","POST"])
    ]

    def __init__(self, annotation_update_endpoint, annotation_select_endpoint, proxied_update=True, proxied_select=False, *args, **kwargs):
        super(PlokamosPlugin, self).__init__(*args, **kwargs)
        self.__annotation_update_endpoint__ = annotation_update_endpoint
        self.__annotation_select_endpoint__ = annotation_select_endpoint
        self.proxied_update = proxied_update
        self.proxied_select = proxied_select

    @property
    def annotation_update_endpoint(self):
        return self.__annotation_update_endpoint__

    @property
    def annotation_select_endpoint(self):
        return self.__annotation_select_endpoint__

    def render(self, **kwargs):
        update = kwargs
        if 'passage_identifier' in update['url'].keys():
            update['urns'] = update['url']['collection']+':'+update['url']['textgroup']+'.'+update['url']['work']+'.'+update['url']['version']+':'+update['url']['passage_identifier']
        elif 'version' in update['url'].keys():
            update['urns'] = update['url']['collection']+':'+update['url']['textgroup']+'.'+update['url']['work']+'.'+update['url']['version']
        elif 'work' in update['url'].keys():
            update['urns'] = update['url']['collection']+':'+update['url']['textgroup']+'.'+update['url']['work']
        elif 'textgroup' in update['url'].keys():
            update['urns'] = update['url']['collection']+':'+update['url']['textgroup']
        elif 'collection' in update['url'].keys():
            update['urns'] = update['url']['collection']
        else:
            update['urns'] = 'invalid-urn-do-not-load'
        if self.proxied_update:
            update["update_endpoint"] = PROXY
        else:
            update["update_endpoint"] = self.annotation_update_endpoint
        if self.proxied_select:
            update["select_endpoint"] = PROXY
        else:
            update["select_endpoint"] = self.annotation_select_endpoint
        if "template" in kwargs and kwargs["template"] == "main::text.html":
            #update["template"] = "plokamos::text.html"
            update["text_passage"] = Markup(' '.join([ x.strip() for x in kwargs["text_passage"].splitlines() ]))
        # elif
        return update

    def r_plokamos_assets(self, filename):
        """ Routes for assets
        :param filename: Filename in data/assets to retrievee
        :return: Content of the file
        """
        return send_from_directory(resource_filename("nemo_plokamos_plugin", "data/assets"), filename)

    @NemoOauthPlugin.oauth_required
    def r_plokamos_proxy(self):
        """ Proxy to write to the annotation store

        :return: response from the remote query store
        :rtype: {str: Any}
        """

        query = request.data

        if self.is_authorized(query,NemoOauthPlugin.current_user()['uri']):
            try:
                resp = requests.post(self.annotation_update_endpoint, data=query, json=None,
                                     headers={"content-type": "application/sparql-update",
                                              "accept": "application/sparql-results+json"})
                resp.raise_for_status()
                return resp.content, resp.status_code
            except requests.exceptions.HTTPError as err:
                return str(err), resp.status_code
        else:
            return "Unauthorized request", 403


    def is_authorized(self,query,user_uri):
        """
            Verify AuthZ conditions for an annotation query

            :param the query
            :type str

            :param the user_uri to validate against the query
            :type str

            :return: True or false
            :rtype bool
        """
        authorized = False
        # we'd like to delegate to the annotation store to check the URI against the graph to which the annotation
        # belongs to make sure that the user has the rights to perform the operation.  For now we just confirm
        # that we had a user 
        return user_uri is not None

