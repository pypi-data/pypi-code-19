from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_core_device._private.PluginNames import deviceFilt
from peek_core_device._private.PluginNames import deviceObservableName
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler


def makeDeviceTupleDataObservableProxy():
    return TupleDataObservableProxyHandler(observableName=deviceObservableName,
                                           proxyToVortexName=peekServerName,
                                           additionalFilt=deviceFilt)
