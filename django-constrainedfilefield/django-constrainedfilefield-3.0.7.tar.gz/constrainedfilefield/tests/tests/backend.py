# -*- coding: utf-8 -*-
import os.path

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from constrainedfilefield.tests.forms import TestModelForm, TestModelFormJs, TestModelNoValidateForm, TestElementForm, \
    TestNoModelForm, TestNoModelJsForm
from constrainedfilefield.tests.models import TestModel, TestContainer


class ConstrainedFileFieldTest(TestCase):
    SAMPLE_FILES_PATH = os.path.join(settings.BASE_DIR, 'sample_files')

    def test_create_empty_instance(self):
        TestModel.objects.create()

    def test_create_instance_with_file(self):
        instance = TestModel.objects.create(
            the_file=File(self._get_sample_file('image2k.png'), 'the_file.png')
        )

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()

    def test_form_ok(self):
        form = self._create_bound_test_model_form(form_class=TestModelForm,
                                                  orig_filename='image2k.png',
                                                  dest_filename='the_file.png',
                                                  content_type='image/png')
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()

    def test_form_js_ok(self):
        form = self._create_bound_test_model_form(form_class=TestModelFormJs,
                                                  orig_filename='image2k.png',
                                                  dest_filename='the_file.png',
                                                  content_type='image/png')
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.png')

        instance.the_file.delete()
        instance.delete()

    def test_form_invalid_size(self):
        form = self._create_bound_test_model_form(form_class=TestModelForm,
                                                  orig_filename='image15k.png',
                                                  dest_filename='the_file.png',
                                                  content_type='image/png')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0],
                         u"File size exceeds limit: 14.2 KB. Limit is 10.0 KB.")

    def test_form_invalid_filetype(self):
        form = self._create_bound_test_model_form(form_class=TestModelForm,
                                                  orig_filename='document1k.pdf',
                                                  dest_filename='the_file.pdf',
                                                  content_type='application/pdf')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0],
                         u"Unsupported file type: application/pdf. "
                         u"Allowed types are ['image/png'].")

    def test_form_invalid_filetype_and_size(self):
        form = self._create_bound_test_model_form(form_class=TestModelForm,
                                                  orig_filename='document15k.pdf',
                                                  dest_filename='the_file.pdf',
                                                  content_type='application/pdf')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0],
                         u"File size exceeds limit: 14.9 KB. Limit is 10.0 KB.")

    def test_form_fake_filetype(self):
        form = self._create_bound_test_model_form(form_class=TestModelForm,
                                                  orig_filename='document1k.pdf',
                                                  dest_filename='the_file.pdf',
                                                  content_type='image/png')
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(len(form.errors['the_file']), 1)
        self.assertEqual(form.errors['the_file'][0],
                         u"Unsupported file type: application/pdf. "
                         u"Allowed types are ['image/png'].")

    def test_form_no_validate(self):
        form = self._create_bound_test_model_form(form_class=TestModelNoValidateForm,
                                                  orig_filename='document15k.pdf',
                                                  dest_filename='the_file.pdf',
                                                  content_type='application/pdf')
        self.assertTrue(form.is_valid())
        instance = form.save()

        self._check_file_url(instance.the_file, 'the_file.pdf')

        instance.the_file.delete()
        instance.delete()

    def test_form_null_file(self):
        form = self._create_bound_test_model_form(form_class=TestModelNoValidateForm)
        self.assertTrue(form.is_valid())
        instance = form.save()

        self.assertEqual(instance.the_file, None)

        instance.delete()

    def test_nomodel_form_ok(self):
        form = self._create_bound_test_model_form(form_class=TestNoModelForm,
                                                  orig_filename='image2k.png',
                                                  dest_filename='the_file.png',
                                                  content_type='image/png')
        self.assertTrue(form.is_valid())

        for uploaded_file in form.files.values():
            uploaded_file.close()

    def test_nomodel_form_js_ok(self):
        form = self._create_bound_test_model_form(form_class=TestNoModelJsForm,
                                                  orig_filename='image2k.png',
                                                  dest_filename='the_file.png',
                                                  content_type='image/png')
        self.assertTrue(form.is_valid())

        for uploaded_file in form.files.values():
            uploaded_file.close()

    # -------
    # Utilities

    def _get_sample_file(self, filename):
        path = os.path.join(self.SAMPLE_FILES_PATH, filename)
        return open(path, mode='rb')

    def _check_file_url(self, filefield, filename):
        url = os.path.join(settings.MEDIA_URL, filefield.field.upload_to, filename)
        self.assertEqual(filefield.url, url)

    def _create_bound_test_model_form(self, form_class, orig_filename=None,
                                      dest_filename=None, content_type=None):
        if orig_filename and dest_filename and content_type:
            uploaded_file = SimpleUploadedFile(
                name=dest_filename,
                content=self._get_sample_file(orig_filename).read(),
                content_type=content_type,
            )
            files = {'the_file': uploaded_file}
        else:
            files = {}
        form = form_class(data={}, files=files)
        return form

    def _create_container(self, name):
        return TestContainer.objects.create(name=name)

    def _add_element(self, container, orig_filename, dest_filename):
        return container.test_elements.create(
            the_file=File(self._get_sample_file(orig_filename), dest_filename)
        )

    def _create_unbound_test_element_form(self, container):
        return TestElementForm(container=container)

    def _create_bound_test_element_form(self, container, orig_filename=None,
                                        dest_filename=None, content_type=None):
        if orig_filename and dest_filename and content_type:
            uploaded_file = SimpleUploadedFile(
                name=dest_filename,
                content=self._get_sample_file(orig_filename).read(),
                content_type=content_type,
            )
            files = {'the_file': uploaded_file}
        else:
            files = {}
        form = TestElementForm(container=container, data={}, files=files)
        return form
