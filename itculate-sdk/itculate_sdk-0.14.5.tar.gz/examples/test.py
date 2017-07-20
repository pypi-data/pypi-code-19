tenant_id = "21U3CdOpgico32Py9BUHfg"
api_key = "5PLZZM6T94UPTXOUS3LPW2AN0"
api_secret = "+r7BEShhSmDldVgwxQa3NgXcJloiOVhxsLVvDvpqIlQ"
server_url = "https://api.itculate.io/api/v1"


import itculate_sdk as itsdk
itsdk.init(server_url=server_url, api_secret=api_secret, api_key=api_key)

hello_vertex = itsdk.add_vertex(name="Hello", vertex_type="hello-type", keys="hello-key", collector_id="cid")

itsdk.flush_all()