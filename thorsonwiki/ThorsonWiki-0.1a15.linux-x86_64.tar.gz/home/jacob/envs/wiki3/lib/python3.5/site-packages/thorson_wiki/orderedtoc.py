from markdown.extensions.toc import TocExtension, TocTreeprocessor
from markdown.util import etree
from six import text_type

class _OrderedTocTreeprocessor(TocTreeprocessor):

    def __init__(self, md, config):

        super(_OrderedTocTreeprocessor, self).__init__(md, config)

        # Ensure that the title is a real string, not a proxy
        self.title = text_type(self.title)

    def build_toc_div(self, toc_list):
        """
        Return a string div given a toc list.
        """

        div = etree.Element('div')
        div.attrib['class'] = "toc"

        # Add title to the div
        if self.title:
            header = etree.SubElement(div, "div")
            header.attrib['class'] = "toctitle"
            header.text = self.title

        def build_etree_ol(toc_list, parent):
            ol = etree.SubElement(parent, 'ol')
            for item in toc_list:
                # List item link, to be inserted into the toc div
                li = etree.SubElement(ol, 'li')
                link = etree.SubElement(li, 'a')
                link.text = item.get('name', '')
                link.attrib['href'] = '#' + item.get('id', '')
                if item['children']:
                    build_etree_ol(item['children'], li)

            return ol

        build_etree_ol(toc_list, div)
        prettify = self.markdown.treeprocessors.get('prettify')
        if prettify:
            prettify.run(div)

        return div

class OrderedTocExtension(TocExtension):
    """
    An improved TOC for markdown which uses an ordered list for the table of
    contents.
    """

    TreeProcessorClass = _OrderedTocTreeprocessor

def makeExtension(*args, **kwargs):

    return OrderedTocExtension(*args, **kwargs)
