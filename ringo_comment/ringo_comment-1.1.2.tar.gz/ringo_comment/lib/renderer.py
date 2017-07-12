import os
import pkg_resources
import cgi
from mako.lookup import TemplateLookup
import ringo.lib.security as security
from ringo.lib.renderer.form import FieldRenderer
from ringo.lib.helpers import literal

base_dir = pkg_resources.get_distribution("ringo_comment").location
template_dir = os.path.join(base_dir, 'ringo_comment', 'templates')
template_lookup = TemplateLookup(directories=[template_dir],
                                 default_filters=['h'])


class CommentRenderer(FieldRenderer):
    """Custom Renderer for the comment listing"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("comments.mako")

    def _get_template_values(self):
        values = FieldRenderer._get_template_values(self)
        comments = []
        for comment in self._field._form._item.comments:
            if security.has_permission('read',
                                       comment,
                                       self._field._form._request):
                comments.append(comment)
        if self._field._form.has_errors():
            last_comment = self._field._form.submitted_data.get("comment", "")
        else:
            last_comment = ""

        values['last_comment'] = last_comment
        values['comments'] = comments
        return values

    def nl2br(self, value=""):
        return literal("<br />".join(cgi.escape(value).split("\n")))
