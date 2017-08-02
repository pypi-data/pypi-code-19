#!/usr/bin/python
# -*- coding: utf-8 -*-

edfStr = u"""
{#- Jinja2 template -#}
{
{% if header is defined -%}
{%- for key, val in header.iteritems() %}
{{ key }} = {{ val }} ;
{%- endfor -%}
{%- else -%}
EDF_DataBlockID = 0.Image.Psd ;
EDF_BinarySize = {{ binsize }} ;
EDF_HeaderSize = {{ headersize }} ;
ByteOrder = LowByteFirst ;
DataType = {% if datatype %}{{ datatype }}{% else %}SignedInteger{% endif %} ;
Dim_1 = {{ dim_1 }} ;
Dim_2 = {{ dim_2 }} ;
Image = 0 ;
Bubble_normalized = {% if normalized %}1{% else %}0{% endif %} ;
HeaderID = EH:000000:000000:000000 ;
Size = {{ binsize }} ;
conversions = x-CBF_BYTE_OFFSET ;
{%- endif %}
}

"""
