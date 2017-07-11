from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.snmp.quali_snmp import QualiSnmp
from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from cloudshell.snmp.snmp_parameters import SNMPV2Parameters

snmp = QualiSnmp(SNMPV2Parameters(snmp_community='Aa123456', ip='192.168.42.235'), get_qs_logger())
result = snmp.set(('SNMPv2-MIB', 'sysLocation', "0"), '''''')
print result