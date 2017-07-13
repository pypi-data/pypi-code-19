from picardapi import PicardApi
import os
from underscore import _
import requests
from time import sleep


class Clone(object):
    api = None
    fakers = dict()
    usermap = None
    verbose = False

    def __init__(self):
        self.errors = []

    def doctype(self, name, source_stack, target_stack, documents, overwrite=False):
        """
        Clone doctype name from source_stack to target_stack

        Args:
            name (str): Name of doctype to clone
            source_stack (dict): dict containing config block name of stack from which you are cloning and username for access
            target_stack (dict): dict containing config block name of stack to which you are cloning and username for access
            documents (bool): if True then move over all documents, default False
            overwrite (bool): if true then delete conflicting assets on target_stack, default False

        Returns:
            boolean
        """
        # Obtain a picard api client configured to communicate with the souce_stack picard stack.
        picard = PicardApi.api(source_stack['name'])
        # Login as user
        picard.login(source_stack['username'])

        # Get the doctype we need to clone
        params = {"name": name, "full": True}
        doctype = picard.query('/custom/doctype', method="get", params=params).json

        # If specified, get the documents
        if documents:
            all_documents = picard.query("/custom/documentSearch", method="get", params={"size": 10000, 'doctypename': doctype['name']}).json

        # Obtain a new picard api client configured to communicate with the target_stack picard stack.
        picard = PicardApi.api(target_stack['name'])

        # Login as user
        picard.login(target_stack['username'])

        # Build the new doctype
        new_doctype = picard.query("/custom/doctype", method="post", params=doctype)
        if new_doctype.status_code == 409:
            if not overwrite:
                new_doctype = picard.query("/custom/doctype", method="get", params=doctype)
            else:
                rv = picard.query("/custom/doctype", method="delete", params={"name": doctype['name']})
                new_doctype = picard.query("/custom/doctype", method="post", params=doctype)
            print 'Doctype already exists.'
        elif new_doctype.status_code != 201:
            print 'Doctype cannot be created'
        if documents:
            if all_documents['response']['count'] == 0:
                print 'No documents found'
                return
            documents = []
            for document in all_documents['response']['documents']:
                document['_source'].pop("_owner", None)
                document['_source'].pop("_modified_by", None)
                document['_source'].pop("_modified", None)
                document['_source'].pop("_created", None)
                documents.append(document['_source'])
            params = {"doctype": new_doctype.json['id'], "documents": documents}
            rv = picard.query("/custom/documentBulkCreate", method="post", params=params)

        a=1

    def app(self, name, source_stack, target_stack, overwrite=False):
        """
        Clone app name from source_stack to target_stack

        Args:
            name (str): Name of app to clone
            source_stack (dict): dict containing config block name of stack from which you are cloning and username for access
            target_stack (dict): dict containing config block name of stack to which you are cloning and username for access
            overwrite (bool): if true then delete conflicting assets on target_stack, default False

        Returns:
            boolean
        """
        # Obtain a picard api client configured to communicate with the souce_stack picard stack.
        picard = PicardApi.api(source_stack['name'])
        # Login as user
        picard.login(source_stack['username'])

        # Get the apps we need to clone
        params = {"doctypename": "apps", "size": 1000, "should": [{"term": {"name": name}}]}
        app = picard.query('/custom/documentSearch', method="get", params=params).json['response']['documents']

        # return if no app exists with given name, otherwise strip the picard fields from the app
        if len(app) == 0:
            raise Exception("Source stack does not contain app named: " + name)
        app = app[0]
        app['_source'].pop("_modified_by", None)
        app['_source'].pop("_modified", None)
        app['_source'].pop("_created", None)
        app['_source'].pop("_owner", None)

        # Returns the app doctype, permissions, pages, and components
        page_doctype = self.get_app_doctype(picard, app)

        # Obtain a new picard api client configured to communicate with the target_stack picard stack.
        picard = PicardApi.api(target_stack['name'])

        # Login as user
        picard.login(target_stack['username'])

        #1 Build the app document
        app_params = {"doctypename": "apps","document": app['_source'], "_id": app['_source']['name']}
        rv = picard.query("/custom/document", method="post", params=app_params)
        if rv.status_code == 409:
            print 'App already exists.'
            # delete the app and pages doctype if the overwrite parameter is True
            if overwrite:
                rv = picard.query("/custom/document", method="delete", params={"doctypename": "apps", "name": app['_source']['name']})
                sleep(5)
                rv = picard.query("/custom/document", method="post", params=app_params)
                while rv.status_code == 409:
                    sleep(5)
                    rv = picard.query("/custom/document", method="post", params=app_params)

            if rv.status_code != 201:
                print 'Failed creating app'
                return False

        if overwrite:
            rv = picard.query("/custom/doctype", method="delete", params={"name": page_doctype['name']})

        #2 Build the pages doctype
        files = []
        if 'files' in page_doctype:
            files = page_doctype.pop("files", None)
        page_doctype['files'] = True
        rv = picard.query("/custom/doctype", method="post", params=page_doctype)
        target_page_doctype = picard.query("/custom/doctype", method="get", params={'name': page_doctype['name']})
        page_doctype['files'] = files

        # Create the images doc
        image_doc = picard.query("/custom/document", method="post",
                                 params={"doctype": target_page_doctype.json['id'],
                                         "document": {'name': 'images'},
                                         '_id': 'images'})

        if image_doc.status_code == 409:
            rv = picard.query("/custom/document", params={"doctype": target_page_doctype.json['id'], "name": "images"}).json
            image_doc = rv['body']
            image_doc['id'] = rv['id']
        else:
            image_doc = image_doc.json

        #2 Build the roles and user groups
        #3 Assign the grouped permissions
        if 'roles' in page_doctype:
            for role in page_doctype['roles']:
                rv = picard.query("/auth/role", method="post", params=role)
                rv = picard.query("/auth/role", method="get", params=role)
                role['grouping_type'] = 'role'
                role['grouping_uuid'] = rv.json['id']
                role['doctype'] = target_page_doctype.json['id']
                rv = picard.query("/custom/grouping", method="post", params=role)

        # Create the pages
        for page in page_doctype['pages']:
            if 'html' not in page['_source'] or 'javascript' not in page['_source']:
                if page['_source']['name'] == 'images':
                    for file in page_doctype['files']:
                        resp = requests.get(file['url'], stream=True)
                        with open(file['filename'], 'wb') as f:
                            f.write(resp.content)

                        rv2 = picard.query('/files/file', method="post",
                                           params={'id': image_doc['id'], 'filename': file['filename']})
                        with open(file['filename'], 'rb') as content_file:
                            print("Uploading file: " + file['filename'])
                            requests.put(rv2.json['url'], data=content_file, headers={"Content-Type": "image/jpeg"})
                        os.remove(file['filename'])
                else:
                    continue
            page['_source'].pop("_modified_by", None)
            page['_source'].pop("_modified", None)
            page['_source'].pop("_created", None)
            page['_source'].pop("_owner", None)
            page['_source'].pop("id", None)
            if page['_source']['name'] != 'images':
                new_doc = picard.query("/custom/document", method="post", params={'doctype':target_page_doctype.json['id'],
                                                                                  'document':page['_source'],
                                                                                  '_id': page['_source']['name']})


        # Create the components
        id = 1
        for component in page_doctype['components']:
            if 'html' not in component['_source'] or 'javascript' not in component['_source']:
                continue
            id += 1
            component['_source'].pop("_modified_by", None)
            component['_source'].pop("_modified", None)
            component['_source'].pop("_created", None)
            component['_source'].pop("_owner", None)
            new_doc = picard.query("/custom/document",
                                   method="post",
                                   params={'doctypename':'components',
                                           'document':component['_source'],
                                           '_id': component['_source']['name']})
            if new_doc.status_code == 409 and overwrite:
                new_doc = picard.query("/custom/document",
                                       method="put",
                                       params={'doctypename':'components',
                                               'document':component['_source'],
                                               'name': component['_source']['name']})


        a = 1

    def get_app_doctype(self, picard, app):
        # Get the corresponding pages doctype
        page_doctype = picard.query("/custom/doctype",
                                    method="get",
                                    params={"name": app['_source']['pages'], "full": True}).json

        # Get any roles or user groups that are part of the grouped permissions for this doctype
        remote_roles = []
        remote_usergroups = []
        for permtype in ['read','write']:
            for role in page_doctype['groupings'][permtype]['role']:
                this_role = picard.query("/auth/role", {"name": role['groupingname']}).json
                this_role.pop("users", None)
                this_role['perm_type'] = permtype
                remote_roles.append(this_role)
            for role in page_doctype['groupings'][permtype]['roleuser']:
                picard.query("/auth/role", {"name": role['groupingname']}).json
                this_role['perm_type'] = permtype
                this_role.pop("users", None)
                remote_roles.append(this_role)
            for usergroup in page_doctype['groupings'][permtype]['usergroup']:
                this_grouping = picard.query("/auth/usergroup", {"name": usergroup['groupingname']}).json
                this_grouping['perm_type'] = permtype
                this_grouping.pop("users", None)
                remote_usergroups.append(this_grouping)

        page_doctype['roles'] = remote_roles
        page_doctype['usergroups'] = remote_usergroups

        # Get the pages
        params = {"doctypename": app['_source']['pages'], "size": 1000}
        page_doctype['pages'] = picard.query('/custom/documentSearch',
                                             method="get",
                                             params=params).json['response']['documents']

        images_doc = picard.query("/custom/document",
                                  {"name": "images","doctypename": app['_source']['pages'], "files": True}).json
        page_doctype['files'] = []
        if 'Contents' in images_doc['files']:
            for file in _.pluck(images_doc['files']['Contents'], 'Key'):
                print("Getting url for file: " + os.path.basename(file))
                res = picard.query("/files/file", {"id": images_doc['id'], "filename": os.path.basename(file)}).json
                res['filename'] = os.path.basename(file)
                page_doctype['files'].append(res)

        # Get the components
        params = {
            "doctypename": "components",
            "size": 1000,
            "sort": ["_modified:asc"],
            "should": [{"term": {"tags.text": app['_source']['name'].lower()}}]
        }
        page_doctype['components'] = picard.query('/custom/documentSearch',
                                                  method="get",
                                                  params=params).json['response']['documents']
        return page_doctype