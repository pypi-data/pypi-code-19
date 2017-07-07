# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Term.definition'
        db.alter_column(u'glossario_term', 'definition', self.gf('djangocms_text_ckeditor.fields.HTMLField')(null=True))

    def backwards(self, orm):
        try:
            import tinymce.models.HTMLField
        except ImportError:
            pass
        else:
            # Changing field 'Term.definition'
            db.alter_column(u'glossario_term', 'definition', self.gf('tinymce.models.HTMLField')(null=True))

    models = {
        u'glossario.term': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Term'},
            'alias': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['glossario.Term']", 'null': 'True', 'blank': 'True'}),
            'definition': ('djangocms_text_ckeditor.fields.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['glossario']