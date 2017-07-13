# -*- coding: utf-8 -*-
import zope.schemaevent
from zope.component.testlayer import ZCMLFileLayer


ZC_LAYER = ZCMLFileLayer(zope.schemaevent,
                         zcml_file='configure.zcml')
