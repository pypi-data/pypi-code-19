# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os
import tempfile
from random import getrandbits

import shutil

import re
from time import sleep

from django.conf import settings
from django.core.files import File
from django.template.defaultfilters import default_if_none
from django.utils.translation import ugettext_lazy as _

from django.db import models
from smb.SMBConnection import SMBConnection
import base64
import MySQLdb


def generate_hash():
    return hashlib.sha1("%032x" % getrandbits(160)).hexdigest()


class AppRegister(models.Model):
    """
        Represent an Application Client
    
    """
    name = models.CharField(
        max_length=255
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    token = models.CharField(
        max_length=40,
        default=generate_hash,
        unique=True
    )
    domain_name = models.CharField(
        max_length=255
    )
    active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        auto_now=True
    )

    def __unicode__(self):
        return u"{0}".format(
            self.name
        )


TYPE_REPO = (
    ('file_system', _('File System')),
    ('database', _('Database')),
)


DATABASE_TYPE = (
    ('postgres', _('Postgres')),
    ('mysql', _('Mysql')),
    ('oracle', _('Oracle')),
)



class PhotoRepository(models.Model):
    name = models.CharField(
        max_length=255
    )
    order = models.PositiveIntegerField(
        _('order')
    )
    repo_type = models.CharField(
        max_length=20,
        choices=TYPE_REPO
    )
    '''
        Fields of File System
    '''
    user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    password = models.CharField(
        max_length=80,
        null=True,
        blank=True
    )
    client_machine_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    server_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    domain = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    server_ip = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    service_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    path = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    '''
        Fields of Database
    '''
    engine = models.CharField(
        max_length=10,
        choices=DATABASE_TYPE,
        null=True,
        blank=True
    )
    database_name = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    database_user = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    database_password = models.CharField(
        max_length=80,
        null=True,
        blank=True
    )
    database_host = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    database_port = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    database_column_search = models.CharField(
        max_length=40,
        null=True,
        blank=True
    )
    database_table_search = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    database_column_filter = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    is_blob = models.BooleanField(
        default=False
    )
    active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    modified_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['order']

    @staticmethod
    def _connect_repo_file_system(repo, photo_name):
        """
            Get connection for repo
        
        :param repo: PhotoRepository
        :param photo_name: name of photo to search
        :return data_info: Dict 
        """

        data_info = {
            'path': '',
            'url': '',
            'type': '',
            'success': False
        }

        conn = SMBConnection(
            username=repo.user_id.encode(
                'ascii'
            ),
            password=repo.password.encode(
                'ascii'
            ),
            my_name=repo.client_machine_name.encode(
                'ascii'
            ),
            remote_name=repo.server_name.encode(
                'ascii'
            ),
            domain=repo.domain.encode(
                'ascii'
            ),
            use_ntlm_v2=True
        )

        try:
            if conn.connect(ip=repo.server_ip, port=139):
                try:

                    path = os.path.join(settings.MEDIA_ROOT, 'photographs', photo_name)
                    file_obj = open(path, 'wb')

                    '''
                        set permissions
                    '''
                    os.chmod(
                        path,
                        0660
                    )

                    file_attributes, file_size = conn.retrieveFile(
                        repo.service_name,
                        '{0}{1}'.format(
                            repo.path,
                            photo_name
                        ),
                        file_obj
                    )

                    if file_attributes:

                        data_info['path'] = path
                        data_info['url'] = '{0}{1}{2}{3}'.format(
                            settings.VALID_HOST,
                            settings.MEDIA_URL,
                            'photographs/',
                            photo_name
                        )
                        data_info['type'] = path.split('.')[-1]
                        data_info['success'] = True

                    sleep(2)

                    file_obj.close()
                    conn.close()

                    return data_info

                except Exception as e:
                    print "Operacion fallida"
                    conn.close()
        except Exception as e:
            print e
            conn.close()

        return data_info

    @staticmethod
    def _connect_repo_database(repo, photo_name):
        data_info = {
            'path': '',
            'url': '',
            'type': '',
            'success': False
        }

        if repo.repo_type == 'database':

            if repo.engine == 'mysql':
                print "mysql"
                '''
                    Mysql connection
                '''
                db = MySQLdb.connect(
                    host=repo.database_host,
                    user=repo.database_user,
                    passwd=repo.database_password,
                    db=repo.database_name,
                    port=default_if_none(
                        repo.database_port,
                        3306
                    )
                )

                try:
                    cursor = db.cursor()
                    query = "SELECT %s FROM %s WHERE %s=%s" % (
                        repo.database_column_search,
                        repo.database_table_search,
                        repo.database_column_filter,
                        photo_name
                    )
                    cursor.execute(query)

                    rows = cursor.fetchall()
                    if len(rows) > 0:
                        '''
                            data exists
                        '''
                        for row in rows:
                            data_info['url'] = base64.encodestring(
                                row[0]
                            )
                            data_info['type'] = 'blob'
                            data_info['success'] = True

                    cursor.close()

                except Exception as e:
                    print e

            elif repo.engine == 'postgres':
                '''
                    Postgres connection
                '''

        return data_info

    @staticmethod
    def _search_photo_local(photo_name):
        """
            Before search in repos ask to local storage of images
        
        :param photo_name: 
        :return: dict 
        """
        data_info = {
            'path': '',
            'type': '',
            'success': False
        }

        for name in PhotoRepository.format_rut(photo_name):

            path = '{0}{1}{2}'.format(
                settings.MEDIA_ROOT,
                '/photographs/',
                name
            )

            '''
                ask if file path exists on OS file system
            '''

            if os.path.exists(path):
                print "existe ruta"
                data_info['path'] = path
                data_info['url'] = '{0}{1}{2}{3}'.format(
                    settings.VALID_HOST,
                    settings.MEDIA_URL,
                    'photographs/',
                    name
                )
                data_info['type'] = path.split('.')[-1]
                data_info['success'] = True

                break
            else:
                print "no se pudo encontrar ruta"

        return data_info

    @staticmethod
    def search_photo_by_name(all_repos, photo_name, refresh=False):
        data_info = {
            'path': '',
            'url': '',
            'type': '',
            'success': False
        }

        if not refresh:
            data_info = PhotoRepository._search_photo_local(photo_name)

        if not data_info['success'] or refresh:
            for repo in all_repos:
                if repo.repo_type == 'file_system':

                    '''
                        search by multiples formats of photo_name
                    '''
                    for name in PhotoRepository.format_rut(photo_name):
                        data_info = PhotoRepository._connect_repo_file_system(
                            repo,
                            name
                        )
                        if data_info['success']:
                            break

                    '''
                        stop searching in repos if data_info success
                    '''

                    if data_info['success']:
                        break

                elif repo.repo_type == 'database':

                    data_info = PhotoRepository._connect_repo_database(
                        repo,
                        photo_name
                    )

                    if data_info['success']:
                        break

        return data_info

    @staticmethod
    def is_rut(photo_name):
        """
            Verified if photo_name is format like rut
        :return: boolean 
        """

        pattern_rut = re.compile("^([0-9]|['k'|'K']){9}")

        if pattern_rut.match(photo_name):
            return True

        return False

    @staticmethod
    def format_rut(photo_name):
        """
            Format photo_name for search in file system
        :return: list of str
        """

        photo_name_list = []

        img_types = [
            'jpg',
            'JPG',
            'png',
            'PNG',
        ]

        temp_photo_name = ''

        '''
            Add zeros to temp_photo_name minor 10
        '''
        if len(photo_name) < 10:
            for i in range(10 - len(photo_name)):
                temp_photo_name += '0'

        for t in img_types:
            '''
                Add photo name and multiples img types
            '''
            new_photo_name = '{0}{1}.{2}'.format(
                temp_photo_name,
                photo_name,
                t
            )

            photo_name_list.append(
                new_photo_name
            )

        return photo_name_list

    def __unicode__(self):
        return u"{0}".format(
            self.name
        )
