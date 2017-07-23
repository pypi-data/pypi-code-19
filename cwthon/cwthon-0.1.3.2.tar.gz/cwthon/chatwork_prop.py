# -*- coding: utf-8 -*-
from enum import Enum

class cwGrammar(Enum) :
    '''
    チャットワーク独自の文法の列挙型
    '''
    TO = '[To:{account_id}]'
    QUOTE_TIME = '[qt][qtmeta aid={account_id} time={timestamp}]{body}[/qt]'
    QUOTE = '[qt][qtmeta aid={account_id}]{body}[/qt]'
    INFO = '[info]{body}[/info]'
    INFO_TITLE = '[info][title]{title}[/title]{body}[/info]'
    RULE = '[hr]'
    PICON = '[picon:{account_id}]'
    PICON_NAME = '[piconname:{account_id}]'

class reqMethods(Enum) :
    '''
    リクエストメソッドの列挙型
    '''
    POST = 'post'
    GET = 'get'
    DELETE = 'delete'

class cwEndPoint(Enum) :
    '''
    エンドポイントURLの列挙型
    '''
    SEND_MSG = {'url' : 'rooms/{room_id}/messages', 'method' : reqMethods.POST, 'params' : ['body']}
