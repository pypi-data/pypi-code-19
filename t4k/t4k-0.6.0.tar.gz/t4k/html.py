from xml.dom import minidom

# This provisional dom is used as an element factory
DOM = minidom.Document()

def element(tag_name, attributes={}):
    elm = DOM.createElement(tag_name)
    bind_attributes(elm, attributes)
    return elm 

def bind_attributes(element, attributes):
    for attribute in attributes:
        element.setAttribute(attribute, attributes[attribute])
    return element

def div(attributes={}):
    return element('div', attributes)

def span(attributes={}):
    return element('span', attributes)

def text(text_content):
    return DOM.createTextNode(str(text_content))

def table(attributes={}):
    return element('table', attributes)

def tr(attributes={}):
    return element('tr', attributes)

def td(attributes={}):
    return element('td', attributes)


def build_table(fields):
    table_elm = table({'class': 'performance'})
    first_row = True
    for row in fields:
        if first_row:
            tr_elm = table_elm.appendChild(tr({'class': 'first-row'}))
            first_row = False
        else:
            tr_elm = table_elm.appendChild(tr())
                
        first_cell = True
        for cell in row:
            if first_cell:
                td_elm = tr_elm.appendChild(td({'class': 'first-cell'}))
                first_cell = False
            else:
                td_elm = tr_elm.appendChild(td())
            td_elm.appendChild(text(cell))

    return table_elm


class Styler(dict):

    def as_element(self):
        style_element = DOM.createElement('style')
        style_element.appendChild(text('\n' + self.serialize()))
        return style_element

    def serialize(self):
        string = ''
        for rule in self:

            # Open the style rule
            string += '%s {\n' % rule

            # Write each directive
            for directive in self[rule]:
                string += '\t%s: %s;\n' % (directive, self[rule][directive])

            # Close the style rule
            string += '}\n'

        return string
