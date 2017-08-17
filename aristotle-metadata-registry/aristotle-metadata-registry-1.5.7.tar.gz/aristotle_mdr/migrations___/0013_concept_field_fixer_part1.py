# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aristotle_mdr.utils.migrations import ConceptMigrationAddConceptFields

class Migration(ConceptMigrationAddConceptFields):
    dependencies = [
        ('aristotle_mdr', '0001_squashed_0012_better_workflows'),
    ]
