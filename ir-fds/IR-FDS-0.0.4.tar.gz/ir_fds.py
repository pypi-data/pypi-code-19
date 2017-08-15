#!/usr/bin/env python
#coding=utf-8
# 2017-02-27

import time
import socket
import hashlib

from fds.fds_client_configuration import FDSClientConfiguration
from fds.galaxy_fds_client import GalaxyFDSClient
from fds.galaxy_fds_client_exception import GalaxyFDSClientException

from fds.model.permission import AccessControlList
from fds.model.permission import Grant
from fds.model.permission import Grantee
from fds.model.permission import Permission
from fds.model.permission import GrantType

from fds.model.fds_object_metadata import FDSObjectMetadata

import traceback


"""
# FDS Configure
FDS_<tag>_REGION_NAME = ''
FDS_<tag>_APPKEY = ''
FDS_<tag>_APPSECRET = ''
FDS_<tag>_BUCKET_NAME = ''
FDS_<tag>_ENABLE_CDN = True
"""

def _get_config_attr(config, attr_name, default_value=''):
    if hasattr(config, attr_name):
        return getattr(config, attr_name)
    else:
        return default_value


class FDSClient(object):
    max_try = 3

    def __init__(self, config=None, tag=None):
        self.tag = tag
        if config is not None:
            self.init_config(config, tag)

    def init_config(self, config, tag=None):
        if not tag is None:
            self.tag = tag

        self._region_name = _get_config_attr(config, 'FDS_REGION_NAME')

        access_key = _get_config_attr(config, 'FDS_APPKEY')
        secret_key = _get_config_attr(config, 'FDS_APPSECRET')
        self._bucket_name = _get_config_attr(config, 'FDS_BUCKET_NAME')
        enable_cdn = _get_config_attr(config, 'FDS_ENABLE_CDN', False)

        if (not self.tag is None) and isinstance(self.tag,(str)):
            tag_region_name = _get_config_attr(config, 'FDS_%s_REGION_NAME'%self.tag)
            if tag_region_name != '':
                self._region_name = tag_region_name
                    
            tag_access_key = _get_config_attr(config, 'FDS_%s_APPKEY'%self.tag)
            if tag_access_key != '':
                access_key = tag_access_key

            tag_secret_key = _get_config_attr(config, 'FDS_%s_APPSECRET'%self.tag)
            if tag_secret_key != '':
                secret_key = tag_secret_key

            tag_bucket_name = _get_config_attr(config, 'FDS_%s_BUCKET_NAME'%self.tag)
            if tag_bucket_name != '':
                self._bucket_name = tag_bucket_name
        
            tag_enable_cdn = _get_config_attr(config, 'FDS_%s_ENABLE_CDN'%self.tag, False)
            if tag_enable_cdn != '':
                enable_cdn = tag_enable_cdn
        
        if access_key == '' or secret_key == '' or self._bucket_name == '':
            raise Exception('init_config failed!')

        print('FlaskFDSClient <%s> initial, region_name: %s'%(tag, self._region_name))
        config = FDSClientConfiguration(region_name=self._region_name, 
            enable_https=False, 
            timeout = 15,
            enable_cdn_for_download = enable_cdn)
        config.enable_md5_calculate = True
        self.fds_client = GalaxyFDSClient(access_key, secret_key, config)


    def exists(self, object_name):
        return self.fds_client.does_object_exists(self._bucket_name, object_name)


    def get(self, object_name):
        if self.exists(object_name):         
            retry = 0
            while retry < FDSClient.max_try:
                try:
                    obj = self.fds_client.get_object(self._bucket_name, object_name)
                    
                    str_data = ''
                    for chunk in obj.stream:
                        str_data += chunk

                    del obj
                    return str_data
                except Exception, ex:
                    time.sleep(0.5)
                    retry += 1

            raise Exception('get_object_string failed: %s/%s'%(self._bucket_name, object_name))
        else:
            return None


    def get_md5(self, object_name):
        if self.exists(object_name):
            retry = 0
            while retry < FDSClient.max_try:
                try:
                    md = self.fds_client.get_object_metadata(self._bucket_name, object_name)
                    if 'content-md5' in md.metadata:
                        return md.metadata['content-md5']
                    else:
                        obj = self.fds_client.get_object(self._bucket_name, object_name)
                        str_data = ''
                        for chunk in obj.stream:
                            str_data += chunk

                        return hashlib.md5(str_data).hexdigest()
                except Exception, ex:
                    time.sleep(0.5)
                    retry += 1            

            raise Exception('get_object_md5 failed: %s/%s'%(self._bucket_name, object_name))
        else:
            return None        


    def get_metadata(self, object_name):
        if self.exists(object_name):
            retry = 0
            while retry < FDSClient.max_try:
                try:
                    md = self.fds_client.get_object_metadata(self._bucket_name, object_name)
                    return md.metadata
                except Exception, ex:
                    time.sleep(0.5)
                    retry += 1            

            raise Exception('get_metadata failed: %s/%s'%(self._bucket_name, object_name))
        else:
            return None


    def save(self, data, object_name, metadata_dict={}, is_public=False, is_recheck=False):
        md = FDSObjectMetadata()
        for key in metadata_dict:
            md.add_user_metadata(key, metadata_dict[key])
        self.fds_client.put_object(self._bucket_name, object_name, data, md)

        if is_public:
            object_acl = AccessControlList()
            object_grant = Grant(Grantee('ALL_USERS'), Permission.READ)
            object_grant.type = GrantType.GROUP
            object_acl.add_grant(object_grant)
            self.fds_client.set_object_acl(self._bucket_name, object_name, object_acl)

        if is_recheck:
            get_str_file = self.get(object_name)
            if data != get_str_file:
                del get_str_file
                raise Exception('save object with recheck: recheck error!')


    def get_for_gz(self, object_name):
        import cStringIO as StringIO
        import gzip

        gz_data = self.get(object_name)

        if gz_data is not None:
            fileobj = StringIO.StringIO(gz_data)
            gzf = gzip.GzipFile(mode="rb", fileobj=fileobj)
            str_data = gzf.read()
            gzf.close()

            del gz_data
            return str_data
        else:
            return None


    def save_for_gz(self, data, object_name, metadata_dict={}, is_public=False, is_recheck=False):
        import cStringIO as StringIO
        import gzip
        import hashlib

        f = StringIO.StringIO()
        zfile = gzip.GzipFile(mode='wb', compresslevel=9, fileobj=f)
        zfile.write(data)
        zfile.close()
        gz_data = f.getvalue()
        f.close()

        del zfile
        del f
        return self.save(gz_data, object_name, metadata_dict, is_public, is_recheck)


    def delete(self, object_name):
        return self.fds_client.delete_object(self._bucket_name, object_name)



    def url(self, object_name, expiration_seconds=180):
        return self.fds_client.generate_presigned_uri(
            None, 
            self._bucket_name, 
            object_name, 
            time.time() * 1000 + expiration_seconds * 1000)