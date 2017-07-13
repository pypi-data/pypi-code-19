#!/usr/bin/python
# -*- coding: utf-8 -*-


class PyAliException(Exception):
    """
    基础异常类
    """

    def __init__(self, error_type, message, req_id=None):
        self.error_type = error_type
        self.message = message
        self.req_id = req_id

    def get_error_info(self):
        if self.req_id is not None:
            return "(\"%s\" \"%s\") RequestID:%s\n" % (self.error_type, self.message, self.req_id)
        else:
            return "(\"%s\" \"%s\")\n" % (self.error_type, self.message)

    def __str__(self):
        return "AliyunException  %s" % (self.get_error_info())


class PyAliParameterException(PyAliException):
    """
    参数错误
    """

    def __init__(self, error_type, message, req_id=None, param_name=None):
        self.param_name = param_name
        super(PyAliParameterException, self).__init__(error_type, message, req_id)

    def get_error_info(self):
        if self.req_id is not None:
            return "(\"%s\" \"%s\") RequestID:%s\n Param name : %s" % \
                   (self.error_type, self.message, self.req_id, self.param_name)
        else:
            return "(\"%s\" \"%s\")\n Param name : %s" % \
                   (self.error_type, self.message, self.param_name)

    def __str__(self):
        return "PyAliParameterException  %s" % (self.get_error_info())


class PyAliErrorResponseException(PyAliException):
    """
    错误的响应
    """

    def __init__(self, error_type, message, req_id=None, code=None):
        self.code = code
        super(PyAliErrorResponseException, self).__init__(error_type, message, req_id)

    def get_error_info(self):
        if self.req_id is not None:
            return "(\"%s\" \"%s\") RequestID:%s\n Error code: %s" % \
                   (self.error_type, self.message, self.req_id, self.code)
        else:
            return "(\"%s\" \"%s\")\n Error code: %s" % \
                   (self.error_type, self.message, self.code)

    def __str__(self):
        return "PyAliErrorResponseException  %s" % (self.get_error_info())


class PyAliXmlParseException(PyAliException):
    """
    xml解析错误
    """

    def __init__(self, error_type, message, req_id=None):
        super(PyAliXmlParseException, self).__init__(error_type, message, req_id)

    def __str__(self):
        return "PyAliXmlParseException  %s" % (self.get_error_info())