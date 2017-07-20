# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-seda unit tests for hooks"""

from itertools import chain, repeat

from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_seda import testutils


class ValidationHooksTC(CubicWebTC):

    assertValidationError = testutils.assertValidationError

    def test_ref_non_rule_constraints(self):
        with self.admin_access.cnx() as cnx:
            create = cnx.create_entity

            access_scheme = create('ConceptScheme', title=u'access')
            access_concept = access_scheme.add_concept(label=u'anyone')
            reuse_scheme = create('ConceptScheme', title=u'reuse')
            reuse_concept = reuse_scheme.add_concept(label=u'share-alike')
            cnx.commit()

            bdo = testutils.create_transfer_to_bdo(cnx)
            transfer = bdo.container[0]
            create('SEDAAccessRuleCodeListVersion',
                   seda_access_rule_code_list_version_from=transfer,
                   seda_access_rule_code_list_version_to=access_scheme)
            create('SEDAReuseRuleCodeListVersion',
                   seda_reuse_rule_code_list_version_from=transfer,
                   seda_reuse_rule_code_list_version_to=reuse_scheme)
            cnx.commit()

            rule_base = create('SEDAAccessRule', seda_access_rule=transfer)
            rule_alt = create('SEDAAltAccessRulePreventInheritance',
                              reverse_seda_alt_access_rule_prevent_inheritance=rule_base)
            non_rule = create('SEDARefNonRuleId', seda_ref_non_rule_id_from=rule_alt)
            cnx.commit()

            with self.assertValidationError(cnx) as cm:
                non_rule.cw_set(seda_ref_non_rule_id_to=reuse_concept)
            self.assertIn('seda_ref_non_rule_id_to-subject', cm.exception.errors)

            non_rule.cw_set(seda_ref_non_rule_id_to=access_concept)
            cnx.commit()

    def test_empty_choice_created(self):
        """Check that a ValidationError is raised when an empty SEDAAlt... entity is created."""
        with self.admin_access.cnx() as cnx:
            # Create an empty SEDAAltAccessRulePreventInheritance
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            with self.assertValidationError(cnx) as cm:
                cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                  reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            self.assertIn('An alternative cannot be empty',
                          str(cm.exception))

    def test_valid_choice_created(self):
        """Check that everything goes fine when a valid SEDAAlt... entity is created."""
        with self.admin_access.cnx() as cnx:
            # Create an empty SEDAArchiveUnit
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            choice = cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                       reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            cnx.create_entity('SEDAPreventInheritance', prevent_inheritance=False,
                              seda_prevent_inheritance=choice)
            cnx.commit()

    def test_last_item_in_choice_deleted(self):
        """Check that a ValidationError is raised when the last relation from a SEDAAlt... entity
        is deleted.
        """
        with self.admin_access.cnx() as cnx:
            # Create a valid SEDAAltAccessRulePreventInheritance
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            choice = cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                       reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            rel = cnx.create_entity('SEDAPreventInheritance', prevent_inheritance=False,
                                    seda_prevent_inheritance=choice)
            cnx.commit()
            # Delete SEDAPreventInheritance
            with self.assertValidationError(cnx) as cm:
                cnx.execute('DELETE SEDAPreventInheritance X WHERE X eid %(rel_eid)s',
                            {'rel_eid': rel.eid})
            self.assertIn('An alternative cannot be empty',
                          str(cm.exception))

    def test_item_in_choice_deleted_with_remaining_item(self):
        """Check that everything goes fine when the a relation from a SEDAAlt... entity
        is deleted but another relation remains.
        """
        with self.admin_access.cnx() as cnx:
            # Create a valid SEDAAltAccessRulePreventInheritance with two items
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=transfer)
            choice = cnx.create_entity('SEDAAltAccessRulePreventInheritance',
                                       reverse_seda_alt_access_rule_prevent_inheritance=access_rule)
            rel = cnx.create_entity('SEDAPreventInheritance', prevent_inheritance=False,
                                    seda_prevent_inheritance=choice)
            cnx.create_entity('SEDARefNonRuleId', seda_ref_non_rule_id_from=choice)
            cnx.commit()
            # Delete SEDAPreventInheritance
            cnx.execute('DELETE SEDAPreventInheritance X WHERE X eid %(rel_eid)s',
                        {'rel_eid': rel.eid})
            cnx.commit()


