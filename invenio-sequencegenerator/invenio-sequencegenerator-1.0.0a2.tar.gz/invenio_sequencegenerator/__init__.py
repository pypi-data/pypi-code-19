# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module for generating sequences.

Invenio-SequenceGenerator is a secondary component of Invenio, responsible for
automatically generating identifiers in a safe manner (i.e. making sure
that every time a client requests a new identifier of a specific form, the
server will provide him with a new *unique* identifier).

Conventions
-----------
Conventions regarding template strings of sequences:

- They must contain exactly one placeholder for the counter, named 'counter',
  which possibly contains conversion and/or format options.

  ========================== ====================================
  Correct                    False
  ========================== ====================================
  ``'File {counter}'``       ``'File {count}'``
  ``'{counter}: File'``      ``'File'``
  ``'{counter:02d}: File'``  ``'File {counter:invalid_format}'``
  ========================== ====================================

.. note::

    You can format the counter (and all other placeholders) with all the
    formatting options provided by Python strings.

- They can contain an optional placeholder for a parent sequence, named as the
  parent sequence, defined when the `Sequence.create` API function was called.

  ============================== ===========================
  Correct                        False
  ============================== ===========================
  PL = ``'Playlist {counter}'``  ``'{PL}-{FL} {counter}'``
  FL = ``'{PL}: {counter}'``     ``'{INVALID}: {counter}'``
  ============================== ===========================

  For a more in-depth example, see :ref:`Hierarchical identifiers`.

- They can contain an arbitrary number of user-defined placeholders, which must
  be always passed as keyword arguments on each instantiation. No exception
  is raised in case of redundant keyword arguments.

  You can find more examples in :ref:`User-defined keywords`.

Initialization
--------------
First create a Flask application:

>>> from flask import Flask
>>> app = Flask('myapp')
>>> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

Then initialise the Invenio-DB extension:

>>> from invenio_db import InvenioDB
>>> ext_db = InvenioDB(app)

Also, initialise the Invenio-SequenceGenerator extension:

>>> from invenio_sequencegenerator.ext import InvenioSequenceGenerator
>>> ext_seq = InvenioSequenceGenerator(app)

In order for the following examples to work, you need to work within an
Flask application context so let's push one:

>>> ctx = app.app_context()
>>> ctx.push()

Also, for the examples to work we need to create the database and tables (note,
in this example we use an in-memory SQLite database):

>>> from invenio_db import db
>>> db.create_all()

Template definition
-------------------
The first thing to do is to define your sequence (i.e. the specific form of
your identifiers):

>>> from invenio_sequencegenerator.api import Template
>>> template = Template.create('ID', '{counter}-file')

Simple counters
---------------
Next, you have to get a sequence based on the aforementioned template. During
this tutorial, this will be referred to as 'instantiation'.

>>> from invenio_sequencegenerator.api import Sequence
>>> seq = Sequence(template)

Then you can request new identifiers from the sequence defined above:

>>> seq.next()
'0-file'
>>> seq.next()
'1-file'
>>> seq.next()
'2-file'

.. note::

    By default, counters start from 0 and are incremented by 1.

Advanced counters
-----------------
You can also specify the initial counter and increment:

>>> tpl = Template.create('ID2', '{counter:02d}-file', start=10, step=10)
>>> seq = Sequence(tpl)
>>> seq.next()
'10-file'
>>> seq.next()
'20-file'
>>> seq.next()
'30-file'

User-defined keywords
---------------------
Consider the case where you need to generate identifiers for files of
different categories. Thus, your template definition should look like this:

>>> cat = Template.create('KW', '{category}: File {counter:03d}', start=1)

Next, instantiate the template for specific categories:

.. note::

    Keyword arguments must be always specified on instantiation.

>>> photos = Sequence(cat, category='PHOTOS')
>>> photos.next()
'PHOTOS: File 001'
>>> photos.next()
'PHOTOS: File 002'
>>> videos = Sequence(cat, category='VIDEOS')
>>> videos.next()
'VIDEOS: File 001'
>>> videos.next()
'VIDEOS: File 002'

>>> Sequence('invalid')
Traceback (most recent call last):
 ...
SequenceNotFound

>>> invalid = Sequence(cat, invalid='PHOTOS')
>>> invalid.next()
Traceback (most recent call last):
 ...
KeyError

Hierarchical identifiers
------------------------
It is possible to have nested templates (i.e. templates depending on another).
This is achieved by placing a placeholder with the name of the parent template
and making sure a valid identifier of the parent is passed on each
instantiation.

Consider the example of playlists of audio files for each year. We need two
template definitions, one for playlists and one for files:

>>> pl = Template.create('PL', '{year}: Playlist {counter}', start=1)
>>> fl = Template.create('FL', '{PL} > Audio File {counter:02d}', start=1)

Let's get some playlists for different years:

>>> pl15 = Sequence(pl, year=2015)
>>> pl15.next()
'2015: Playlist 1'
>>> pl15.next()
'2015: Playlist 2'
>>> pl16 = Sequence(pl, year=2016)
>>> pl16.next()
'2016: Playlist 1'

Now let's get some files inside the playlists generated above:

>>> fl15 = Sequence(fl, PL='2015: Playlist 2')
>>> fl15.next()
'2015: Playlist 2 > Audio File 01'
>>> fl15.next()
'2015: Playlist 2 > Audio File 02'
>>> fl16 = Sequence(fl, PL='2016: Playlist 1')
>>> fl16.next()
'2016: Playlist 1 > Audio File 01'

Bulk generations
----------------
As Sequence is a proper Python iterator, you can use all Python methods that
consume them (mainly found on the itertools library). Picking up from the last
example with playlists, one might want to generate multiple files for a
specific playlist, all at once:

>>> from itertools import islice
>>> list(islice(fl15, 5)) # doctest: +SKIP
['2016: Playlist 2 > Audio File 03', '2016: Playlist 2 > Audio File 04',
'2016: Playlist 2 > Audio File 05', '2016: Playlist 2 > Audio File 06',
'2016: Playlist 2 > Audio File 07']

Command-line interface
----------------------
It is possible to use the command-line interface, instead of using the API
directly. As you would expect, one can define new templates and get new
identifiers from sequences.

To get started, we need to first setup the example app:

.. code-block:: console

    $ cd examples
    $ export FLASK_APP=app.py
    $ flask db init
    $ flask db create

Let's see the example introduced in :ref:`Simple counters`, using the CLI this
time:

.. code-block:: console

    $ flask sequences create ID '{counter}-file'
    $ flask sequences next ID
    0-file
    $ flask sequences next ID
    1-file
    $ flask sequences next ID
    2-file

Now let's see a more complicated example, such as the one shown in
:ref:`Hierarchical identifiers`:

.. code-block:: console

    $ flask sequences create PL '{year}: Playlist {counter}' --start 1
    $ flask sequences create FL '{PL} > Audio File {counter:02d}' --start 1
    $ flask sequences next PL year=2015
    2015: Playlist 1
    $ flask sequences next PL year=2015
    2015: Playlist 2
    $ flask sequences next PL year=2016
    2016: Playlist 1
    $ flask sequences next FL PL='2015: Playlist 2'
    2015: Playlist 2 > Audio File 01
    $ flask sequences next FL PL='2015: Playlist 2'
    2015: Playlist 2 > Audio File 02
    $ flask sequences next FL PL='2016: Playlist 1'
    2016: Playlist 1 > Audio File 01

"""

from __future__ import absolute_import, print_function

from .ext import InvenioSequenceGenerator
from .version import __version__

__all__ = ('__version__', 'InvenioSequenceGenerator')
