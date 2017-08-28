# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, C does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Tests for generation of identifiers."""

from __future__ import absolute_import, print_function

from itertools import islice

import pytest
from invenio_sequencegenerator.api import Sequence, Template
from invenio_sequencegenerator.errors import InvalidResetCall, \
    InvalidTemplate, SequenceNotFound
from invenio_sequencegenerator.models import Counter, TemplateDefinition
from invenio_sequencegenerator.utils import double_counter


def test_cern_articles(db):
    """Test CERN articles use-case."""
    with pytest.raises(SequenceNotFound):
        Sequence('ART')

    articles = Template.create('ART', 'CERN-ARTICLE-{category}-{counter}')
    journals = Sequence(articles, category='JOURNALS')
    theses = Sequence(articles, category='THESES')

    assert journals.next() == 'CERN-ARTICLE-JOURNALS-0'
    assert journals.next() == 'CERN-ARTICLE-JOURNALS-1'
    assert journals.next() == 'CERN-ARTICLE-JOURNALS-2'
    assert theses.next() == 'CERN-ARTICLE-THESES-0'
    assert theses.next() == 'CERN-ARTICLE-THESES-1'
    assert journals.next() == 'CERN-ARTICLE-JOURNALS-3'
    assert theses.next() == 'CERN-ARTICLE-THESES-2'


def test_inspire_authors(db):
    """Test INSPIRE authors use-case."""
    auth = Template.create('AUTH', '{author}.{counter}')
    john = Sequence(auth, author='John.Tester')
    tom = Sequence(auth, author='Tom.Phake')

    assert john.next() == 'John.Tester.0'
    assert john.next() == 'John.Tester.1'
    assert john.next() == 'John.Tester.2'
    assert tom.next() == 'Tom.Phake.0'
    assert tom.next() == 'Tom.Phake.1'
    assert john.next() == 'John.Tester.3'
    assert tom.next() == 'Tom.Phake.2'
    assert tom.next() == 'Tom.Phake.3'


def test_cern_playlists(db):
    """Test CERN playlists use-case."""

    pl = Template.create('PL', 'C-{year}-{counter}')
    fl = Template.create('FL', '{PL}:{counter}')
    pl15 = Sequence(pl, year=2015)
    pl16 = Sequence(pl, year=2016)

    assert pl15.next() == 'C-2015-0'
    assert pl15.next() == 'C-2015-1'
    assert pl15.next() == 'C-2015-2'
    assert pl16.next() == 'C-2016-0'

    fl_15_2 = Sequence(fl, PL='C-2015-1')
    fl_16_1 = Sequence(fl, PL='C-2016-0')
    assert fl_15_2.next() == 'C-2015-1:0'
    assert fl_15_2.next() == 'C-2015-1:1'
    assert fl_15_2.next() == 'C-2015-1:2'
    assert fl_16_1.next() == 'C-2016-0:0'


def test_get(db):
    """Test get sequence."""
    Template.create('A', 'A-{counter}')
    Template.create('B', 'B-{counter}')

    assert Sequence('A')
    assert Sequence('A').next() == 'A-0'
    assert Sequence('A').next() == 'A-1'

    assert Sequence('B')
    assert Sequence('B').next() == 'B-0'
    assert Sequence('B').next() == 'B-1'


def test_reset(db):
    """Test reset sequence."""
    y = Template.create('FL', '{year}: File {counter}')
    y15 = Sequence(y, year=2015)
    y16 = Sequence(y, year=2016)

    assert y15.next() == '2015: File 0'
    assert y15.next() == '2015: File 1'

    assert y16.next() == '2016: File 0'
    assert y16.next() == '2016: File 1'

    y15.counter.reset()
    assert y15.next() == '2015: File 0'
    assert y15.next() == '2015: File 1'
    y16.counter.reset(start=156)
    assert y16.next() == '2016: File 156'
    assert y16.next() == '2016: File 157'


