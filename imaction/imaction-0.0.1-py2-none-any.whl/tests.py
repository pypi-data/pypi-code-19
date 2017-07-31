# encoding: utf-8
# pylint: disable=W0613, C0103, C0301

from unittest import TestCase

from imaction.as_action import (
    ACTION_NAME,
    ACTIONID_NAME,
    ACTION_ATTR_ACNAME,
    ACTION_ATTR_ACPARANAMES,
    ACTION_ATTR_ACPARADESC,
    NO_DESCRIPTION_MESSAGE,
    as_action,
    collect_action_names,
    metafunc_to_action,
    register_actions,
)


NAME_ACTION = 'signin'
DESC_ACTION = 'login with the given username and password'

NAME_USERNAME = 'uname'
DESC_USERNAME = 'name of user'

NAME_PASSWORD = 'pswd'
DESC_PASSWORD = 'password of user'

NAME_SAVEACCOUNT = 'save'
DESC_SAVEACCOUNT = 'whether save account information or not'


class ImactionDecoratorTester(TestCase):
    action_para_names = {
        'username': NAME_USERNAME,
        'password': NAME_PASSWORD,
        'save_account': NAME_SAVEACCOUNT,
    }
    action_para_descriptions = {
        'username': DESC_USERNAME,
        'password': DESC_PASSWORD,
        'save_account': DESC_SAVEACCOUNT,
    }

    def test_config_all_with_dict(self):
        @as_action(
            DESC_ACTION,
            para_names={
                'username': NAME_USERNAME,
                'password': NAME_PASSWORD,
                'save_account': NAME_SAVEACCOUNT,
            },
            para_descriptions={
                'username': DESC_USERNAME,
                'password': DESC_PASSWORD,
                'save_account': DESC_SAVEACCOUNT,
            },
        )
        def login_action(username, password, save_account):
            return {}

        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARANAMES), self.action_para_names)
        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARADESC), self.action_para_descriptions)

        action = login_action(username='Joe', password='psw-joe', save_account=False)
        self.assertIn(ACTIONID_NAME, action)

        action.pop(ACTIONID_NAME)
        expected_action = {
            ACTION_NAME: 'login_action',
            NAME_USERNAME: 'Joe',
            NAME_PASSWORD: 'psw-joe',
            NAME_SAVEACCOUNT: False,
        }
        self.assertDictEqual(action, expected_action)

    def test_config_all_with_list(self):
        @as_action(
            DESC_ACTION,
            para_names=[NAME_USERNAME, NAME_PASSWORD, NAME_SAVEACCOUNT],
            para_descriptions=[DESC_USERNAME, DESC_PASSWORD, DESC_SAVEACCOUNT],
        )
        def login_action(username, password, save_account):
            return {}

        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARANAMES), self.action_para_names)
        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARADESC), self.action_para_descriptions)

        action = login_action(username='Joe', password='psw-joe', save_account=True)
        self.assertIn(ACTIONID_NAME, action)

        action.pop(ACTIONID_NAME)
        expected_action = {
            ACTION_NAME: 'login_action',
            NAME_USERNAME: 'Joe',
            NAME_PASSWORD: 'psw-joe',
            NAME_SAVEACCOUNT: True,
        }
        self.assertDictEqual(action, expected_action)

    def test_config_part_with_dict(self):
        @as_action(
            DESC_ACTION,
            para_names={
                'username': NAME_USERNAME,
                'save_account': NAME_SAVEACCOUNT,
            },
            para_descriptions={
                'username': DESC_USERNAME,
                'password': DESC_PASSWORD,
            },
        )
        def login_action(username, password, save_account):
            return {}

        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARANAMES),
            dict(self.action_para_names, password='password'))
        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARADESC),
            dict(self.action_para_descriptions, save_account=NO_DESCRIPTION_MESSAGE))

        action = login_action(username='Joe', password='psw-joe', save_account=True)
        self.assertIn(ACTIONID_NAME, action)

        action.pop(ACTIONID_NAME)
        expected_action = {
            ACTION_NAME: 'login_action',
            NAME_USERNAME: 'Joe',
            'password': 'psw-joe',
            NAME_SAVEACCOUNT: True,
        }
        self.assertDictEqual(action, expected_action)

    def test_config_part_with_list(self):
        @as_action(
            DESC_ACTION,
            para_names=[NAME_USERNAME, NAME_PASSWORD],
            para_descriptions=[DESC_USERNAME],
        )
        def login_action(username, password, save_account):
            return {}

        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARANAMES),
            dict(self.action_para_names, save_account='save_account'))
        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARADESC),
            dict(
                self.action_para_descriptions,
                password=NO_DESCRIPTION_MESSAGE,
                save_account=NO_DESCRIPTION_MESSAGE
            ))

        action = login_action(username='Joe', password='psw-joe', save_account=False)
        self.assertIn(ACTIONID_NAME, action)

        action.pop(ACTIONID_NAME)
        expected_action = {
            ACTION_NAME: 'login_action',
            NAME_USERNAME: 'Joe',
            NAME_PASSWORD: 'psw-joe',
            'save_account': False,
        }
        self.assertDictEqual(action, expected_action)

    def test_action_name(self):
        @as_action('', action_name=NAME_ACTION)
        def login_action(username, password, save_account):
            return {}
        action = login_action('Joe', 'psw-joe', False)

        self.assertTrue(isinstance(action, dict))
        self.assertEqual(action[ACTION_NAME], NAME_ACTION)  # pylint: disable=E1126

        action = login_action(username='Joe', password='psw-joe', save_account=False)
        self.assertIn(ACTIONID_NAME, action)
        self.assertIn(ACTION_NAME, action)
        self.assertEqual(action[ACTION_NAME], NAME_ACTION)

    def test_action_description(self):
        @as_action(DESC_ACTION)
        def login_action(username, password, save_account):
            return {}

        self.assertEqual(login_action.__doc__, DESC_ACTION)


