from unittest import TestCase

from mock import patch
from django.http import Http404
from django.test import RequestFactory

from regulations.generator.node_types import INTERP
from regulations.views import partial_interp


class PartialInterpViewTest(TestCase):
    @patch('regulations.views.partial.generator')
    def test_get_context_data(self, generator):
        generator.get_tree_paragraph.return_value = {
            'text': 'Some Text',
            'children': [],
            'label': ['867', '53', 'q', 'Interp'],
            'node_type': INTERP
        }
        request = RequestFactory().get('/fake-path')
        view = partial_interp.PartialInterpView.as_view(layers=[])
        response = view(request, label_id='lablab', version='verver')
        self.assertEqual(response.context_data['c']['node_type'], INTERP)
        self.assertEqual(response.context_data['c']['children'],
                         [generator.get_tree_paragraph.return_value])
        self.assertFalse(response.context_data['inline'])

        view = partial_interp.PartialInterpView.as_view(
            inline=True, layers=[])
        response = view(request, label_id='lablab', version='verver')
        self.assertEqual(response.context_data['c']['node_type'], INTERP)
        self.assertEqual(response.context_data['c']['children'],
                         [generator.get_tree_paragraph.return_value])
        self.assertTrue(response.context_data['inline'])


class PartialSubterpViewTest(TestCase):
    @patch('regulations.views.partial.generator')
    @patch('regulations.views.partial_interp.generator')
    @patch('regulations.views.partial_interp.filter_by_subterp')
    @patch('regulations.views.partial_interp.CFRHTMLBuilder')
    @patch('regulations.views.partial.navigation')
    def test_get_context_data(self, nav, CFRHTMLBuilder, filter_by_subterp,
                              interp_generator, partial_generator):
        partial_generator.layers.return_value = []
        interp_generator.get_tree_paragraph.return_value = None
        nav.nav_sections.return_value = None, None

        request = RequestFactory().get('/fake-path')
        view = partial_interp.PartialSubterpView.as_view()
        try:
            view(request, label_id='lablab', version='verver')
            self.assertTrue(False)
        except Http404:
            pass

        interp_generator.get_tree_paragraph.return_value = {'children': []}
        filter_by_subterp.return_value = []
        view = partial_interp.PartialSubterpView.as_view()
        try:
            view(request, label_id='lablab', version='verver')
            self.assertTrue(False)
        except Http404:
            pass

        filter_by_subterp.return_value = ['sec1', 'sec2', 'sec3']
        view(request, label_id='lablab', version='verver')
        self.assertEqual(
            CFRHTMLBuilder.return_value.tree,
            {'children': ['sec1', 'sec2', 'sec3'],
             'html_label': ['lablab'],
             'label': ['lablab']})
