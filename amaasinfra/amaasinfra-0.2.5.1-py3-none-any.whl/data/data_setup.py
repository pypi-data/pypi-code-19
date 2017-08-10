import click
import os
import pymysql
from configparser import ConfigParser, NoSectionError
from amaasinfra.config.amaas_config import AMaaSConfig

class DatabaseSetter(object):
    def __init__(self):
        pass

    def recreate(self, schema, environment, db_config={}):
        environment = environment.lower()
        config = AMaaSConfig()
        if environment in ['dev', 'staging']:
            click.echo(f"Using {environment} Settings") 
            server = config.get_config_value(environment, 'db_server')
            username = config.get_config_value(environment, 'db_username')
            password = config.get_config_value(environment, 'db_password')
        elif environment == 'automation':
            click.echo(f"Using automation Settings") 
            server = db_config.get('db_server')
            username = db_config.get('db_username')
            password = db_config.get('db_password')
        else:
            click.echo("Using Local Settings")
            server="localhost"
            username="root"
            password="amaas"
        #connect to the server and create database
        try:
            click.echo("Connecting to the server")
            conn = pymysql.connect(server, user=username, passwd=password, charset='utf8')
            conn.cursor().execute("SET time_zone = '+00:00';")
            click.echo("Creating schema: " + schema)
            conn.cursor().execute("DROP DATABASE IF EXISTS "+ schema +";")
            conn.cursor().execute("CREATE DATABASE "+schema+" CHARACTER SET utf8 COLLATE utf8_unicode_ci;")
            conn.cursor().execute("USE "+schema+";")
            click.echo("Schema " + schema + " created successfully.")
        except (pymysql.InternalError, pymysql.OperationalError):
            raise Exception('Error Creating DB and Connection') 
        tables_path = os.path.join(os.getcwd() + "/tables")
        files = [f for f in os.listdir(tables_path)]
        #executing sql files
        try:
            for file in files:
                file_path = os.path.join(tables_path, file)
                with open(file_path) as SQL_file:
                    content=SQL_file.readlines()
                exe_line = ''
                for line in content:
                    exe_line+=line.partition('#')[0].rstrip()
                    if exe_line!='' and str(exe_line[-1]) == ';':
                        print("executing: "+exe_line)
                        conn.cursor().execute(exe_line)
                        exe_line=''
                click.echo("Create table "+file[:-4]+" successfully")
        except (pymysql.OperationalError):
            raise Exception('Error executing mysql files in tables')
