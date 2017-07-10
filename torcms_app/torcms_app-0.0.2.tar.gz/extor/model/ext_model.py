import tornado.escape
import tornado.web
from torcms.model.reply_model import MReply
from torcms.model.rating_model import MRating
from torcms.core.libs.deprecation import deprecated

class panel_reply(tornado.web.UIModule):
    '''
    the reply panel.
    '''

    def render(self, *args):
        uid = args[0]
        userinfo = args[1]
        return self.render_string(
            'modules_ext/reply_panel.html',
            uid=uid,
            replys=MReply.query_by_post(uid),
            userinfo=userinfo,
            unescape=tornado.escape.xhtml_unescape,
            linkify=tornado.escape.linkify
        )