import itculate_sdk as itsdk

itsdk.init(server_url="https://api.itculate.io/api/v1")


#############################
# create topology
#############################


hello_vertex = itsdk.add_vertex(name="Hello", vertex_type="hello-type", keys="hello-key", collector_id="cid")
world_vertex = itsdk.add_vertex(name="World", vertex_type="hello-type", keys="hello-key", collector_id="cid")

itsdk.connect(source=hello_vertex, target=world_vertex, topology="topology", collector_id="cid")


#############################
# publish health event
#############################


itsdk.vertex_unhealthy(vertex=world_vertex, message="Global Warming")


#############################
# publish metric
#############################


itsdk.add_sample(vertex=world_vertex, counter="latency", value=itsdk.LatencyDataType.value(1000))

itsdk.flush_all()
