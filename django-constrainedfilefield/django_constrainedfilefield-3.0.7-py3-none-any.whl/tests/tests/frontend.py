import os.path

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client


class ConstrainedFileFieldTest(StaticLiveServerTestCase):
    SAMPLE_FILES_PATH = os.path.join(settings.BASE_DIR, 'sample_files')

    def test_nomodel_form_js_view_ok(self):
        c = Client()
        response = c.get('/nomodel/')
        # FIXME: validate response content: form is included as expected
        assert response.status_code == 200
        from django.contrib.staticfiles import finders
        self.assertIsNotNone(finders.find('constrainedfilefield/js/file_checker.js'))
