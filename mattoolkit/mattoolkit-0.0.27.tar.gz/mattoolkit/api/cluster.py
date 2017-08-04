from .resource import ResourceList, ResourceItem


class ClusterResourceItem(ResourceItem):
    def __init__(self, id):
        super().__init__('compute/clusters', id)

    @property
    def username(self):
        return self.data['username']

    @username.setter
    def username(self, value):
        self.data['username'] = value

    @property
    def port(self):
        return self.data['port']

    @port.setter
    def port(self, value):
        self.data['port'] = value

    @property
    def hostname(self):
        return self.data['hostname']

    @hostname.setter
    def hostname(self, value):
        self.data['hostname'] = value

    @property
    def uri(self):
        return '{}@{}:{}'.format(self.username, self.hostname, self.port)

    @property
    def public_key(self):
        return self.data['public_key']

    @property
    def queues(self):
        return self.data['queues']

    @queues.setter
    def queues(self, value):
        if not isinstance(value, list):
            raise ValueError('queues must be list')

        for label in value:
            if not isinstance(label, str):
                raise ValueError('each element in queues must be string')
        self.data['queues'] = value

    @property
    def scratch_directory(self):
        return self.data['scratch_directory']

    @scratch_directory.setter
    def scratch_directory(self, value):
        self.data['scratch_directory'] = value

    def __repr__(self):
        if self.data:
            return f'<{self.__class__.__name__}: id: {self.id}, uri:{self.uri}>'
        else:
            return f'<{self.__class__.__name__}: id: {self.id}>'


class ClusterResourceList(ResourceList):
    ITEM = ClusterResourceItem

    def __init__(self):
        super().__init__('compute/clusters')


class ClusterJobResourceItem(ResourceItem):
    def __init__(self, id):
        super().__init__('compute/clusterjobs', id)

    @property
    def cluster(self):
        cluster_rec = ClusterResourceItem(self.data['cluster'])
        cluster_rec.get()
        return cluster_rec

    @classmethod
    def create(cls, calculation, cluster, queue, time, cores):
        from .calculation import CalculationResourceItem
        if not isinstance(calculation, CalculationResourceItem) or calculation.id == None:
            raise ValueError('calculation must be of type CalculationResorsceItem and have id')

        if not isinstance(cluster, ClusterResourceItem) or cluster.id == None:
            raise ValueError('cluster must be of type ClusterResorsceItem and have id')

        if queue not in cluster.queues:
            raise ValueError('queue must exist on cluster')

        cluster_job_rec = cls(None)
        cluster_job_rec.data= {
            'calculation': calculation.id,
            'cluster': cluster.id,
            'queue': queue,
            'time': time,
            'cores': cores
        }
        return cluster_job_rec

    @property
    def status(self):
        return self.data['status']

    @property
    def script(self):
        return self.data['script']

    @property
    def job_id(self):
        return self.data['job_id']

    @property
    def directory(self):
        return self.data['directory']

    @property
    def queue(self):
        return self.data['queue']

    @queue.setter
    def queue(self, value):
        self.data['queue'] = value

    @property
    def time(self):
        return self.data['time']

    @time.setter
    def time(self, value):
        self.data['time'] = value

    @property
    def cores(self):
        return self.data['cores']

    @cores.setter
    def cores(self, value):
        self.data['cores'] = value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.data)



class ClusterJobResourceList(ResourceList):
    ITEM = ClusterJobResourceItem

    def __init__(self):
        super().__init__('compute/clusterjobs')
