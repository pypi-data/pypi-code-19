from oglhclient import LighthouseApiClient
api = LighthouseApiClient()
client = api.get_client()
print client.nodes.ports.list(parent_id='demo-im')
