import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.conf.urls import patterns
from django.template.defaultfilters import truncatechars
from django.shortcuts import get_object_or_404, redirect
from django import forms

from wagtail.wagtailcore.utils import cautious_slugify

from molo.yourtips.models import (
    YourTipsEntry, YourTip, YourTipsSectionIndexPage, YourTipsArticlePage
)


@staff_member_required
def convert_to_article(request, entry_id):
    def get_entry_author(entry):
        if not entry.optional_name:
            return 'By Anonymous'
        return 'By %s' % entry.optional_name

    entry = get_object_or_404(YourTipsEntry, pk=entry_id)
    if not entry.converted_article_page:
        tip_section_index_page = YourTipsSectionIndexPage.objects.\
            descendant_of(request.site.root_page).live().first()
        tip_article = YourTipsArticlePage(
            title='Tip-%s' % str(entry.id),
            slug='yourtips-entry-%s' % cautious_slugify(entry.id),
            body=json.dumps([
                {"type": "paragraph", "value": entry.tip_text},
                {"type": "heading", "value": get_entry_author(entry)}
            ])
        )
        tip_section_index_page.add_child(instance=tip_article)
        tip_article.save_revision()
        tip_article.unpublish()

        entry.converted_article_page = tip_article
        entry.save()
    return redirect('/admin/pages/%d/edit/' % entry.converted_article_page.id)


class YourTipsEntryForm(forms.ModelForm):

    class Meta:
        model = YourTipsEntry
        fields = ['tip_text', "optional_name"]


class YourTipsEntryAdmin(admin.ModelAdmin):
    list_display = ['truncate_text', 'user', 'optional_name',
                    'submission_date', 'allow_share_on_social_media',
                    '_convert']
    list_filter = ['submission_date']
    date_hierarchy = 'submission_date'
    form = YourTipsEntryForm
    readonly_fields = ('tip_text', 'optional_name', 'submission_date')

    def truncate_text(self, obj, *args, **kwargs):
        return truncatechars(obj.tip_text, 30)

    def get_urls(self):
        urls = super(YourTipsEntryAdmin, self).get_urls()
        entry_urls = patterns(
            '', (r'^(?P<entry_id>\d+)/convert/$', convert_to_article)
        )
        return entry_urls + urls

    def _convert(self, obj, *args, **kwargs):
        if obj.converted_article_page:
            return (
                '<a href="/admin/pages/%d/edit/">Article Page</a>' %
                obj.converted_article_page.id)
        return (
            ' <a href="%d/convert/" class="addlink">Convert to article</a>' %
            obj.id)

    _convert.allow_tags = True
    _convert.short_description = ''


class YourTipsAdmin(admin.ModelAdmin):
    list_display = ['status']
    list_filter = ['title']
    search_fields = ['title', 'content', 'description']

    def status(self, obj, *args, **kwargs):
        if obj.live:
            return 'First published on ' + str(obj.first_published_at.date())
        return 'Unpublished'


class YourTipsArticlePageAdmin(admin.ModelAdmin):
    list_display = ['title', 'latest_revision_created_at', 'votes', 'live']
    list_filter = ['title']
    search_fields = ['title', 'content', 'description']
    date_hierarchy = 'latest_revision_created_at'


admin.site.register(YourTipsEntry, YourTipsEntryAdmin)
admin.site.register(YourTipsArticlePage, YourTipsArticlePageAdmin)
admin.site.register(YourTip, YourTipsAdmin)
