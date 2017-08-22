from collections import namedtuple

import data
from script import *

Credentials = namedtuple('Credentials', ['user', 'password'])

def Configuration(name = None):
    """
    Configuration

    A block with configuration for a domain.

    Shall be used in a 'with statement'.

    with Configuration('scriptname'):
       PreClasspathDir()
    """
    if not name:
        # Use same name as template file
        name = os.path.splitext(os.path.basename(sys.argv[2]))[0]
    return scope(name, 'config')

def Resources(name = None):
    """
    Resources

    Creates the resources of the domain.

    Shall be used in a 'with statement'.

    with Resources('scriptname'):
        DefaultConnectionFactory()
    """
    if not name:
        # Use same name as template file
        name = os.path.splitext(os.path.basename(sys.argv[2]))[0] + '_resources'
    add_pre_script_definition('server_url', 't3://localhost:7001')
    return scope(name, 'resources')

def Domain(name, credentials):
    """
    Domain

    Create a new domain.

    Only to use in a configuration block
    """
    if state().block and state().block != 'config':
        raise SyntaxError('Domain can only be used in a configuration block')

    add_pre_script_definition('domain_name', name)
    add_pre_script_definition('admin_user', credentials.user )
    add_pre_script_definition('admin_password', credentials.password )
    print data.domain.format(domain={'user' : 'admin_user', 'password' : 'admin_password'})

def PreClasspathDir(dirname = 'pre-classpath'):
    """
    PreClasspathDir

    Create configuration for a pre-classpath dir.
    """
    print data.pre_classpath_dir.format(domain={'pre-classpath-dir': dirname})

def SystemPropertiesDir(dirname = 'system-properties'):
    """
    SystemProperty

    Creates configuration for a system-properties dir.
    """
    print data.system_properties_dir.format(domain={'system-properties-dir': dirname})

def DataSource(jndiName, databaseName, host, portNumber, credentials):
    """
    DataSource

    Create a new data source.

    Only to use in a resource block
    """
    if state().block and state().block != 'resources':
        raise SyntaxError('DataSource can only be used in a resources block')

    print data.data_source.format(dataSource = {
      'name': databaseName,
      'jndiName': jndiName,
      'databaseName': databaseName,
      'host': host,
      'portNumber': portNumber,
      'user' : credentials.user,
      'password': credentials.password})

def WTCExport():
    """
    WTCExport

    Exports local services.

    Only to use in a resource block.
    """
    if state().block and state().block != 'resources':
        raise SyntaxError('WTCExport can only be used in a resources block')

    return subscope('wtc-export')

def WTCImport(name, networkAddress):
    """
    WTCImport

    Imports remote services.

    Only to use in a resource block.
    """
    if state().block and state().block != 'resources':
        raise SyntaxError('WTCImport can only be used in a resources block')

    add_pre_block_definition('remote-access-point', name)
    add_pre_block_definition('remote-network-address', networkAddress)
    return subscope('wtc-import-' + name)

def Service(name, ejbName = ''):
    """
    Service

    Define local or remote  service. EJB name is only used for local services.
    """
    if state().subblock == 'wtc-export':
        print data.wtc_exported_service.format(service = { 'name' : name, 'ejbName' : ejbName})
    elif state().subblock.startswith('wtc-import'):
        print data.wtc_imported_service.format(service = { 'name' : name})

def Messaging():
    """
    Messaging

    Creates JMS resources.

    Only to use in a resource block.
    """
    if state().block and state().block != 'resources':
        raise SyntaxError('Messaging can only be used in a resources block')
    return subscope('messaging')

def ConnectionFactory(jndiName):
    """
    ConnectionFactory

    Creates a JMS connection factory.
    """
    print data.connection_factory.format(factory = {'name' : jndiName, 'jndiName' : jndiName})

def Queue(jndiName):
    """
    Queue

    Creates a JMS queue.
    """
    print data.queue.format(queue = {'name' : jndiName, 'jndiName' : jndiName})

