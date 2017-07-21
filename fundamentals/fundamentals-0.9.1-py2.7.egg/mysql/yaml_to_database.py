#!/usr/local/bin/python
# encoding: utf-8
"""
*Take key-values from a yaml file including a tablename and add them to a mysql table*

:Author:
    David Young

:Date Created:
    January 10, 2017
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import yaml
import requests
os.environ['TERM'] = 'vt100'
from fundamentals import tools
from fundamentals.mysql import convert_dictionary_to_mysql_table


class yaml_to_database():
    """
    *The worker class for the yaml_to_database module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary
        - ``pathToInputDir`` -- path to the directory containing the yaml files that will be added to the database table(s)
        - ``dbConn`` -- connection to database to add the content to
        - ``deleteFiles`` - - delete the yamls files once their content has been added to the database. Default * False*

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a yaml_to_database object, use the following:

        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - update the package tutorial if needed

        .. code-block:: python 

            usage code   
    """
    # Initialisation
    # 1. @flagged: what are the unique attrributes for each object? Add them
    # to __init__

    def __init__(
            self,
            log,
            pathToInputDir,
            dbConn,
            settings=False,
            deleteFiles=False

    ):
        self.log = log
        log.debug("instansiating a new 'yaml_to_database' object")
        self.settings = settings
        self.pathToInputDir = pathToInputDir
        self.dbConn = dbConn
        self.deleteFiles = deleteFiles

        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

        return None

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def ingest(self):
        """
        *ingest the yaml file contents into a database table*

        **Return:**
            - None

        **Usage:**
        .. todo::

            - add usage info
            - create a sublime snippet for usage
            - update the package tutorial if needed

        .. code-block:: python 

            usage code 
        """
        self.log.info('starting the ``ingest`` method')

        for d in os.listdir(self.pathToInputDir):
            if os.path.isfile(os.path.join(self.pathToInputDir, d)):
                self.add_yaml_file_content_to_database(
                    filepath=os.path.join(self.pathToInputDir, d),
                    deleteFile=self.deleteFiles
                )

        self.log.info('completed the ``ingest`` method')
        return None

    def add_yaml_file_content_to_database(
        self,
        filepath,
        deleteFile=False
    ):
        """*given a file to a yaml file, add yaml file content to database*

        **Key Arguments:**
            - ``filepath`` -- the path to the yaml file
            - ``deleteFile`` -- delete the yaml file when its content has been added to the database. Default *False*

        **Return:**
            - None

        **Usage:**
            ..  todo::

                - add usage info
                - create a sublime snippet for usage
                - update package tutorial if needed

            .. code-block:: python 

                usage code 

        """
        self.log.info(
            'starting the ``add_yaml_file_content_to_database`` method')

        # OPEN THE FILE AND GET THE YAML CONTENT
        try:
            stream = file(filepath, 'r')
            yamlContent = yaml.load(stream)
            stream.close()
        except:
            log.warning(
                'Could not parse the content of %(filepath)s as yaml content' % locals())
            return None

        if "table" not in yamlContent:
            log.warning(
                'A table value is need in the yaml content to indicate which database table to add the content to: %(filepath)s' % locals())
            return None

        dbTable = yamlContent["table"]
        del yamlContent["table"]

        # UNSHORTEN URL
        try:
            r = requests.head(yamlContent["url"], allow_redirects=True)
            yamlContent["url"] = r.url
        except:
            pass

        yamlContent["original_yaml_path"] = filepath

        if "url" in yamlContent:
            uniqueKeyList = ["url"]
        else:
            uniqueKeyList = []

        convert_dictionary_to_mysql_table(
            dbConn=self.dbConn,
            log=self.log,
            dictionary=yamlContent,
            dbTableName=dbTable,
            uniqueKeyList=uniqueKeyList,
            dateModified=True,
            returnInsertOnly=False,
            replace=True
        )
        if deleteFile:
            os.remove(filePath)

        self.log.info(
            'completed the ``add_yaml_file_content_to_database`` method')
        return None

    # use the tab-trigger below for new method
    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
