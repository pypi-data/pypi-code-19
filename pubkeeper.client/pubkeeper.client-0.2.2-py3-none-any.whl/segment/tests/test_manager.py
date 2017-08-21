from unittest import TestCase
from unittest.mock import Mock, patch

from pubkeeper.segment.manager import SegmentManager


class TestSegmentManager(TestCase):

    class MyClient(object):
        def __init__(self, brews):
            self.brews = brews

    """ Asserts segment manager functionality
    """
    def test_segment_manager(self):
        segment_id = "segment_id"
        topic = None
        brewer_details = None
        patron_details = None
        brewer_brew = Mock()
        brewer_brew.name = "A"
        brewer_brew.create_patron = Mock(return_value={"detail1": "value"})
        patron_brew = Mock()
        patron_brew.name = "B"
        client = TestSegmentManager.MyClient({
            brewer_brew.name: brewer_brew,
            patron_brew.name: patron_brew
        })

        # assert incoming arguments are validated against None values
        with self.assertRaises(ValueError):
            SegmentManager.create(
                client, segment_id, topic, brewer_details, patron_details)
        self.assertEqual(len(SegmentManager.segments), 0)

        segment_id = "segment_id"
        patron_brew.create_brewer = Mock(return_value={"detail1": "value"})
        brewer_details = {"topic": "brewer_topic", "brew": {"name": "A"},
                          "brewer_id": "brewer_id"}
        patron_details = {"topic": "patron_topic", "brew_name": "B",
                          "patron_id": "patron_id"}
        topic = "topic"
        brewer_mock = Mock()
        brewer_mock.new_patron = Mock()
        brewer_mock.remove_patron = Mock()
        patron_mock = Mock()
        patron_mock.new_brewer = Mock()
        patron_mock.remove_brewer = Mock()
        with patch(SegmentManager.__module__ + ".Brewer") as mocked_brewer:
            with patch(SegmentManager.__module__ + ".Patron") as mocked_patron:
                mocked_brewer.return_value = brewer_mock
                mocked_patron.return_value = patron_mock
                SegmentManager.create(
                    client, segment_id, topic, brewer_details, patron_details)
                self.assertEqual(len(SegmentManager.segments), 1)

                # an attempt to create same segment is ignored
                SegmentManager.create(
                    client, segment_id, topic, brewer_details, patron_details)
                self.assertEqual(len(SegmentManager.segments), 1)

                # assert brewer and patron link to original patron and brewer
                # respectively
                # brewer_mock.new_patron.assert_called_with(
                #     patron_details["patron_id"], patron_details["brew"])
                patron_mock.new_brewer.assert_called_with(
                    topic,
                    brewer_details["brewer_id"],
                    None,
                    brewer_details["brew"])

                # assert internal brews were setup
                brewer_brew.create_patron.assert_called_with(patron_mock)
                patron_brew.create_brewer.assert_called_with(brewer_mock)

                # simulate connecting the brewer
                with self.assertRaises(ValueError):
                    SegmentManager.connect_brewer("invalid segment id",
                                                  "patron_id",
                                                  Mock())

                segment_info = SegmentManager.segments[segment_id]
                SegmentManager.connect_brewer(segment_id,
                                              segment_info.patron.patron_id,
                                              Mock())

                # causes no effect trying to destroy an invalid segment
                SegmentManager.destroy("invalid_segment_id")
                self.assertEqual(len(SegmentManager.segments), 1)
                segment_id = list(SegmentManager.segments.keys())[0]

                # destroy segment
                SegmentManager.destroy(segment_id)
                self.assertEqual(len(SegmentManager.segments), 0)

                # assert removal/destroys
                brewer_mock.remove_patron.assert_called_with("patron_id")
                patron_mock.remove_brewer.assert_called_with("brewer_id")

                brewer_brew.destroy_patron.assert_called_with(patron_mock)
                patron_brew.destroy_brewer.assert_called_with(brewer_mock)

    def test_manager_reset(self):
        segment_id = 1
        segment = Mock()
        with patch.object(SegmentManager, "destroy") as destroy_patch:
            with patch.object(SegmentManager, "_segments",
                              new={segment_id: segment}):
                self.assertEqual(len(SegmentManager._segments), 1)
                SegmentManager.reset()
                destroy_patch.assert_called_with(segment_id)
                self.assertEqual(len(SegmentManager._segments), 0)
