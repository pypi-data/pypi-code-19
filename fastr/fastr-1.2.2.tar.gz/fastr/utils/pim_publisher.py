import requests
import fastr

from fastr.core.node import MacroNode
from fastr.execution.job import JobState
from fastr import exceptions


class PimPublisher(object):
    """
    Class to publish to PIM
    """
    PIM_STATUS_MAPPING = {
        JobState.nonexistent: 'unknown',
        JobState.created: 'idle',
        JobState.queued: 'idle',
        JobState.hold: 'idle',
        JobState.running: 'running',
        JobState.execution_done: 'running',
        JobState.execution_failed: 'running',
        JobState.processing_callback: 'running',
        JobState.finished: 'success',
        JobState.failed: 'failed',
        JobState.cancelled: 'failed',
    }

    def __init__(self, uri=None):
        if uri is None and fastr.config.pim_host == '':
            fastr.log.info("No valid PIM host given, PIM publishing will be disabled!")
            self.pim_uri = None
        else:
            self.pim_uri = uri or fastr.config.pim_host
        self.registered = False
        self.run_id = None

    def pim_update_status(self, job):
        if not self.registered:
            fastr.log.debug('Did not register a RUN with PIM yet! Cannot'
                            ' send status updates!')
            return

        run_id = job.run_id

        # Create PIM job data
        pim_job_data = {
            "id": job.id,
            "node_id": job.node_id,
            "run_id": run_id,
            "sample_id": str(job.sample_id),
            "status": self.PIM_STATUS_MAPPING[job.status]
        }

        # Send the data to PIM
        fastr.log.debug('Updating PIM job status {} => {} ({})'.format(job.id,
                                                                       job.status,
                                                                       self.PIM_STATUS_MAPPING[job.status]))
        uri = '{pim}/api/runs/{run_id}/jobs/{job_id}'.format(pim=fastr.config.pim_host,
                                                             run_id=run_id,
                                                             job_id=job.id)

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, pim_job_data))
        try:
            response = requests.put(uri, json=pim_job_data)
        except requests.ConnectionError as exception:
            fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))

    @staticmethod
    def pim_serialize_network(network):
        """
        Serialize Network in the correct for to use with PIM.

        :return: json data for PIM
        """
        node_classes = {'Node': 'node',
                        'SourceNode': 'source',
                        'ConstantNode': 'constant',
                        'SinkNode': 'sink'}

        network_data = {
            "description": network.description,
            "nodes": [],
            "links": [],
            "groups": [{"id": 'step_' + x,
                        "description": "undefined",
                        "parent_group": "root"} for x in network.stepids.keys()]
        }

        # Add the nodes
        for node in network.nodelist.values():
            if isinstance(node, MacroNode):
                # MacroNodes are a weird tool-less Node that will fail
                continue

            node_class = node.__class__.__name__
            step = None
            for stepid, nodes in network.stepids.items():
                if node in nodes:
                    step = stepid
                    break

            node_data = {
                "group_id": ('step_' + step) if step else "root",
                "id": node.id,
                "in_ports": [{'id': 'in_' + x.id, 'description': x.description} for x in node.tool.inputs.values()],
                "out_ports": [{'id': 'out_' + x.id, 'description': x.description} for x in node.tool.outputs.values()],
                "type": node_classes[node_class] if node_class in node_classes else 'node'
            }

            network_data["nodes"].append(node_data)

        # Add the links
        for link in network.linklist.values():
            link_data = {
                "id": link.id,
                "from_node": link.source.node.id,
                "from_port": 'out_' + link.source.id,
                "to_node": link.target.node.id,
                "to_port": 'in_' + link.target.id,
                "type": link.source.resulting_datatype.id
            }

            network_data["links"].append(link_data)

        return network_data

    def pim_register_run(self, network):
        if self.pim_uri is None:
            fastr.log.debug('No valid PIM uri known. Cannot register to PIM!')
            return

        self.run_id = network.run_id
        pim_run_data = {
            "collapse": False,
            "description": "Run of {} started at {}".format(network.id,
                                                            network.timestamp),
            "id": self.run_id,
            "network": self.pim_serialize_network(network),
            "workflow_engine": "fastr"
        }

        uri = '{pim}/api/runs/'.format(pim=fastr.config.pim_host)
        fastr.log.info('Registering {} with PIM at {}'.format(self.run_id, uri))

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, pim_run_data))

        # Send out the response and record if we registered correctly
        try:
            response = requests.put(uri, json=pim_run_data)
            if response.status_code in [200, 201]:
                self.registered = True
        except requests.ConnectionError as exception:
            fastr.log.error('Could no register network to PIM, encountered'
                            ' exception: {}'.format(exception))
