from setuptools import setup
setup(
  name = 'ambari-ldap-manager',
  packages = ['ambari-ldap-manager'], # this must be the same as the name above
  version = '0.1',
  description = 'A tool to manage Ambari users and groups when authentication uses LDAP.',
  author = 'James Barney',
  author_email = 'jamesbarney71@gmail.com',
  url = 'https://github.com/Barneyjm/ambari-ldap-manager',
  download_url = 'https://github.com/Barneyjm/ambari-ldap-manager/archive/0.1.tar.gz',
  keywords = ['hadoop', 'ldap', 'active-directory', 'ambari', 'manager'],
  install_requires=[
          'requests',
          'flask'
      ],
  classifiers = []
)