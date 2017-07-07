# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.fields import HTMLField


class TermManager(models.Manager):
    def term_exists(self, name, exact=True):
        """
        Restituisce True se trova la voce di glossario `name`, False altrimenti.
        Se `exact` è True cerca una corrispondenza esatta, altrimenti si limita all'inizio del valore.
        """
        if name:
            if exact:
                return self.filter(name__iexact=name).exists()
            return self.filter(name__istartswith=name).exists()
        return False


class Term(models.Model):
    id = models.SlugField(max_length=50, primary_key=True, verbose_name=_("Chiave"))
    name = models.CharField(max_length=50, blank=False, null=False, verbose_name=_("Termine"))
    definition = HTMLField(blank=True, null=True, verbose_name=_("Definizione"))
    alias = models.ForeignKey('self', blank=True, null=True, verbose_name=_("Sinonimo di"))

    objects = TermManager()

    def get_url(self):
        if self.id:
            return reverse('glossario_term', kwargs={'current': self.id[0], 'pk': self.pk})

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        verbose_name = _("termine")
        verbose_name_plural = _("termini")
        ordering = ('name',)


@receiver((models.signals.post_save, models.signals.post_delete), sender=Term)
def clear_index_cache(sender, **kwargs):
    if sender == Term:
        from .helpers import index_list

        index_list(reset=True)
