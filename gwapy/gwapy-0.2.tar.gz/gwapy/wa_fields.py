from xml.dom.minidom import getDOMImplementation

impl = getDOMImplementation()


class WaList:
    def __init__(self, sword, pword, name):
        self.sword = sword
        self.pword = pword
        self.name = name
        self.items = []

    def __str__(self):
        doc = impl.createDocument(None, "list", None)
        list = doc.documentElement
        list.setAttribute('sword', self.sword)
        list.setAttribute('name', self.name)
        for itemStr in self.items:
            item = doc.createElement('item')
            item.appendChild(doc.createTextNode(itemStr))
            list.appendChild(item)
        return list.toprettyxml()

    def add(self, value):
        self.items.append(value)


class WaFft:
    def __init__(self, sword, pword, name, mandatory):
        self.sword = sword
        self.pword = pword
        self.name = name
        self.mandatory = mandatory == 'Y'
        self.lines = []

    def __str__(self):
        doc = impl.createDocument(None, "fft", None)
        fft = doc.documentElement
        fft.setAttribute('sword', self.sword)
        fft.setAttribute('name', self.name)
        for lineStr in self.lines:
            line = doc.createElement('line')
            line.appendChild(doc.createTextNode(lineStr))
            fft.appendChild(line)
        return fft.toprettyxml()

    def add(self, value):
        self.lines.append(value)

    def getValue(self, index):
        return self.lines[index]

    def getValues(self):
        return self.lines


class WaField:
    def __init__(self, sword, pword, name, mandatory):
        self.sword = sword
        self.pword = pword
        self.name = name
        self.mandatory = mandatory == 'Y'

    def __str__(self):
        doc = impl.createDocument(None, "field", None)
        field = doc.documentElement
        value = doc.createTextNode(self.value)
        field.appendChild(value)
        field.setAttribute("sword", self.sword)
        field.setAttribute("name", self.name)
        return field.toprettyxml()

    def set(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def isValueSet(self):
        try:
            self.value
        except:
            return False
        return True