def test_delete(db):
    """Test delete."""
    fl = Template.create('FL', '{year}: File {counter}')

    fl15 = Sequence(fl, year=2015)
    assert list(islice(fl15, 20))
    assert fl15.next() == '2015: File 20'

    fl16 = Sequence(fl, year=2016)
    assert list(islice(fl16, 30))
    assert fl16.next() == '2016: File 30'

    fl17 = Sequence(fl, year=2017)
    assert fl17.next() == '2017: File 0'

    assert db.session.query(Counter).count() == 3

    db.session.delete(fl17.counter)
    assert db.session.query(Counter).count() == 2

    db.session.delete(fl.model)
    db.session.commit()

    with pytest.raises(SequenceNotFound):
        Sequence('FL', year=2016)
    assert db.session.query(Counter).count() == 0


def test_step(db):
    """Test larger incremental steps."""
    fl = Template.create('FL', 'File {counter}', start=0, step=100)
    seq = Sequence(fl)

    assert seq.next() == 'File 0'
    assert seq.next() == 'File 100'
    assert seq.next() == 'File 200'
    assert seq.next() == 'File 300'
    seq.counter.reset(start=15)
    assert seq.next() == 'File 15'
    assert seq.next() == 'File 115'
    assert seq.next() == 'File 215'
    assert seq.next() == 'File 315'


def test_iter(db):
    """Test simple files use-case."""
    fl = Sequence(Template.create('FL', 'File {counter}'))
    assert list(islice(fl, 10)) == ['File {}'.format(c) for c in range(0, 10)]

    y = Sequence(Template.create('Y', '{year}: {counter}'), year=2016)
    assert list(islice(y, 10)) == ['2016: {}'.format(c) for c in range(0, 10)]


def test_exceptions(db):
    """Test exceptions."""

    p1 = Sequence(Template.create('P1', 'P-{counter}'))
    assert p1.next() == 'P-0'
    Template.create('P2', 'P:{counter}')

    with pytest.raises(InvalidTemplate) as exc:
        Template.create('invalid', '{P1}-{P2}-{counter}')
    assert 'More than 1 parents in template' in str(exc)

    with pytest.raises(InvalidTemplate) as exc:
        Template.create('invalid', 'INVALID')
    assert 'No counter placeholder' in str(exc)

    assert Sequence('P1')
    with pytest.raises(SequenceNotFound):
        Sequence('invalid')

    seq = Template.create('C1', '{P1}:{counter}')
    seq1 = Sequence(seq, P1='P-0')
    assert seq1.next() == 'P-0:0'
    with pytest.raises(KeyError) as exc:
        Sequence(seq).next()
    assert 'P1' in str(exc)

    with pytest.raises(InvalidResetCall) as exc:
        Sequence('P1').counter.reset()
    assert 'Cannot reset sequence: children exist' in str(exc)


def test_formatting(db):
    """Test counter formatting options."""
    seq1 = Sequence(Template.create('P', 'P-{counter:03d}'))
    assert seq1.next() == 'P-000'
    assert seq1.next() == 'P-001'
    assert seq1.next() == 'P-002'

    seq2 = Template.create('C', '{P}-{counter:04d}')
    p1 = Sequence(seq2, P='P-000')
    assert p1.next() == 'P-000-0000'
    assert p1.next() == 'P-000-0001'
    assert p1.next() == 'P-000-0002'
    p2 = Sequence(seq2, P='P-001')
    assert p2.next() == 'P-001-0000'
    assert p2.next() == 'P-001-0001'


def test_regex():
    """Test counter regex."""
    cr = TemplateDefinition.COUNTER_REGEX
    assert cr.search(' << {counter!r:04d} >> ')

    assert double_counter('<{counter}>', cr) == '<{{counter}}>'
    assert double_counter('<{counter!r}>', cr) == '<{{counter!r}}>'
    assert double_counter('<{counter:04d}>', cr) == '<{{counter:04d}}>'
    assert double_counter('<{counter!r:04d}>', cr) == '<{{counter!r:04d}}>'


def test_py3_next(db):
    """Test PY3 __next__."""
    assert Sequence(Template.create('PY3', '{counter}')).__next__() == '0'


def test_repr(db):
    """Test __repr__."""
    template = Template.create('A', '{counter}')
    assert repr(template.model) == (
        "TemplateDefinition(name='A', "
        "meta_template='{counter}', start=0, step=1)"
    )
    sequence = Sequence(template)
    assert repr(sequence.counter) == (
        "Counter(template_instance='{counter}', "
        "definition_name='A', counter=0, template_definition="
        "TemplateDefinition(name='A', meta_template='{counter}', "
        "start=0, step=1))"
    )
