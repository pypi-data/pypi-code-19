# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import connection
try:
    import tinymce.models.HTMLField
except ImportError:
    definition_class = 'djangocms_text_ckeditor.fields.HTMLField'
else:
    definition_class = 'tinymce.models.HTMLField'


class Migration(SchemaMigration):

    def forwards(self, orm):
        table_names = connection.introspection.table_names()
        if 'glossario_term' not in table_names:
            # Adding model 'Term'
            db.create_table(u'glossario_term', (
                ('id', self.gf('django.db.models.fields.SlugField')(max_length=50, primary_key=True)),
                ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
                ('definition', self.gf(definition_class)(null=True, blank=True)),
                ('alias', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['glossario.Term'], null=True, blank=True)),
            ))
            db.send_create_signal(u'glossario', ['Term'])

    def backwards(self, orm):
        # Deleting model 'Term'
        db.delete_table(u'glossario_term')

    models = {
        u'glossario.term': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Term'},
            'alias': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['glossario.Term']", 'null': 'True', 'blank': 'True'}),
            'definition': (definition_class, [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['glossario']
