from django.db import migrations

from django.db import migrations, models

def update_permission_names(apps, schema_editor):

    Permission = apps.get_model('auth', 'Permission')
    Article = apps.get_model('thorson_wiki', 'Article')

    for permission in Permission.objects.all():
        old_codename = permission.codename

        try:
            (old_prefix, old_slug) = old_codename.split(':', 1)
        except ValueError:
            continue

        if old_prefix == 'edit-article':
            old_object = Article.objects.get(slug=old_slug)
            permission.codename = 'edit-article:%s:%s' % (old_object.namespace,
                    old_object.slug)
            permission.name = "Can edit the article '%s' in namespace '%s'" \
                    % (old_object.title, old_object.namespace)
            permission.save()
        elif old_prefix == 'read-article':
            old_object = Article.objects.get(slug=old_slug)
            permission.codename = 'read-article:%s:%s' % (old_object.namespace,
                    old_object.slug)
            permission.name = "Can read the article '%s' in namespace '%s'" \
                    % (old_object.title, old_object.namespace)
            permission.save()
        else:
            continue

class Migration(migrations.Migration):

    dependencies = [
        ('thorson_wiki', '0003_auto_20170701_1416'),
    ]

    operations = [
        migrations.RunPython(update_permission_names)
    ]
