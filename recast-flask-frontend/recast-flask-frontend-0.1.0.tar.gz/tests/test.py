import os

import unittest
import recastfrontend.server
from recastfrontend.server import create_app
from recastfrontend.server import db
import recastdb.models
from flask import url_for
import json

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()
        
    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_setup(self):
        self.assertTrue(self.app is not None)
        self.assertTrue(self.client is not None)
        
    def test_home_page(self):
        response = self.client.get('/')
        self.assertTrue(response.status_code == 200)
        #json_response = json.loads(response.data.decode('utf-8'))
        #self.assetTrue('Stranger' in response.get_data(as_text=True))
        #print self.client.get(url_for('about'))
        pass

    def test_about_page(self):
        response = self.client.get('/about')
        self.assertTrue(response.status_code == 200)

    def test_analysis_page(self):
        response = self.client.get('/analyses')
        self.assertTrue(response.status_code == 200)
        
    def test_show_last_analysis(self):
        query = recastdb.models.Analysis.query.all()
        self.assertTrue(len(query) > 0)
        response = self.client.get('/analysis/'+str(len(query)))
        self.assertTrue(response.status_code == 200)

    def test_requests(self):
        response = self.client.get('/requests')
        self.assertTrue(response.status_code == 200)
        
    def test_subscriptions(self):
        response = self.client.get('/subscriptions')
        self.assertTrue(response.status_code == 200)

    def test_analysis_form(self):
        response = self.client.get('analysis_form')
        self.assertTrue(response.status_code == 200)
        
    def test_show_last_request(self):
        query = recastdb.models.ScanRequest.query.all()
        self.assertTrue(len(query) > 0)
        response = self.client.get('request_form/'+str(len(query)))
        self.assertTrue(response.status_code == 200)

    def test_db(self):
        user = recastdb.models.User(name="Test User", email="test@email.com")
        db.session.add(user)
        db.session.commit()
        
        run_condition = recastdb.models.RunCondition(name="run condition test", description="test")
        db.session.add(run_condition)
        db.session.commit()
        
        analysis = recastdb.models.Analysis(title="Analysis title test", description="Testing description test", collaboration="ATLAS", run_condition_id=run_condition.id, owner_id=user.id)
        db.session.add(analysis)
        db.session.commit()

        request = recastdb.models.ScanRequest(description_of_model="Model description test", reason_for_request="Reason for request test", additional_information="Additional info test", analysis_id=analysis.id, requester_id=user.id)
        db.session.add(request)
        db.session.commit()

        point_request = recastdb.models.PointRequest(scan_request_id=request.id, requester_id=user.id)
        db.session.add(point_request)
        db.session.commit()

        basic_request = recastdb.models.BasicRequest(point_request_id=point_request.id, requester_id=user.id, number_of_events=0)
        db.session.add(basic_request)
        db.session.commit()

        lhe_file = recastdb.models.LHEFile(basic_request_id=basic_request.id)
        db.session.add(lhe_file)
        db.session.commit()

        subscription = recastdb.models.Subscription(subscription_type="Observer", description="Description test", requirements="Requirements test", notifications="Recast Requests", subscriber_id=user.id, analysis_id=analysis.id)
        db.session.add(subscription)
        db.session.commit()
