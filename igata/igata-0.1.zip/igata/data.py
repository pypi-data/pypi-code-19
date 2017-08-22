#-*- coding: utf-8 -*-

config_begin = """
import ntpath
import os
import posixpath
import sys

wl_home = os.environ["WL_HOME"]
if len(sys.argv)<2:
    domain_path = os.path.dirname(sys.argv[0])
else:
    domain_path = sys.argv[1]

if not domain_name:
    domain_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
domain_dir = os.path.normpath(os.path.join(domain_path, domain_name))
domain_root_dir = os.path.join(domain_dir, 'domain-root')
"""

config_end = """
writeConfiguration(domain_env_file_win, '\\n'.join([
    "goto :EOF",
    "",
    ":ReadProperties",
    "for /f usebackq %%o IN (\\"%~1\\") do (",
    "   call :AddToProperties \\"%%o\\"",
    ")",
    "goto :EOF",
    "",
    ":AddToProperties",
    "if NOT \\"%EXTRA_JAVA_PROPERTIES%\\"==\\"\\" (",
    "   set EXTRA_JAVA_PROPERTIES=%EXTRA_JAVA_PROPERTIES% -D%~1",
    ") else (",
    "   set EXTRA_JAVA_PROPERTIES=-D%~1",
    ")",
    "goto :EOF",
    "",
    ":AddToPath",
    "if NOT \\"%EXT_PRE_CLASSPATH%\\"==\\"\\" (",
    "   set EXT_PRE_CLASSPATH=%EXT_PRE_CLASSPATH%;%~dpfn1",
    ") else (",
    "   set EXT_PRE_CLASSPATH=%~dpfn1",
    ")",
    "goto :EOF"
    ]))
exit()
"""

resources_begin = """
connect(admin_user, admin_password, server_url)

edit()
startEdit()
"""

resources_end = """
save()
activate()
disconnect()
exit()
"""

overrides_function =  """
domain_env_file = os.path.join(domain_root_dir, 'bin', 'setUserOverrides')
domain_env_file_win = domain_env_file + '.cmd'
domain_env_file_unix = domain_env_file + '.sh'

def writeConfiguration(filename, text, mode = 'a'):
    try:
        f = open(filename, mode)
        f.write(text)
        f.close()
    except:
        print "Failed to write configuration to %s." % filename
"""

domain = """
readTemplate(os.path.join(wl_home, 'common', 'templates', 'wls', 'wls.jar'))

# Configure the admin server
cd('Servers/AdminServer')
set('ListenAddress','')
set('ListenPort', 7001)

create('AdminServer','SSL')
cd('SSL/AdminServer')
set('Enabled', 'True')
set('ListenPort', 7002)

# Set the domain password for the WebLogic Server administration user
cd('/')
cd('Security/base_domain/User/%s' % {domain[user]})
cmo.setPassword({domain[password]})

setOption('OverwriteDomain', 'true')
writeDomain(domain_root_dir)

closeTemplate()

writeConfiguration(domain_env_file_win, '\\n'.join([
    "@echo off",
    "",
    "@rem WARNING: This file was created from a igata template",
    "@rem Any changes to this file may be lost when regenerating the domain.",
    "",""
    ]),'w')

writeConfiguration(domain_env_file_unix, '\\n'.join([
    "#!/bin/sh",
    "",
    "# WARNING: This file was created from a igata template",
    "# Any changes to this file may be lost when regenerating the domain.",
    "",""
    ]), 'w')
"""

# Create custom configuration
pre_classpath_dir = """
pre_classpath = '{domain[pre-classpath-dir]}'
pre_classpath_path = os.path.join(domain_dir, pre_classpath)

try:
    os.mkdir(pre_classpath_path)
except:
    print "Directory %s does already exist" % pre_classpath_path

writeConfiguration(domain_env_file_win, '\\n'.join([
    "@rem Configuration for pre-classpath directory",
    "for %%%%a in (\\"%%DOMAIN_HOME%%/../%s/*\\") do (" % pre_classpath,
    "   call :AddToPath \\"%%DOMAIN_HOME%%/../%s/%%%%~nxa\\"" % pre_classpath,
    ")",
    "echo EXT_PRE_CLASSPATH=%EXT_PRE_CLASSPATH%",
    "",""
    ]))

writeConfiguration(domain_env_file_unix, '\\n'.join([
    "for i in $DOMAIN_HOME/../%s/*; do" % pre_classpath,
    "   if [ ! \\"$EXT_PRE_CLASSPATH\\" = \\"\\" ]; then",
    "      EXT_PRE_CLASSPATH=$EXT_PRE_CLASSPATH:$i",
    "   else",
    "      EXT_PRE_CLASSPATH=$i",
    "   fi",
    "done",
    "echo \\"EXT_PRE_CLASSPATH=$EXT_PRE_CLASSPATH\\"",
    "export EXT_PRE_CLASSPATH",
    "",""
    ]))
"""

