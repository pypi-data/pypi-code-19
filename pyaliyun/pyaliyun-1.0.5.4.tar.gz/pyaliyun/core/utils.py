#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
aliyun的辅助工具方法
"""
import hmac
import time
import xml.dom.minidom
from hashlib import sha1 as sha

from pyaliyun.core.cryptool import b64encode_as_string
from pyaliyun.core.encoding import force_text, force_bytes
from pyaliyun.core.six import iteritems, dict_type


def get_date():
    """
    获取标准GMT时间格式,放在header里用
    :return:
    """
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())


def sign(
        ak_secret,
        http_method,
        content_md5,
        content_type,
        date,
        resource_string,
        headers_string):
    """
    通用签名函数
    """
    # 连接待签字符串
    string_to_sign = '\n'.join([http_method,
                                content_md5,
                                content_type,
                                date,
                                headers_string + resource_string])
    h = hmac.new(force_bytes(ak_secret), force_bytes(string_to_sign), sha)
    signature = b64encode_as_string(h.digest()).strip()
    # signature = base64.b64decode(force_bytes(h.digest())).strip()
    return signature


def build_header_authorization(business, ak_id, signature):
    """
    组合最终Authorization的值,用以放在header里
    Authorization: MNS AccessKeyId:Signature
    :param business:
    :param ak_id:
    :param signature:
    :return:
    """
    return "{0} {1}:{2}".format(business, ak_id, signature)


def buiild_canonicalized_headers(headers, prefix):
    """
    aliyun的header里的canonicalized属性排序和计算
    :param headers:
    :param prefix:
    :return:
    """
    canonicalized_headers = ""
    if len(headers) > 0:
        x_header_list = headers.keys()
        sorted(x_header_list)
        for k in x_header_list:
            if k.startswith(prefix):
                canonicalized_headers += k + ":" + headers[k] + "\n"
    return canonicalized_headers


def dictToXml(params, xmlns):
    """array转xml"""
    xml = [u"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"]
    for k, v in iteritems(params):
        if isinstance(v, int) or isinstance(v, float):
            xml.append(u"<{0}>{1}</{0}>".format(k, v))
        elif v.isdigit():
            xml.append(u"<{0}>{1}</{0}>".format(k, v))
        else:
            text_v = force_text(v)
            xml.append(u"<{0}><![CDATA[{1}]]></{0}>".format(k, text_v))
    xml_body = u"".join(xml)
    xml_body_utf8 = xml_body.encode('utf-8')
    return xml_body_utf8


def dict_to_xml(tag_name, data_dic, xmlns):
    """
    编译成xml
    :param tag_name:
    :param data_dic:
    :param xmlns:
    :return:
    """
    doc = xml.dom.minidom.Document()
    rootNode = doc.createElement(tag_name)
    rootNode.attributes["xmlns"] = xmlns
    doc.appendChild(rootNode)
    if data_dic:
        for k, v in data_dic.items():
            keyNode = doc.createElement(k)
            if type(v) is dict_type:
                for subkey, subv in v.items():
                    subNode = doc.createElement(subkey)
                    subNode.appendChild(doc.createTextNode(subv))
                    keyNode.appendChild(subNode)
            else:
                keyNode.appendChild(doc.createTextNode(force_text(v)))
            rootNode.appendChild(keyNode)
    else:
        nullNode = doc.createTextNode("")
        rootNode.appendChild(nullNode)
    return doc.toxml("utf-8")