class ImactionDocumentTester(TestCase):
    action_para_names = {
        'username': NAME_USERNAME,
        'password': NAME_PASSWORD,
        'save_account': NAME_SAVEACCOUNT,
    }
    action_para_descriptions = {
        'username': DESC_USERNAME,
        'password': DESC_PASSWORD,
        'save_account': DESC_SAVEACCOUNT,
    }

    def test_config_all(self):
        def login_action(username, password, save_account):
            '''
            @as_action: login with the given username and password

            - username:         #uname  name of user
            - password:         #pswd   password of user
            - save_account:     #save   whether save account information or not
            '''
            return {}
        login_action = metafunc_to_action(login_action)

        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARANAMES), self.action_para_names)
        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARADESC), self.action_para_descriptions)

        action = login_action(username='Rose', password='psw-rose', save_account=False)
        self.assertIn(ACTIONID_NAME, action)

        action.pop(ACTIONID_NAME)
        expected_action = {
            ACTION_NAME: 'login_action',
            NAME_USERNAME: 'Rose',
            NAME_PASSWORD: 'psw-rose',
            NAME_SAVEACCOUNT: False,
        }
        self.assertDictEqual(action, expected_action)

    def test_config_part(self):
        def login_action(username, password, save_account):
            '''
            @as_action: login with the given username and password

            - username:         #uname  name of user
            - password:                 password of user
            - save_account:     #save
            '''
            return {}
        login_action = metafunc_to_action(login_action)

        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARANAMES),
            dict(self.action_para_names, password='password'))
        self.assertDictEqual(
            getattr(login_action, ACTION_ATTR_ACPARADESC),
            dict(self.action_para_descriptions, save_account=NO_DESCRIPTION_MESSAGE))

        action = login_action(username='Rose', password='psw-rose', save_account=True)
        self.assertIn(ACTIONID_NAME, action)

        action.pop(ACTIONID_NAME)
        expected_action = {
            ACTION_NAME: 'login_action',
            NAME_USERNAME: 'Rose',
            'password': 'psw-rose',
            NAME_SAVEACCOUNT: True,
        }
        self.assertDictEqual(action, expected_action)

    def test_action_name(self):
        def login_action(username, password, save_account):
            '''
            @as_action: #signin
            '''
            return {}
        login_action = metafunc_to_action(login_action)
        action = login_action('Joe', 'password of Joe', False)

        self.assertTrue(isinstance(action, dict))
        self.assertEqual(action[ACTION_NAME], NAME_ACTION)  # pylint: disable=E1126

        action = login_action(username='Rose', password='psw-rose', save_account=False)
        self.assertIn(ACTIONID_NAME, action)
        self.assertIn(ACTION_NAME, action)
        self.assertEqual(action[ACTION_NAME], NAME_ACTION)

    def test_action_description(self):
        def login_action(username, password, save_account):
            '''
            @as_action: login with the given username and password
            '''
            return {}
        login_action = metafunc_to_action(login_action)

        self.assertEqual(login_action.__doc__, DESC_ACTION)


