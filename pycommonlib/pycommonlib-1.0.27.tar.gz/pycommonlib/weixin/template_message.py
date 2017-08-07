# -*- coding: utf-8 -*-
from . import weixin_lib
from common.util import datetime

class TemplateMessage(object):
    
    def __init__(self, templateId, *args, **kwargs):
        self.templateId = templateId
        object.__init__(self, *args, **kwargs)
    
    def send(self, toOpenId, url, data):
        templateData = {}
        for (key, value) in data.iteritems():
            templateData[key] = {'value':value, 'color':'#173177'}
        weixin_lib.sent_template_message(toOpenId, self.templateId, url, templateData)
        
        
class IMReplyMessage(TemplateMessage):
    
    def __init__(self, *args, **kwargs):
        
        super(IMReplyMessage, self).__init__('S7DM8R_ASRHX8Yf6BAEF90H-GXy6idqtmnFDK28zQXE',)
        
        
    def send(self, toOpenId, fromUsername, messgae, *args, **kwargs):
        data = {}
        data['first'] = u'您好！您收到一条回复信息'
        data['keyword1'] = fromUsername
        data['keyword2'] = datetime.now_str()
        data['keyword3'] = messgae
        data['remark'] = u'点击此消息来回复'
        url = self._make_url(kwargs)
        TemplateMessage.send(self, toOpenId, url, data)
        
        
    def _make_url(self, kwargs):
        parameter = []
        for (key, value) in kwargs.iteritems():
            parameter.append('{}_{}'.format(key, value))
        state = 'im'
        if len(parameter) > 0:
            state = state + '_' + '_'.join(parameter)
        return 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx462721a7464334e0&redirect_uri=http%3A%2F%2Fwww.wuwuke.com%2Fapi%2Fv1.0%2Fweixin%2Flogin%2F&response_type=code&scope=snsapi_base&state={}#wechat_redirect'.format(state)
    
        
        
class HouseCheckMessage(TemplateMessage):
    
    def __init__(self):
        super(HouseCheckMessage, self).__init__('mjaRCrCT8zcXh8rRGoVV_w8GHQp3U-yGq-5ujou6oqY')
        self.url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx462721a7464334e0&redirect_uri=http%3A%2F%2Fwww.wuwuke.com%2Fapi%2Fv1.0%2Fweixin%2Flogin%2F&response_type=code&scope=snsapi_base&state=my#wechat_redirect'
        
    def send(self, toOpenId, houseNum, contact_name, contact_tel):
        data = {}
        data['first'] = u'您好！您发布的房源已经通过审核,房源编号为{}'.format(houseNum)
        data['keyword1'] = contact_name
        data['keyword2'] = contact_tel
        data['keyword3'] = datetime.now_str()        
        data['remark'] = u'点击此消息查看详情'
        TemplateMessage.send(self, toOpenId, self.url, data)    
        