system_properties_dir = """
system_properties = '{domain[system-properties-dir]}'
system_properties_path = os.path.join(domain_dir, system_properties)
try:
    os.mkdir(system_properties_path)
except:
    print "Directory %s does already exist" % system_properties_path

writeConfiguration(domain_env_file_win, '\\n'.join([
    "@rem Configuration for system properties directory",
    "for %%%%a in (\\"%%DOMAIN_HOME%%/../%s/*\\") do (" % system_properties,
    "   call :ReadProperties \\"%%DOMAIN_HOME%%/../%s/%%%%~nxa\\"" % system_properties,
    ")",
    "echo EXTRA_JAVA_PROPERTIES=%EXTRA_JAVA_PROPERTIES%",
    "",""
    ]))

writeConfiguration(domain_env_file_unix, '\\n'.join([
    "for i in $DOMAIN_HOME/../%s/*; do" % system_properties,
    "   while read -r line || [[ -n \\"$line\\" ]]; do",
    "      if [ ! \\"$EXTRA_JAVA_PROPERTIES\\" = \\"\\" ]; then",
    "         EXTRA_JAVA_PROPERTIES=\\"$EXTRA_JAVA_PROPERTIES -D$line\\"",
    "      else",
    "         EXTRA_JAVA_PROPERTIES=-D$line",
    "      fi",
    "   done < \\"$i\\"",
    "done",
    "echo \\"EXTRA_JAVA_PROPERTIES=$EXTRA_JAVA_PROPERTIES\\"",
    "export EXTRA_JAVA_PROPERTIES",
    "",""
]))
"""

data_source_function = """
def addDataSource(name, jndiName, databaseName, host, portNumber, user, password):
    dsURL = 'jdbc:db2://%(host)s:%(portNumber)s/%(databaseName)s' % {'host': host, 'portNumber': portNumber, 'databaseName' : databaseName}
    dsDriver = 'com.ibm.db2.jcc.DB2XADataSource'

    cd('/')
    if cmo.lookupJDBCSystemResource(name):
        print "JDBC resource %s does already exist. Skipping..." % name
        return
    print "Creating JDBC resource %s." % name
    systemResource = cmo.createJDBCSystemResource(name)
    systemResource.setTargets(jarray.array([getMBean('/Servers/AdminServer')], weblogic.management.configuration.TargetMBean))

    resource = systemResource.getJDBCResource()
    resource.setName(name)
    resource.setDatasourceType('GENERIC')

    dataSourceParams = resource.getJDBCDataSourceParams()
    dataSourceParams.setJNDINames(jarray.array([String(jndiName)], String))
    dataSourceParams.setGlobalTransactionsProtocol('OnePhaseCommit')

    driverParams = resource.getJDBCDriverParams()
    driverParams.setUrl(dsURL)
    driverParams.setDriverName(dsDriver)
    driverParams.setPassword(password)

    properties = driverParams.getProperties()
    properties.createProperty('user', user)
    properties.createProperty('portNumber', portNumber)
    properties.createProperty('databaseName', databaseName)
    properties.createProperty('serverName', host)
    properties.createProperty('batchPerformanceWorkaround', 'true')
    properties.createProperty('driverType', '4')

    resource.getJDBCConnectionPoolParams().setTestTableName('SQL SELECT COUNT(*) FROM SYSIBM.SYSDUMMY1\\r\\n')
"""

data_source = """
addDataSource('{dataSource[name]}', '{dataSource[jndiName]}', '{dataSource[databaseName]}', '{dataSource[host]}', '{dataSource[portNumber]}', '{dataSource[user]}', '{dataSource[password]}')
"""

