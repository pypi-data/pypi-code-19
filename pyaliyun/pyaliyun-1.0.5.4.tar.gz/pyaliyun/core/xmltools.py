#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
xml工具
参考 nodeType
    ELEMENT_NODE                = 1
    ATTRIBUTE_NODE              = 2
    TEXT_NODE                   = 3
    CDATA_SECTION_NODE          = 4
    ENTITY_REFERENCE_NODE       = 5
    ENTITY_NODE                 = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE                = 8
    DOCUMENT_NODE               = 9
    DOCUMENT_TYPE_NODE          = 10
    DOCUMENT_FRAGMENT_NODE      = 11
    NOTATION_NODE               = 12
"""

import xml.dom.minidom

from pyaliyun.core import six
from pyaliyun.core.exception import PyAliParameterException

XML_ATTRIBUTE_KEY_NAME = "@attributes@"
XML_DOCUMENT_KEY_NAME = "@document@"

class XmlDecoder(object):
    """
    xml解析类
    """

    @staticmethod
    def xml_to_dict(xml_string):
        dict_root = {}
        xml_string = xml_string.strip()
        if xml_string == "":
            return dict_root
            # raise PyAliParameterException("ParamError", "Xml data is \"\"!", param_name="xml_data")
        root_document = xml.dom.minidom.parseString(xml_string)
        parse_dict = XmlDecoder.parse_childnodes(root_document)
        return parse_dict

    @staticmethod
    def parse_childnodes(node):
        node_dict = {}
        attrs_dict = XmlDecoder.parse_node_attributes(node)
        if attrs_dict:
            node_dict.update(attrs_dict)
        for sub_node in node.childNodes:
            sub_name = sub_node.nodeName
            # 如果有子节点,继续解析子节点
            if sub_node.hasChildNodes():
                child_dict = XmlDecoder.parse_childnodes(sub_node)
                if sub_name in node_dict:
                    old_sub_value = node_dict.get(sub_name)
                    if type(old_sub_value) == six.dict_type:
                        # 转成列表, 添加两个新的进去
                        sub_list = []
                        sub_list.append(old_sub_value)
                        sub_list.append(child_dict)
                        node_dict.update({sub_name: sub_list})
                    elif type(old_sub_value) == six.list_type:
                        old_sub_value.append(child_dict)
                        node_dict.update({sub_name: old_sub_value})
                else:
                    node_dict.update({sub_name: child_dict})
            else:
                node_text = XmlDecoder.parse_node_text(node)
                if node_text:
                    node_dict.update(node_text)

        return node_dict

    @staticmethod
    def parse_node_text(node):
        """
        文本节点
        :param node:
        :return:
        """
        # 只有一个子节点
        if len(node.childNodes) == 1:
            text_node = node.childNodes[0]
            if text_node.nodeName == '#text':
                node_value = text_node.nodeValue.strip()
                if node_value != '\\n':
                    return {'@document@': node_value}
                return None

    @staticmethod
    def parse_node_attributes(node):
        """
        解析节点的属性
        :param node:
        :return:
        """
        node_attrs = node.attributes
        if node_attrs:
            attr_dict = {}
            for attr in node_attrs.items():
                attr_dict[attr[0]] = attr[1]
            return {'@attributes@': attr_dict}
        return None

    @staticmethod
    def get_attributes(node_dict):
        """
        获取属性的字典
        :param node_dict:
        :return:
        """
        return node_dict.get(XML_ATTRIBUTE_KEY_NAME)

    @staticmethod
    def get_document(node_dict):
        """
        获取节点里的纯文本
        :param node_dict:
        :return:
        """
        return node_dict.get(XML_DOCUMENT_KEY_NAME)