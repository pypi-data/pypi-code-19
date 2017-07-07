# -*- coding: utf-8 -*-
import unittest
from sqlalchemy import create_engine
from .database import build_engine_string
from flask_testing import TestCase

class TestFlaskPumpWood(TestCase):
    test_app_config = None
    flask_alchemy_db = None

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super(TestFlaskPumpWood, cls).setUpClass(*args, **kwargs)
        print ( 'Iniciando o test' )
        temp_engine = create_engine( build_engine_string(**cls.test_app_config['BK_TEST_DATABASE']) )
        with temp_engine.connect() as con:
            print ( 'Limpando conecções...' )
            kill_conections = """SELECT pg_terminate_backend(pg_stat_activity.pid)
                                 FROM pg_stat_activity 
                                 WHERE pg_stat_activity.datname IN ('%s', '%s')
                                 AND pid <> pg_backend_pid();""" % ( cls.test_app_config['DATABASE']['database']
                                                                   , cls.test_app_config['BK_TEST_DATABASE']['database'] )
            con.execute( kill_conections )

            print ( 'Derrubando a tabela de testes antiga...' )
            con.execute("commit;")
            con.execute( 'DROP DATABASE IF EXISTS %s;' % cls.test_app_config['DATABASE']['database'])

            print ( 'Copiando o BK para a tabela de testes...' )
            con.execute("commit;")
            con.execute( 'CREATE DATABASE %s WITH TEMPLATE %s;' % ( cls.test_app_config['DATABASE']['database']
                                                                  , cls.test_app_config['BK_TEST_DATABASE']['database'] ) )
            con.close()

    def setUp(self, *args, **kwargs):
        super(TestFlaskPumpWood, self).setUp(*args, **kwargs)
        # Create two savepoint
        self.savepoint1 = self.flask_alchemy_db.session.begin_nested()
        self.savepoint2 = self.flask_alchemy_db.session.begin_nested()
 
        # Make backup of session and replace with savepoint
        self.session_backup = self.flask_alchemy_db.session
        self.flask_alchemy_db.session = self.savepoint2.session

    def tearDown(self, *args, **kwargs):
        super(TestFlaskPumpWood, self).tearDown(*args, **kwargs)
        # Roll back to first savepoint
        self.savepoint1.rollback()
        # Restore original session
        self.flask_alchemy_db.session = self.session_backup
