from __future__ import print_function

import tempfile
import os

import mock

# These are the tests from the pagure/ git repo.
# Run with:
# PYTHONPATH=.:/path/to/pagure/checkout nosetests dist_git_auth_tests.py
import pagure
import tests

import dist_git_auth


expected = """
repo test
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/test
  RWC = pingou

repo test2
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/test2
  RWC = pingou

repo somenamespace/test3
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/somenamespace/test3
  RWC = pingou

# end of body
"""


class DistGitoliteAuthTestCase(tests.Modeltests):
    """ Test generating the gitolite configuration file for dist-git. """

    maxDiff = None

    def setUp(self):
        """ Set up the environment in which to run the tests. """
        super(DistGitoliteAuthTestCase, self).setUp()
        self.configfile = tempfile.mkstemp()[1]

    def tearDown(self):
        """ Tear down the environment in which the tests ran. """
        try:
            os.remove(self.configfile)
        except:
            print("Couldn't remove %r" % self.configfile)
            pass
        super(DistGitoliteAuthTestCase, self).tearDown()

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls(self, get_supported_branches):
        """ Test generating the entire gitolite configuration file
        (project == -1).

        """
        get_supported_branches.return_value = ['master', 'f9000']
        print("Initializing DB.")
        tests.create_projects(self.session)

        print("Generating %r" % self.configfile)
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=-1)

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()
        self.assertMultiLineEqual(contents.strip(), expected.strip())

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls_none_project(self, get_supported_branches):
        """ Test not touching the gitolite configuration file
        (project == None).

        """
        get_supported_branches.return_value = ['master', 'f9000']
        print("Initializing DB.")
        tests.create_projects(self.session)

        print("Generating %r" % self.configfile)
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=None)

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()
        self.assertMultiLineEqual(contents.strip(), '')

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls_test_project(self, get_supported_branches):
        """ Test updating the gitolite configuration file for just one
        project (project == a pagure.lib.model.Project).

        """

        get_supported_branches.return_value = ['master', 'f9000']
        self.test_write_gitolite_acls()

        print("Modifying the test project so the output differs.")
        project = pagure.lib._get_project(self.session, 'test')
        project.user_id = 2
        self.session.add(project)
        self.session.commit()

        project = pagure.lib._get_project(self.session, 'test')
        msg = pagure.lib.add_user_to_project(
            self.session,
            project=project,
            new_user='pingou',
            user='foo',
            access='commit'
        )
        self.assertEqual(msg, 'User added')
        self.session.commit()

        print("Rewriting %r" % self.configfile)
        project = pagure.lib._get_project(self.session, 'test')
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=project
        )

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()

        expected = '''repo test2
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/test2
  RWC = pingou

repo somenamespace/test3
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/somenamespace/test3
  RWC = pingou

repo test
  R   = @all
  RWC master = foo pingou
  RWC f9000 = foo pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = foo pingou

repo requests/test
  RWC = foo pingou

# end of body'''
        self.assertMultiLineEqual(expected, contents.strip())

    def test_get_supported_branches(self):
        """ Test for real what is returned by PDC. """
        expected = ['master', 'f27', 'f26', 'f25', 'el6']
        actual = dist_git_auth.get_supported_branches('rpms', 'nethack')
        self.assertEquals(set(actual), set(expected))

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls_test_project_w_group(
            self, get_supported_branches):
        """ Test updating the gitolite configuration file for just one
        project (project == a pagure.lib.model.Project).

        """

        get_supported_branches.return_value = ['master', 'f9000']
        self.test_write_gitolite_acls()

        print("Modifying the test project so the output differs.")
        project = pagure.lib._get_project(self.session, 'test')
        project.user_id = 2
        self.session.add(project)
        self.session.commit()

        # Add a group to a project and someone to this group
        project = pagure.lib._get_project(self.session, 'test')
        msg = pagure.lib.add_group_to_project(
            session=self.session,
            project=project,
            new_group='test_grp',
            user='pingou',
            access='admin',
            create=True,
            is_admin=True)
        self.assertEqual(msg, 'Group added')
        grp = pagure.lib.search_groups(self.session, group_name='test_grp')
        msg = pagure.lib.add_user_to_group(
            session=self.session,
            username='pingou',
            group=grp,
            user='pingou',
            is_admin=False)
        self.session.commit()

        print("Rewriting %r" % self.configfile)
        project = pagure.lib._get_project(self.session, 'test')
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=project
        )

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()

        expected = '''@test_grp  = pingou
# end of groups

repo test2
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/test2
  RWC = pingou

repo somenamespace/test3
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/somenamespace/test3
  RWC = pingou

repo test
  R   = @all
  RWC master = foo
  RWC f9000 = foo
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @test_grp @provenpackager
  RWC = foo

repo requests/test
  RWC = @test_grp
  RWC = foo

# end of body'''
        self.assertMultiLineEqual(expected, contents.strip())

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls_fork(
            self, get_supported_branches):
        """ Test updating the gitolite configuration file when forking a
        project.

        """

        get_supported_branches.return_value = ['master', 'f9000']
        self.test_write_gitolite_acls()

        print("Forking the test project.")
        project = pagure.lib._get_project(self.session, 'test')
        pagure.lib.fork_project(
            session=self.session,
            user='pingou',
            repo=project,
            gitfolder=self.path,
            docfolder=None,
            ticketfolder=None,
            requestfolder=None)

        print("Rewriting %r" % self.configfile)
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=-1
        )

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()

        expected = '''repo test
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/test
  RWC = pingou

repo test2
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/test2
  RWC = pingou

repo somenamespace/test3
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/somenamespace/test3
  RWC = pingou

repo forks/pingou/test
  R   = @all
  RW+C = pingou

repo requests/forks/pingou/test
  RW+C = pingou

# end of body'''
        self.assertMultiLineEqual(expected, contents.strip())

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls_rpms_firefox(self, get_supported_branches):
        """ Test generating the entire gitolite configuration file
        with the firefox project in the rpms namespace (ie a project not
        allowing provenpackager access).

        """
        get_supported_branches.return_value = ['master', 'f9000']
        print("Initializing DB.")
        item = pagure.lib.model.Project(
            user_id=1,  # pingou
            name='firefox',
            description='The firefox project',
            hook_token='aaabbbeee',
            namespace='rpms',
        )
        self.session.add(item)
        self.session.commit()

        print("Generating %r" % self.configfile)
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=-1)

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()
        expected = """repo rpms/firefox
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = pingou

repo requests/rpms/firefox
  RWC = pingou

# end of body
"""
        self.assertMultiLineEqual(contents.strip(), expected.strip())

    @mock.patch('dist_git_auth.get_supported_branches')
    def test_write_gitolite_acls_firefox(self, get_supported_branches):
        """ Test generating the entire gitolite configuration file
        with the firefox project.

        """
        get_supported_branches.return_value = ['master', 'f9000']
        print("Initializing DB.")
        item = pagure.lib.model.Project(
            user_id=1,  # pingou
            name='firefox',
            description='The firefox project',
            hook_token='aaabbbeee',
            namespace=None,
        )
        self.session.add(item)
        self.session.commit()

        print("Generating %r" % self.configfile)
        dist_git_auth.DistGitoliteAuth.write_gitolite_acls(
            self.session,
            configfile=self.configfile,
            project=-1)

        print("Checking the contents of %r" % self.configfile)
        with open(self.configfile, 'r') as f:
            contents = f.read()
        expected = """repo firefox
  R   = @all
  RWC master = pingou
  RWC f9000 = pingou
  -    f[0-9][0-9] = @all
  -    epel[0-9] = @all
  -    epel[0-9][0-9] = @all
  -    el[0-9] = @all
  -    olpc[0-9] = @all
  RWC = @provenpackager
  RWC = pingou

repo requests/firefox
  RWC = pingou

# end of body
"""
        self.assertMultiLineEqual(contents.strip(), expected.strip())