class SetDefaultHooksTC(CubicWebTC):

    def test_default_code_list_version(self):
        with self.admin_access.cnx() as cnx:
            for rtype, etype in chain(zip(('seda_format_id_to', 'seda_mime_type_to',
                                           'seda_encoding_to'),
                                          repeat(None)),
                                      [('seda_algorithm', 'SEDABinaryDataObject'),
                                       ('seda_rule', 'SEDASeqAppraisalRuleRule'),
                                       ('seda_rule', 'SEDASeqAccessRuleRule'),
                                       ('seda_rule', 'SEDASeqDisseminationRuleRule')]):
                testutils.scheme_for_type(cnx, rtype, etype)
            cnx.commit()
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            cnx.commit()

            self.assertTrue(transfer.reverse_seda_file_format_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_message_digest_algorithm_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_mime_type_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_encoding_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_access_rule_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_appraisal_rule_code_list_version_from)
            self.assertTrue(transfer.reverse_seda_dissemination_rule_code_list_version_from)

    def test_default_card_on_typed_data_object_ref(self):
        """When creating a SEDADataObjectReference in the context of a reference, its cardinality
        should always be 1 (by default any card is allowed since in may be used in the context of
        'main' reference).
        """
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            version_of = cnx.create_entity('SEDAIsVersionOf', seda_is_version_of=unit_alt_seq)
            alt2 = cnx.create_entity('SEDAAltIsVersionOfArchiveUnitRefId',
                                     reverse_seda_alt_is_version_of_archive_unit_ref_id=version_of)
            do_ref = cnx.create_entity('SEDADataObjectReference', seda_data_object_reference=alt2)
            cnx.commit()

            self.assertEqual(do_ref.user_cardinality, '1')

    def test_simplified_profile_do_ref_sync(self):
        """When creating a SEDABinaryDataObject in a simplified profile from the ui, one only
        specifies user_cardinality for it, not for it's associated reference whose cardinality
        should have the same value.
        """
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'test profile',
                                         simplified_profile=True)
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            bdo = testutils.create_data_object(unit_alt_seq, user_cardinality=u'1',
                                               seda_binary_data_object=transfer)
            cnx.commit()
            ref = cnx.find('SEDADataObjectReference').one()

            ref.cw_clear_all_caches()
            self.assertEqual(ref.user_cardinality, '1')

            bdo.cw_set(user_cardinality=u'1..n')
            cnx.commit()
            ref.cw_clear_all_caches()
            self.assertEqual(ref.user_cardinality, '1..n')


class CheckProfileTC(CubicWebTC):

    assertValidationError = testutils.assertValidationError

    def test_base(self):
        with self.admin_access.cnx() as cnx:
            transfer = cnx.create_entity('SEDAArchiveTransfer', title=u'diagnosis testing')
            unit, unit_alt, unit_alt_seq = testutils.create_archive_unit(transfer)
            access_rule = cnx.create_entity('SEDAAccessRule', seda_access_rule=unit_alt_seq)
            cnx.commit()

            with self.assertValidationError(cnx):
                transfer.cw_set(simplified_profile=True)

            access_rule_seq = cnx.create_entity('SEDASeqAccessRuleRule',
                                                reverse_seda_seq_access_rule_rule=access_rule)
            start_date = cnx.create_entity('SEDAStartDate',
                                           seda_start_date=access_rule_seq)
            transfer.cw_set(simplified_profile=True)
            cnx.commit()

            with self.assertValidationError(cnx):
                start_date.cw_set(user_cardinality=u'0..1')

            with self.assertValidationError(cnx):
                access_rule_seq.cw_delete()


if __name__ == '__main__':
    import unittest
    unittest.main()
