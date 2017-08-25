from thorson_wiki.models import Article
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from django.utils.text import slugify

@receiver(pre_save, sender=Article)
def update_slug(sender, **kwargs):
    """
    Updates an Articles slug when the object is updated. This also results in
    updating the article permissions.
    """

    instance = kwargs['instance']
    try:
        old_instance = Article.objects.get(id=instance.id)
    except Article.DoesNotExist:
        old_instance = None

    instance.slug = slugify(instance.title)

    if old_instance is None:
        return

    old_slug = old_instance.slug

    if instance.slug != old_instance.slug or \
            instance.namespace != old_instance.namespace:
        edit_permission = Permission.objects.get(
            codename='edit-article:%s:%s' % (old_instance.namespace,
                old_instance.slug)
        )

        edit_permission.codename='edit-article:%s:%s' % (instance.namespace,
                instance.slug)
        edit_permission.name="Can edit the article '%s' in namespace '%s'" \
                % (instance.title, instance.namespace)
        edit_permission.save()

        read_permission = Permission.objects.get(
            codename='read-article:%s:%s' % (old_instance.namespace,
                old_instance.slug)
        )

        read_permission.codename='read-article:%s:%s' % (instance.namespace,
                instance.slug)
        read_permission.name="Can read the article '%s' in namespace '%s'" \
                % (instance.title, instance.namespace)
        read_permission.save()

@receiver(post_save, sender=Article)
def create_article_permissions(sender, **kwargs):
    """
    Creates individual article permissions when an article is created.
    """

    instance = kwargs['instance']
    created = kwargs.get('created', False)

    slug = instance.slug
    namespace = instance.namespace
    title = instance.title

    if created:
        content_type = ContentType.objects.get_for_model(Article)
        permission = Permission.objects.create(
            codename='edit-article:%s:%s' % (namespace, slug),
            name="Can edit the article '%s' in namespace '%s'" % \
                    (title, namespace),
            content_type=content_type
        )

        content_type = ContentType.objects.get_for_model(Article)
        permission = Permission.objects.create(
            codename='read-article:%s:%s' % (namespace, slug),
            name="Can read the article '%s' in namespace '%s'" % \
                    (title, namespace),
            content_type=content_type
        )

@receiver(post_delete, sender=Article)
def delete_article_permissions(sender, **kwargs):
    """
    Deletes an article's permissions when the article is deleted.
    """

    instance = kwargs['instance']

    slug = instance.slug
    namespace = instance.namespace

    try:
        Permission.objects.get(codename='edit-article:%s:%s' % (namespace,
            slug)).delete()
    except ObjectDoesNotExist:
        pass
    try:
        Permission.objects.get(codename='read-article:%s:%s' % (namespace,
            slug)).delete()
    except ObjectDoesNotExist:
        pass
