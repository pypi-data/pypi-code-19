# from behave import *
# from mock import MagicMock, patch
# import numpy as np
# from lib import descriptors
# #from lib.descriptors import _inputfasta
# from lib.analysis import *
#
# use_step_matcher("parse")
#
# @given(u'a fasta file with equal counts of all amino acids.')
# def step_impl(context):
#
#     fasta_parser = _inputfasta()
#     fasta_parser.setinputformat("FASTA")
#
#     context.generator = fasta_parser.fastasequencegenerator(context.text.split("\n"))
#
#
# @when(u'running ncomposition with all defaults (kmer length is 1 and standard fasta format.).')
# def step_impl(context):
#     with patch.object(_inputfasta, 'generatefastaobjects') as mock_method:
#         mock_method.return_value = context.generator
#         descriptors.ncomposition(context.parser)
#     assert mock_method.called
#
#
#
# @then(u'there should be a {:d} element vector with each element equaling {}.')
# def step_impl(context, number, val):
#     #assert context.stdout_capture.getvalue().count(value) == times
#     #print(context.stdout_capture.getvalue())
#     row = context.stdout_capture.getvalue()
#     assert len(row.split()) == number, len(row.split())
#     assert set(row.split()) == set([val])
