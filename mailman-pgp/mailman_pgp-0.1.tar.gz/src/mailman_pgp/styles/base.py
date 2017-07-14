# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

""""""
from lazr.config import as_boolean
from public import public

from mailman_pgp.config import config, mm_config
from mailman_pgp.database import transaction
from mailman_pgp.model.list import PGPMailingList


@public
class PGPStyle:
    def apply(self, mailing_list):
        """Creates the encrypted mailing list instance for the list it's
        applied to.
        """
        mailing_list.posting_chain = 'pgp-posting-chain'

        old_policy = mailing_list.subscription_policy.name
        new_policy_name = 'pgp-' + old_policy[4:]
        if new_policy_name in mm_config.workflows:
            mailing_list.subscription_policy = new_policy_name

        pgp_list = PGPMailingList.for_list(mailing_list)
        if pgp_list:
            return

        generate = as_boolean(config.get('keypairs', 'autogenerate'))

        with transaction() as session:
            pgp_list = PGPMailingList(mailing_list)
            if generate:
                pgp_list.generate_key()
            session.add(pgp_list)
