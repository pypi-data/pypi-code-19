# -*- coding: utf-8 -*-
def listToDict(list : list , keyColumn : str) -> dict:
    '''
    list型のオブジェクトを、Dict型に変換する
    :param list: 対象list型オブジェクト
    :param keyColumn: Dictのキーとするカラム
    :return: 変換されたDict型オブジェクト
    '''
    parsed = dict()
    for item in list :
        key = item.get(keyColumn)
        parsed.update({key : item})

    return parsed

def replaceParam(target : str, params : dict) -> str:
    '''
    文字列のパレメータ置換処理を行う。
    例えば、引数targetの内容が"{id} is id. {pass} is pass"
    かつ、引数paramsが{id : "JohnDoe", pass : "abc111abc"}であった場合
    "JonDoe is id. abc111abc is pass" と変換された文字列を返す。
    :param target: 変換対象文字列
    :param params: 置換パラメータ
    :return: 置換処理された文字列
    '''
    for key in params.keys() :
        value = params[key]
        replaceKey = '{' + key +'}'
        if value and replaceKey:
            target = target.replace(replaceKey, str(value))
    return target
