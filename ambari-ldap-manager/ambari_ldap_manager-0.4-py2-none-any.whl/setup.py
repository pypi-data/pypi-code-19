from setuptools import setup
setup(
  name = 'ambari-ldap-manager',
  packages = ['ambari-ldap-manager'], # this must be the same as the name above
  version = '0.4',
  description = 'A tool to manage Ambari users and groups when authentication uses LDAP.',
  author = 'James Barney',
  author_email = 'jamesbarney71@gmail.com',
  url = 'https://github.com/Barneyjm/ambari-ldap-manager',
  download_url = 'https://github.com/Barneyjm/ambari-ldap-manager/archive/0.4.tar.gz',
  keywords = ['hadoop', 'ldap', 'active-directory', 'ambari', 'manager'],
  entry_points={
          'console_scripts': [
              'ambari-ldap-manager = ldap_management_server:main'
          ]
      },
  install_requires=[
          'requests',
          'flask'
      ],
  classifiers = []
)