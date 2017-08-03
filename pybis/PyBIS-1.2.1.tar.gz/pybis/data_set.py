#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
data_set.py

Module with functions for operating on data sets.


Created by Chandrasekhar Ramakrishnan on 2017-04-05.
Copyright (c) 2017 Chandrasekhar Ramakrishnan. All rights reserved.
"""


def transfer_to_file_creation(content, file_creation, key, file_creation_key=None):
    if file_creation_key is None:
        file_creation_key = key
    if content.get(key):
        file_creation[file_creation_key] = content[key]


class GitDataSetCreation(object):
    def __init__(self, openbis, data_set_type, path, commit_id, dms, sample=None, properties={},
                 dss_code=None, parents=None, data_set_code=None, contents=[]):
        """Initialize the command object with the necessary parameters.
        :param openbis: The openBIS API object.
        :param data_set_type: The type of the data set
        :param data_set_type: The type of the data set
        :param path: The path to the git repository
        :param commit_id: The git commit id
        :param dms: An external data managment system object or external_dms_id
        :param sample: A sample object or sample id.
        :param properties: Properties for the data set.
        :param dss_code: Code for the DSS -- defaults to the first dss if none is supplied.
        :param parents: Parents for the data set.
        :param data_set_code: A data set code -- used if provided, otherwise generated on the server
        :param contents: A list of dicts that describe the contents:
            {'fileLength': [file length],
             'crc32': [crc32 checksum],
             'directory': [is path a directory?]
             'path': [the relative path string]}

        """
        self.openbis = openbis
        self.data_set_type = data_set_type
        self.path = path
        self.commit_id = commit_id
        self.dms = dms
        self.sample = sample
        self.properties = properties
        self.dss_code = dss_code
        self.parents = parents
        self.data_set_code = data_set_code
        self.contents = contents

    def new_git_data_set(self):
        """ Create a link data set.
        :return: A DataSet object
        """

        data_set_creation = self.data_set_metadata_creation()
        file_metadata = self.data_set_file_metadata()
        if not file_metadata:
            return self.create_pure_metadata_data_set(data_set_creation)
        return self.create_mixed_data_set(data_set_creation, file_metadata)

    def create_pure_metadata_data_set(self, data_set_creation):
        # register the files in openBIS
        request = {
            "method": "createDataSets",
            "params": [
                self.openbis.token,
                [data_set_creation]
            ]
        }

        # noinspection PyProtectedMember
        resp = self.openbis._post_request(self.openbis.as_v3, request)
        return self.openbis.get_dataset(resp[0]['permId'])

    def create_mixed_data_set(self, metadata_creation, file_metadata):
        data_set_creation = {
            "fileMetadata": file_metadata,
            "metadataCreation": metadata_creation,
            "@type": "dss.dto.dataset.create.FullDataSetCreation"
        }

        # register the files in openBIS
        request = {
            "method": "createDataSets",
            "params": [
                self.openbis.token,
                [data_set_creation]
            ]
        }

        server_url = self.data_store_url(metadata_creation['dataStoreId']['permId'])
        # noinspection PyProtectedMember
        resp = self.openbis._post_request_full_url(server_url, request)
        return self.openbis.get_dataset(resp[0]['permId'])

    def data_store_url(self, dss_code):
        data_stores = self.openbis.get_datastores()
        data_store = data_stores[data_stores['code'] == dss_code]
        return "{}/datastore_server/rmi-data-store-server-v3.json".format(data_store['hostUrl'][0])

    def data_set_metadata_creation(self):
        """Create the respresentation of the data set metadata."""
        dss_code = self.dss_code
        if dss_code is None:
            dss_code = self.openbis.get_datastores()['code'][0]

        # if a sample identifier was given, use it as a string.
        # if a sample object was given, take its identifier
        sample_id = self.openbis.sample_to_sample_id(self.sample)
        dms_id = self.openbis.external_data_managment_system_to_dms_id(self.dms)
        parents = self.parents
        parentIds = []
        if parents is not None:
            if not isinstance(parents, list):
                parents = [parents]
            parentIds = [self.openbis.data_set_to_data_set_id(parent) for parent in parents]
        data_set_creation = {
            "linkedData": {
                "@type": "as.dto.dataset.create.LinkedDataCreation",
                "contentCopies": [
                    {
                        "@type": "as.dto.dataset.create.ContentCopyCreation",
                        "path": self.path,
                        "gitCommitHash": self.commit_id,
                        "externalDmsId": dms_id
                    }
                ]
            },
            "typeId": {
                "@type": "as.dto.entitytype.id.EntityTypePermId",
                "permId": self.data_set_type
            },
            "sampleId": sample_id,
            "dataStoreId": {
                "permId": dss_code,
                "@type": "as.dto.datastore.id.DataStorePermId"
            },
            "parentIds": parentIds,
            "measured": False,
            "properties": self.properties,
            "@type": "as.dto.dataset.create.DataSetCreation"
        }
        if self.data_set_code is not None:
            data_set_creation['code'] = self.data_set_code
            data_set_creation["autoGeneratedCode"] = False
        else:
            data_set_creation["autoGeneratedCode"] = True

        return data_set_creation

    def data_set_file_metadata(self):
        """Create a representation of the file metadata"""
        return [self.as_file_metadata(c) for c in self.contents]

    def as_file_metadata(self, content):
        # The DSS objects do not use type
        # result = {"@type": "dss.dto.datasetfile.DataSetFileCreation"}
        result = {}
        transfer_to_file_creation(content, result, 'fileLength')
        transfer_to_file_creation(content, result, 'crc32', 'checksumCRC32')
        transfer_to_file_creation(content, result, 'directory')
        transfer_to_file_creation(content, result, 'path')
        return result