def _action_with_no_id(action):
    return {k: v for k, v in action.items() if k != ACTIONID_NAME}


class ModuleDefinationTester(TestCase):
    def setUp(self):
        self.action1 = taction_1(p1='var1')
        self.action2 = taction_2(p1='var1', p2='var2')
        self.action3 = taction_3(p1='var1', p2='var2', p3='var3')
        self.action4 = taction_4(p1='var1', p2='var2', p3='var3', p4='var4')

        self.action1_without_id = _action_with_no_id(self.action1)
        self.action2_without_id = _action_with_no_id(self.action2)
        self.action3_without_id = _action_with_no_id(self.action3)
        self.action4_without_id = _action_with_no_id(self.action4)

    def test_action_namelist(self):
        self.assertItemsEqual(ACTIONS_BEFORE_REGISTRATION, ['taction_1', 'act2', 'taction_3'])
        self.assertItemsEqual(ACTIONS_BEFORE_REGISTRATION, ACTIONS_AFTER_REGISTRATION)

        self.assertItemsEqual(ACTIONS_WITH_NEW_REGISTRATION, ['taction_1', 'act2', 'taction_3', 'act4'])

    def test_action_has_id(self):
        self.assertIn(ACTIONID_NAME, self.action1)
        self.assertIn(ACTIONID_NAME, self.action2)
        self.assertIn(ACTIONID_NAME, self.action3)
        self.assertIn(ACTIONID_NAME, self.action4)

    def test_action_content(self):
        self.assertDictEqual(
            self.action1_without_id, {ACTION_NAME: 'taction_1', 'parameter1': 'var1'})
        self.assertDictEqual(
            self.action2_without_id, {ACTION_NAME: 'act2', 'parameter1': 'var1', 'parameter2': 'var2'})
        self.assertDictEqual(
            self.action3_without_id, {ACTION_NAME: 'taction_3', 'parameter1': 'var1', 'p2': 'var2', 'parameter3': 'var3'})
        self.assertDictEqual(
            self.action4_without_id, {ACTION_NAME: 'act4', 'p1': 'var1', 'p2': 'var2', 'p3': 'var3', 'parameter4': 'var4'})


def taction_1(p1):
    '''
    @as_action:

    - p1:    #parameter1    parameter that named as p1
    '''
    return {}
def taction_2(p1, p2):
    '''
    @as_action: #act2

    - p1:   #parameter1     parameter that named as p1
    - p2:   #parameter2     parameter that named as p2
    '''
    return {}
def taction_3(p1, p2, p3):
    '''
    @as_action:

    - p1:   #parameter1     parameter that named as p1
    - p3:   #parameter3     parameter that named as p3
    '''
    return {}
ACTIONS_BEFORE_REGISTRATION = collect_action_names()


register_actions()
ACTIONS_AFTER_REGISTRATION = collect_action_names()


def taction_4(p1, p2, p3, p4):
    '''
    @as_action:  #act4   this `act4` action is registered after another previous registration.

    - p4:   #parameter4     parameter that named as p4
    '''
    return {}

def taction_5(p1, p2, p3, p4, p5):
    '''
    as_action:  #act5   this is not an action as there is no '@' before `as_action`

    - p1:  #parameter1      parameter that named as p1
    - p5:  #parameter1      parameter that named as p5
    '''
register_actions()
ACTIONS_WITH_NEW_REGISTRATION = collect_action_names()
