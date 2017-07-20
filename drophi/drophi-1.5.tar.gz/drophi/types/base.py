import arrow

class DockerObject():
    PROPERTIES = ()
    def __eq__(self, other):
        return all([getattr(self, p) == getattr(other, p) for p in self.PROPERTIES])

    def diff(self, other):
        return {
            p: (getattr(self, p), getattr(other, p))
            for p in self.PROPERTIES if getattr(self, p) != getattr(other, p)
        }

class Container():
    "A container"
    def __init__(self, image):
        self.image = image

        self.hostname = None
        self.domainname = None
        self.user = None
        self.attachstdin = False
        self.attachstdout = True
        self.attachstderr = True
        self.ports = []
        self.tty = False
        self.openstdin = False
        self.stdinonce = False
        self.env = []
        self.cmd = []
        self.healthcheck = None
        self.args_escaped = False
        self.volumes = []
        self.working_dir = None
        self.entrypoint = None
        self.network_disabled = False
        self.mac_address = None
        self.on_build = None
        self.labels = []
        self.stop_signal = 'SIGTERM'
        self.stop_timeout = 10
        self.shell = None
        self.host_config = None
        self.networking_config = None

    def get_create_payload(self):
        return {
            'Hostname'          : self.hostname,
            'Domainname'        : self.domainname,
            'User'              : self.user,
            'AttachStdin'       : self.attachstdin,
            'AttachStdout'      : self.attachstdout,
            'AttachStderr'      : self.attachstderr,
            'ExposedPorts'      : self.ports,
            'Tty'               : self.tty,
            'OpenStdin'         : self.opnstdin,
            'StdinOnce'         : self.stdinonce,
            'Env'               : self.env,
            'Cmd'               : self.cmd,
            'Healthcheck'       : self.healthcheck,
            'ArgsEscaped'       : self.args_escaped,
            'Image'             : self.image,
            'Volumes'           : [v.to_payload() for v in self.volumes],
            'WorkingDir'        : self.working_dir,
            'Entrypoint'        : self.entrypoint,
            'NetworkDisabled'   : self.network_disabled,
            'MacAddress'        : self.mac_address,
            'OnBuild'           : self.on_build,
            'Labels'            : self.labels,
            'StopSignal'        : self.stop_signal,
            'StopTimeout'       : self.stop_timeout,
            'Shell'             : self.shell,
            'HostConfig'        : self.host_config,
            'NetworkingConfig'  : self.networking_config,
        }

class Service():
    "A service in a docker swarm"
    def __init__(self, name, image, endpoint, id_=None, previous=None, version=None, mounts=None):
        self.endpoint   = endpoint
        self.id         = id_
        self.image      = Image.parse(image) if isinstance(image, str) else image
        self.mounts     = mounts or []
        self.name       = name
        self.previous   = None
        self.version    = version

    def __eq__(self, other):
        if other is None:
            return False
        return all([getattr(self, prop) == getattr(other, prop) for prop in (
            'endpoint', 'image', 'mounts')])

    def __str__(self):
        return "Service {} {}".format(self.name, self.image)

    def __repr__(self):
        return str(self)

    async def apply(self, client):
        if self.old == self.new:
            LOGGER.debug("No changes to %s", self.new.name)
            return
        LOGGER.info("Applying %s", self)
        if self.old:
            payload = drophi.serializer.Service.to_payload(self.new)
            await client.service_update(
                self.old.id,
                self.old.version,
                payload,
            )
        else:
            await client.service_create()
        await asyncio.gather(*self.done_callbacks)

class Port():
    def __init__(self, name, published, target, protocol='tcp', mode='ingress'):
        self.name       = name
        self.protocol   = protocol
        self.mode       = mode
        self.published  = published
        self.target     = target

    def __eq__(self, other):
        return all([getattr(self, p) == getattr(other, p) for p in (
            'protocol', 'mode', 'published', 'target')])

    @staticmethod
    def parse(payload):
        return Port(
            mode        = payload['PublishMode'],
            name        = payload.get('Name'),
            protocol    = payload['Protocol'],
            published   = payload['PublishedPort'],
            target      = payload['TargetPort'],
        )

    def to_service_payload(self):
        return {
            'Name'              : self.name,
            'Protocol'          : self.protocol,
            'PublishedPort'     : self.published,
            'TargetPort'        : self.target,
        }

class Mount():
    def __init__(self, source, target, type='volume', readonly=True):
        self.readonly   = readonly
        self.source     = source
        self.target     = target
        self.type       = type

    def __eq__(self, other):
        return all([getattr(self, p) == getattr(other, p) for p in (
            'readonly', 'source', 'target', 'type')])

    def to_payload(self):
        return '{source}:{target}:{flag}'.format(
            source  = self.source,
            target  = self.target,
            flag    = 'ro' if self.readonly else 'rw',
        )

class Volume():
    def __init__(self, name, driver='local', labels=None, mountpoint=None, options=None, scope='local'):
        self.driver     = driver
        self.labels     = labels or {}
        self.mountpoint = mountpoint
        self.options    = options
        self.name       = name
        self.scope      = scope

    async def apply(self, client):
        if self.old == self.new:
            LOGGER.debug("No changes to %s", self.new.name)
            return
        LOGGER.info("Applying %s", self)
        if self.old:
            payload = drophi.serializer.Volume.to_payload(self.new)
            await client.volume_update(payload)
        else:
            volume = drophi
        await asyncio.gather(*self.done_callbacks)
