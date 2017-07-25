from fabric.context_managers import settings, lcd
from fabric.operations import local


def prepare_database(root_password, user, password, database, hosts):
    with settings(warn_only=True):
        if not local('mysqlshow -u%s -p%s %s' % (user, password, database)).succeeded:
            local('mysql -uroot -p%s -e "CREATE DATABASE \\`%s\\` DEFAULT CHARACTER SET utf8;"' % (root_password, database))

            for host in hosts:
                local('mysql -uroot -p%s -e "GRANT ALL PRIVILEGES ON %s.* TO %s@\'%s\' IDENTIFIED BY \'%s\' WITH GRANT OPTION";' % (root_password, database, user, host, password))