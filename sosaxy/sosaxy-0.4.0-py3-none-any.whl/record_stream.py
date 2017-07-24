import xml.sax

class RecordStream():
    record_number = 0

    def __init__(self, input_file, document_node, fields, on_record):
        self.input_file = input_file
        self.document_node = document_node
        self.fields = fields
        self.on_record = on_record

    def play(self):
        try:
            content_handler = self.RecordStreamContentHandler(self)
            parser = xml.sax.make_parser()
            parser.setContentHandler(content_handler)
            parser.parse(self.input_file)
        except StopIteration:
            pass

    class RecordStreamContentHandler(xml.sax.handler.ContentHandler):
        root = None
        current_dict = None 
        capture_text = False
        current_text = [] 
        name_stack = []
        o_stack = []

        def __init__(self, outer):
            self.outer = outer

        def startElement(self, name, attrs):
            if name == self.outer.document_node:
                self.outer.record_number = self.outer.record_number + 1
                self.current_dict = {}
                self.o_stack.append(self.current_dict)
            elif name == self.root and not self.root:
                self.root = name

            if self.current_dict != None:
                n = self.clean_name(name)
                self.name_stack.append(n)

                o = {}
                self.set_dict_value(self.o_stack[-1], n, o)
                self.o_stack.append(o)

                if self.current_path() in self.outer.fields:
                    self.capture_text = True
                    self.current_text = []

                for k in attrs.keys():
                    path = "{}/@{}".format(self.current_path(), k) 
                    if path in self.outer.fields:
                        k2 = self.clean_name(k)
                        self.set_dict_value(o, k2, attrs[k])

        def endElement(self, name):
            if self.current_dict != None:
                if self.current_path() in self.outer.fields:
                    content = ''.join(self.current_text).strip()
                    self.set_dict_value(self.o_stack[-1], 'text', content)

                self.capture_text = False
                self.current_text = []

                self.name_stack.pop()
                self.o_stack.pop()

                if name == self.outer.document_node:
                    self.outer.on_record(self.current_dict[self.outer.document_node])
                    self.current_dict = None
                    self.name_stack = []
                    self.o_stack = []

            if name == self.root:
                raise StopIteration

        def characters(self, content):
            if self.capture_text:
                self.current_text.append(content)

        def clean_name(self, n):
            return n.replace(':', '_')

        def current_path(self):
            return '/'.join([n for n in self.name_stack])

        def set_dict_value(self, o, key, value):
            if key in o:
                if not type(o[key]) is list:
                    prev = o[key]
                    o[key] = [prev]

                o[key].append(value)
            else:
                o[key] = value
