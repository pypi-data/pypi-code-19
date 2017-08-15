from pyedu.app import app_factory
from flask_script import Manager
from flask_migrate import MigrateCommand, upgrade
from pyedu.models import db, Role, User
import json, os

# build the script Manager
manager = Manager(app_factory)
manager.add_option('-c', '--config', dest='config_name', default='default', help='specifiy the app configuration')
manager.add_command('db', MigrateCommand)


@manager.option('--drop', dest='drop', default=False, action='store_true', help='Drop the database.')
@manager.option('-S', '--superuser', dest='set_superuser', default=False,
                action='store_true', help='Set a (new) superuser')
def deploy(drop=False, set_superuser=False):
    """
    Install the database with or without dropping the old instance.

    :param drop:
    :return:
    """

    if drop:
        print('Dropping database.')
        db.drop_all()
    print('Creating database at %s' % str(db.session.bind.url))
    upgrade()

    # populate
    print('Populating Roles.')
    try:
        Role.insert_default_roles()
        if set_superuser:
            User.insert_default_users(superuser_mail=input('superuser mail: '), superuser_password=input('superuser password: '))
    except Exception as e:
        db.session.rollback()
        print('Error occured: %s\n Rollback.' % str(e))
    finally:
        print('Done.')


@manager.option('-f', '--file', dest='filepath', default=os.path.join(os.path.expanduser('~'), 'pyedu_users.json'),
                help='Specify the user JSON file')
def import_users(filepath=os.path.join(os.path.expanduser('~'), 'pyedu_users.json')):
    """
    Import user from a JSON file (defualt at ~/pyedu_users.json)
    """
    # get the roles
    r_teach = Role.query.filter_by(name='teacher').first()
    r_stud = Role.query.filter_by(name='student').first()

    with open(filepath) as userfile:
        users = json.loads(userfile.read())
    print('Found user file at: %s, importing %d users...' % (filepath, len(users)))

    for user in users:
        try:
            user['role'] = r_teach if user.get('role') == 'teacher' else r_stud
            user.setdefault('confirmed', True)

            # add to session
            db.session.add(
                User(**user)
            )
            db.session.commit()
            print('Added user:\n%s' % str(user))
        except Exception as e:
            db.session.rollback()
            print('Could not load user:\n%s\nMessage: %s' % (str(user), str(e)))
        print('Done.')

if __name__ == '__main__':
    manager.run()