wtc_function = """
import socket
wtc_server = 'WTCServer'
local_access_point = socket.gethostname()
def addWTCServer():
    cd('/')
    if cmo.lookupWTCServer(wtc_server):
        return
    server = cmo.createWTCServer(wtc_server)

    server.setTargets(jarray.array([getMBean('/Servers/AdminServer')], weblogic.management.configuration.TargetMBean))

def addLocalAccessPoint():
    addWTCServer()
    cd('/WTCServers/%(wtcServer)s' % {'wtcServer' : wtc_server})
    if cmo.lookupWTCLocalTuxDom(local_access_point):
        return
    local_network_address = '//localhost:7003'
    localAP = cmo.createWTCLocalTuxDom(local_access_point)

    localAP.setAccessPoint(local_access_point)
    localAP.setAccessPointId(local_access_point)
    localAP.setNWAddr(local_network_address)
    localAP.setConnectionPolicy('ON_STARTUP')
    localAP.setRetryInterval(60)
    localAP.setInteroperate('Yes')

def addRemoteAccessPoint(remote_access_point, networkAddress):
    addLocalAccessPoint()
    cd('/WTCServers/%(wtcServer)s' % {'wtcServer' : wtc_server})
    if cmo.lookupWTCRemoteTuxDom(remote_access_point):
        return
    remoteAP = cmo.createWTCRemoteTuxDom(remote_access_point)

    remoteAP.setAccessPoint(remote_access_point)
    remoteAP.setAccessPointId(remote_access_point)
    remoteAP.setLocalAccessPoint(local_access_point)
    remoteAP.setNWAddr(networkAddress)
    remoteAP.setConnectionPolicy('ON_STARTUP')
    remoteAP.setAclPolicy('GLOBAL')
    remoteAP.setCredentialPolicy('GLOBAL')
    remoteAP.setAllowAnonymous(true)

def addExportedService(service_name, ejb_name):
    cd('/WTCServers/%(wtcServer)s' % {'wtcServer' : wtc_server})
    if cmo.lookupWTCExport(service_name):
        print "Exported service %s does already exist. Skipping..." % service_name
        return
    print "Creating exported service %s." % service_name
    service = cmo.createWTCExport(service_name)

    service.setResourceName(service_name)
    service.setLocalAccessPoint(local_access_point)
    service.setEJBName(ejb_name)
    service.setRemoteName('')

def addImportedService(service_name, remote_access_point):
    cd('/WTCServers/%(wtcServer)s' % {'wtcServer' : wtc_server})
    if cmo.lookupWTCImport(service_name):
        print "Imported service %s does already exist. Skipping..." % service_name
        return
    print "Creating imported service %s." % service_name
    service = cmo.createWTCImport(service_name)

    service.setResourceName(service_name)
    service.setLocalAccessPoint(local_access_point)
    service.setRemoteAccessPointList(remote_access_point)
    service.setRemoteName('')
"""

wtc_export_begin = """
addLocalAccessPoint()
"""

wtc_import_begin = """
addRemoteAccessPoint()
"""

wtc_exported_service = """
addExportedService('{service[name]}', '{service[ejbName]}')
"""

wtc_remote_access_point = """
remote_access_point = '{remoteAccessPoint[name]}'
addRemoteAccessPoint(remote_access_point, '{remoteAccessPoint[networkAddress]}')
"""

wtc_imported_service = """
addImportedService('{service[name]}', remote_access_point)
"""

jms_function = """
jms_server = 'JMSServer'
jms_module = 'JMSModule'
jms_subdep = 'SubDeployment'
def addJMSServer():
    cd('/')
    if cmo.lookupJMSServer(jms_server):
        return
    server = cmo.createJMSServer(jms_server)

    server.setTargets(jarray.array([getMBean('/Servers/AdminServer')], weblogic.management.configuration.TargetMBean))

def addJMSModule():
    addJMSServer()
    cd('/')
    if cmo.lookupJMSSystemResource(jms_module):
        return
    module = cmo.createJMSSystemResource(jms_module)

    module.setTargets(jarray.array([getMBean('/Servers/AdminServer')], weblogic.management.configuration.TargetMBean))

    subdep = module.createSubDeployment(jms_subdep)
    subdep.setTargets(jarray.array([getMBean('/JMSServers/%s' % jms_server)], weblogic.management.configuration.TargetMBean))

def addConnectionFactory(name, jndiName):
    cd('/JMSSystemResources/%(jmsModule)s/JMSResource/%(jmsModule)s'  % {'jmsModule' : jms_module})
    if cmo.lookupConnectionFactory(name):
        print "Connection factory %s does already exists. Skipping..." % name
        return
    print "Creating connection factory %s." % name
    connectionFactory = cmo.createConnectionFactory(name)

    connectionFactory.setJNDIName(jndiName)
    connectionFactory.setSubDeploymentName(jms_subdep)

    connectionFactory.getTransactionParams().setXAConnectionFactoryEnabled(true)

def addQueue(name, jndiName):
    cd('/JMSSystemResources/%(jmsModule)s/JMSResource/%(jmsModule)s'  % {'jmsModule' : jms_module})
    if cmo.lookupQueue(name):
        print "Queue %s does already exists. Skipping..." % name
        return
    print "Creating queue %s." % name
    queue = cmo.createQueue(name)

    queue.setJNDIName(jndiName)
    queue.setSubDeploymentName(jms_subdep)
"""

jms_begin = """
addJMSServer()
addJMSModule()
"""

connection_factory = """
addConnectionFactory('{factory[name]}', '{factory[jndiName]}')
"""

queue = """
addQueue('{queue[name]}', '{queue[jndiName]}')
"""

