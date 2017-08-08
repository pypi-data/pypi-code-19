class WorkerMessage:
    def __init__(self, basic_deliver, properties, body):
        self.body = body
        self.basic_deliver = basic_deliver
        self.properties = properties
        self.delivery_tag = basic_deliver.delivery_tag
