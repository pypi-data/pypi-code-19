import sys
import unittest
try:
    from unittest import mock
except ImportError:
    from mock import mock
from mongomock import MongoClient
sys.modules['helga.plugins'] = mock.Mock() # hack to avoid py3 errors in test
from helga.db import db
from helga_team.helga_team import handle_add, handle_remove, handle_update, \
        parser_to_dict, parse, status


class TestTeam(unittest.TestCase):
    def setUp(self):
        self.db_patch = mock.patch(
            'pymongo.MongoClient',
            new_callable=lambda: MongoClient
        )
        self.db_patch.start()
        self.addCleanup(self.db_patch.stop)
        db.team.candidates.drop()

    def tearDown(self):
        db.team.candidates.drop()

    def test_parse(self):
        parser = parse(("-i", "id1", "-n" "A B", "-r", "Steve"))
        args = parser_to_dict(parser)
        self.assertEqual("id1", args['id'])
        self.assertEqual("A B", args['name'])
        self.assertEqual("Steve", args['recruiter'])

    def test_add_remove(self):
        first_name = "Mack1"
        second_name = "Mack2"
        parser_mock = mock.Mock()
        parser_mock.name = first_name
        parser_mock.recruiter = None
        parser_mock.owner = None
        parser_mock.status = None
        parser_mock.id = 1
        parser_mock.recruiter = None
        parser_mock.code_review = None
        owner = 'Nick1'
        # verify insertion
        handle_add(None, None, parser_mock, owner)
        candidate = db.team.candidates.find_one({"name": first_name})
        self.assertEqual(first_name, candidate['name'])
        candidate = db.team.candidates.find_one({"id": parser_mock.id})
        self.assertEqual(first_name, candidate['name'])
        # update name
        parser_mock.name = second_name
        handle_update(None, None, parser_mock, owner)
        candidate = db.team.candidates.find_one({"name": second_name})
        self.assertEqual(second_name, candidate['name'])
        # verify removal
        handle_remove(None, None, parser_mock, owner)
        try:
            candidate = db.team.candidates.find_one({"name": second_name})
            if candidate != None:
                raise Exception("Candidate should be None here!")
        except:
            pass

    def test_status(self):
        candidate = {
            'owner': 'owner1',
            'name': 'name1',
            'id': 'id1',
            'status': 'pending',
        }
        response = status(candidate)
        self.assertIn("owner1", response)
        self.assertIn("name1", response)
        self.assertIn("id1", response)
        self.assertIn("status", response)
        self.assertNotIn("recruiter", response)
        self.assertNotIn("code_review", response)


if __name__ == '__main__':
    unittest.main()
