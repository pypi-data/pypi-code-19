import time


class Task(object):

    def __init__(self, *,
                 name,
                 inputter,
                 processor,
                 outputter,
                 deserializer=None,
                 serializer=None):
        self.name = name
        self.inputter = inputter
        self.processor = processor
        self.outputter = outputter
        self.deserializer = deserializer
        self.serializer = serializer

    def do(self):
        context = self.inputter.read()
        body = context.body
        if self.deserializer is not None:
            body = self.deserializer.deserialize(body)
        for d in self.processor.process(body, context=context):
            job_name = self.name
            class_name = self.processor.__class__.__name__
            metadatakey = 'processed_time_{}_{}'.format(job_name, class_name)
            timestamp = int(time.time())
            context.add_metadata(**{metadatakey: timestamp})
            if self.serializer is not None:
                d = self.serializer.serialize(d)
            self.outputter.write(d, context=context)
        self.inputter.done()
