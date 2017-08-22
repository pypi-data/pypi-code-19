import datetime

from keyman.entities import Account
from keyman.utils import dt2tstmp


class DBHandler:
    """
    The class handling the database.

    Note that all arguments passed to methods of DBHanlder are thought to be
    valid and will not be checked and modified.

    """

    def __init__(self, conn):
        self.conn = conn

    def insert(self, account):
        """ Insert a new account into the database. """
        sql = r"INSERT INTO ACCOUNT ({keystr}) VALUES ({placeholders})". \
            format(
            keystr=account.keystr(),
            placeholders=('?, ' * len(account.keys))[:-2]
        )

        account.set('id', self._get_free_id())
        account.set('deleted', 0)  # False
        time_now = dt2tstmp(datetime.datetime.now())
        account.set('create_date', time_now)
        account.set('last_update', time_now)

        cursor = self.conn.cursor()
        cursor.execute(sql, account.values())
        n_inserted = cursor.rowcount
        cursor.close()

        self.conn.commit()

        return n_inserted

    def remove(self, id, nontrash=False):
        """
        Remove an account designated by `id`.

        If `nontrash` is True, the account will be removed from the dababase
        completely; otherwise the record will be marked as trash, not shown
        in the search results, and can be recovered by `recover`.

        """
        if not self.check_exist(id):
            # no records to be moved
            return 0

        if nontrash:  # remove completely
            sql = r"DELETE FROM ACCOUNT WHERE id = {id}".format(id=id)
        elif self.check_removed(id):
            return 0
        else:  # mark the record as trash
            sql = (r"UPDATE ACCOUNT SET deleted = 1, last_update = '{time}' "
                   r"WHERE id = {id}").format(
                time=dt2tstmp(datetime.datetime.now()),
                id=id
            )

        cursor = self.conn.cursor()
        cursor.execute(sql)
        n_removed = cursor.rowcount
        cursor.close()

        self.conn.commit()

        return n_removed

    def recover(self, id):
        """ Remove an account designated by `id`. """
        if not self.check_removed(id):
            return 0

        sql = (r"UPDATE ACCOUNT SET deleted = 0, last_update = '{time}' "
               r"WHERE id = {id}").format(
            time=dt2tstmp(datetime.datetime.now()),
            id=id
        )

        cursor = self.conn.cursor()
        cursor.execute(sql)
        n_recovered = cursor.rowcount
        cursor.close()

        self.conn.commit()

        return n_recovered

    def search(self, show_all=False, **conditions):
        """ Search for accounts that satisfy `conditions`. """
        sql = "SELECT * FROM ACCOUNT WHERE {0}".format(
            " AND ".join(
                [k + " LIKE '%" + str(v) + "%'" for k, v in conditions.items()
                 if v is not None]
            )
        )

        if not show_all:
            sql += " AND deleted <> 1"

        # print(sql)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        account_tuples = cursor.fetchall()
        cursor.close()

        accounts = self._sql_results_to_account_objs(account_tuples)
        return accounts

    def list(self, range):
        sql = "SELECT * FROM ACCOUNT"
        if range == "t":  # only return trash records
            sql += " WHERE deleted = 1"
        elif range == "a":  # return all record
            pass
        else:  # only return normal record
            sql += " WHERE deleted <> 1"

        cursor = self.conn.cursor()
        cursor.execute(sql)
        account_tuples = cursor.fetchall()
        cursor.close()

        accounts = self._sql_results_to_account_objs(account_tuples)
        return accounts

    def update(self, id, **new_values):  # id is not in new_values
        if not self.check_normal(id):  # unable to update (nothing changed)
            return 0

        time_now = dt2tstmp(datetime.datetime.now())
        new_values['last_update'] = time_now
        new_values_str = ", ".join(
            [k + ' = "' + v + '"' for k, v in new_values.items()]
        )

        sql = "UPDATE ACCOUNT SET {str} WHERE id = {id}".format(
            str=new_values_str, id=id
        )
        # print(sql)

        cursor = self.conn.cursor()
        cursor.execute(sql)
        n_updated = cursor.rowcount
        cursor.close()

        self.conn.commit()

        return n_updated

    def _get_free_id(self):
        sql = r"SELECT id FROM ACCOUNT"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        ids = cursor.fetchall()

        if ids:
            ids.sort()

            (max_id,) = ids[-1]
            free_id = -1
            # id values starting from 1; the possible maximum value is
            # max_id + 1.
            for i in range(1, max_id + 2):
                if (i,) not in ids:
                    free_id = i
                    break

        else:  # no existing records found
            free_id = 1

        return free_id

    @staticmethod
    def _sql_results_to_account_objs(account_tuples):
        accounts = []
        for a_tuple in account_tuples:
            a_dict = dict(zip(Account.keys, a_tuple))
            accounts.append(Account(**a_dict))

        return accounts

    def check_exist(self, id):
        """
        Check the existence of the account designated by id.

        :param id: int
            ID of the account.
        :return: bool
            If the account exists (including in trash), return True; otherwise,
            return False.

        """
        sql = r"SELECT * FROM ACCOUNT WHERE id = {0}".format(id)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        accounts = cursor.fetchall()

        return bool(len(accounts))

    def check_removed(self, id):
        """
        Check whether the account is removed into trash.

        :param id: int
            ID of the account.
        :return:
            If the account exists and has been moved into trash, return True;
            otherwise return False.

        """
        sql = r"SELECT * FROM ACCOUNT WHERE id = {0} AND deleted = 1".format(id)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        accounts = cursor.fetchall()

        return bool(len(accounts))

    def check_normal(self, id):
        """
        Check whether the account is normal, i.e. exists but was not removed
        into trash.

        :param id: int
            ID of the account.
        :return:
            If the account exists and was not moved into trash, return True;
            otherwise return False.

        """
        sql = r"SELECT * FROM ACCOUNT WHERE id = {0} AND deleted = 0".format(id)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        accounts = cursor.fetchall()

        return bool(len(accounts))
