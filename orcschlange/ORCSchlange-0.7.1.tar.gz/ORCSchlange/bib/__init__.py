"""The bib module that contains classes that represent the bibliographic objects and how output them from ORCID."""
from pybtex.backends.html import Backend
from pybtex.style.formatting.plain import Style
from pybtex.richtext import Tag, Text, Symbol, HRef
from pybtex.io import get_default_encoding

from itertools import count


class Date:
    """The date class that can not contain month or day of the month."""
    
    def __init__(self, y, m, d):
        """Save year, month, and day of the month.

        :param y: The year.
        :param m: The month.
        :param d: The day of the month.
        """
        self.y = int(y) if y else None
        self.m = int(m) if m else None
        self.d = int(d) if d else None
    
    def __check(self, other, attr):
        """Compare the date with an other date by a specific attribute.

        :param other: The other date that is compared.
        :param attr: The attribute on which they are compared (y, m or d).
        :return: 1 if self<other or one None, -1 if other >self and 0 if they are equal.
        """
        if getattr(self, attr) is None or getattr(other, attr) is None:
            return 1
        if getattr(self, attr) < getattr(other, attr):
            return 1
        if getattr(self, attr) > getattr(other, attr):
            return -1
        return 0
    
    def __le__(self, other):
        """Check if this Date is smaller or equal then the other Date

        If they are equal until one or both of them have a parameter with None True is returned.
        These create no total order but an partial order that is enough for an filtering.
        :param other: The other Date.
        :return: True if self is smaller or equal then the other Date.
        """
        return True if 1 == (
            self.__check(other, "y") or self.__check(other, "m") or self.__check(other, "d") or 1) else False
    
    def __str__(self):
        """ Create string representation in form "YYYY-MM-DD".

        :return: Date in form "YYYY-MM-DD".
        """
        return str(self.y) + ("-{:02d}".format(self.m) + ("-{:02d}".format(self.d) if self.d else "") if self.m else "")


class WorkSummary:
    """The summary of a work it contains the basic data of a work."""
    
    def __init__(self, orcid, putcode, title, date):
        """Save the data of the work.
        
        :param orcid: The orcid where the work is from.
        :param putcode: The code that identify the work.
        :param title: The title of the work.
        :param date: The publication date of the work.
        """
        self.orc = orcid
        self.id = putcode
        self.title = title
        self.date = date
    
    def __lt__(self, other):
        """Check these WorkSummary is smaller then an other WorkSummary. In respect of the publication year and the title.
        
        :param other: The other WorkSummary.
        :return: True if these WorkSummary is smaller.
        """
        return self.date.y < other.date.y or (self.date.y == other.date.y and self.title < other.title)
    
    def __eq__(self, other):
        """Check if these WorkSummary is equal to an other WorkSummary. In respect of the publication year and the title.
        
        :param other: The other WorkSummary.
        :return: True if the WorkSummary are equal
        """
        return self.date.y == other.date.y and self.title == other.title
    
    def __str__(self):
        """Make a string with the title and the date of the WorkSummary.
        
        :return: "*title*:*date*"
        """
        return self.title + ": " + str(self.date)
    
    def __getattr__(self, name):
        """Function to get a indirect attribute path.
        
        :param name: The name of the parameter
        :return: the path of name os path.
        """
        if name == "path":
            return "/{orc}/work/{id}".format(orc=self.orc.get_id(), id=self.id)
        raise AttributeError()


def it_name(name):
    """Small helper functions that iterate over name and append a number at the end.
    
    These function is used to iterate over possible names of a Work until an unique name is found.
    
    :param name: The starting name of the iteration
    :return: An possible name that is expandet with a number.
    """
    yield name
    for i in count(2):
        yield "{0}_{1}".format(name, i)


def join_bibliography(bib1, bib2):
    """Add all entries of the second bibliography to the first bibliography.
    
    Iterate over the second bibliography and add it to the first if the key is unique.
    If this is not the case the key is appended with a number until a unique key is found.
    
    :param bib1: The first bibliography that is appended.
    :param bib2: THe second bibliography which is appended to the first.
    """
    for key in bib2.entries:
        for name in it_name(key):
            if name not in bib1.entries:
                bib1.entries[name] = bib2.entries[key]
                break


class HtmlTag(Tag):
    """An extension of the normal richText Tag that contains an additional options field.
    
    For HTML it make sens to add options like "style" to some tags. So these HtmlTag can be used.
    However, all other Backends ignore the extra inforamtion and handel it like a normal Tag.
    """
    
    def __init__(self, name, opt, *args):
        """Save tha opt inforamtion and then call the normal Tag initialization.
        
        :param name: The name of the Tag.
        :param opt: The html options of the Tag.
        :param args: Other args of the Tag.
        """
        super(HtmlTag, self).__init__(name, *args)
        self.options = opt
    
    def render(self, backend):
        """Render the Tag with the addional options.
        
        When rendered it is tried to use a format_tag function of the backend that gets a options field.
        If no function exists the normal format_tag function without the additional information is called.
        
        :param backend: The Backend that is used to render the Tag.
        :return: The rendered Tag.
        """
        text = super(Tag, self).render(backend)
        try:
            return backend.format_tag(self.name, text, options=self.options)
        except TypeError:
            return backend.format_tag(self.name, text)


class HtmlStyle(Style):
    """A style that extends the plain Style with a nice html formating of the article entries."""
    
    def format_article(self, context):
        """Format an articale for a nice html rendering.
        
        :param context: The context of the that contain all information.
        :return: A RichText representation of the html rendering.
        """
        ret = Text()
        ret += HtmlTag("h4", "style=\"margin-bottom: 2px;\"", context.rich_fields['title'])
        ret += Tag("i", context.rich_fields['author']) + Symbol('newblock')
        ret += context.rich_fields['journal']
        if 'volume' in context.fields:
            ret += Symbol("nbsp") + context.rich_fields['volume']
        if 'number' in context.fields:
            ret += Symbol("nbsp") + "(" + context.rich_fields['number'] + ")"
        if 'pages' in context.fields:
            ret = ret + ":" + context.rich_fields['pages']
        if 'doi' in context.fields:
            ret += Symbol('newblock') + HRef('https://doi.org/' + context.fields['doi'], "[ Publishers's page ]")
        return HtmlTag("div", "class=\"" + context.fields['year'] + " mix \"", ret)


class HtmlBackend(Backend):
    """The Backend that render the html output."""
    symbols = {'ndash': u'&ndash;', 'newblock': u'<br/>\n', 'nbsp': u'&nbsp;'}
    label = None
    
    def format_tag(self, tag, text, options=None):
        """Render an HtmlTag or an Tag for html.
        
        Render an Tag into an DOM object that is of the type like the name of the Tag is.
        If the optinal options argument is given put the options in the openning Tag.
        
        :param tag: The name of the tag i.e. the Tag type
        :param text: The rendered text that is put in the Tag.
        :param options: The html options of the Tag.
        :return: The rendered Tag.
        """
        return u'<{0} {2} >{1}</{0}>'.format(tag, text, options if options else "") if text else u''
    
    def write_entry(self, key, label, text):
        """Write an entry to the output.
        
        Write an entry to the ouput.
        If a new year is reached with these entry it is render as headline before the entry.
        
        :param key: The key of the entry (is unused).
        :param label: The label of the entrie i.e. the publication year.
        :param text: The rendered entry.
        """
        if label != self.label:
            self.output(u'<h3 class=\"{0} year\">{0}</h3>\n'.format(label))
            self.label = label
        self.output(u'%s\n' % text)
    
    def write_prologue(self):
        """Write the header and the body content until the entries are reached."""
        prologue = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
        <html>
        <head><meta name="generator" content="Pybtex">
        <meta http-equiv="Content-Type" content="text/html; charset=%s">
        <title>Bibliography</title>
        <script src="jquery-3.2.1.min.js"></script>
        <script type="text/javascript">
        $(function(){
            search = $(".filter-input input[type='search']")
            search.keyup(function(){
                inputText = search.val().toLowerCase()
                $('.mix').each(function() {
                    var $this = $(this);
                    if(($this.attr('class') + $this.text()).toLowerCase().match(inputText) ) {
                        $(this).show()
                    }
                    else {
                        $(this).hide()
                    }
                });
                $('.year').each(function() {
                    if ($("."+$(this).text()+ ".mix").is(":visible")) $(this).show()
                    else $(this).hide()
                });
            })
        })
        
        </script>
        </head>
        <body>
        <div class="filter-input">
            <input type="search" placeholder="Try unicorn">
        </div>
        <div id="content">
        """
        encoding = self.encoding or get_default_encoding()
        self.output(prologue % encoding)
    
    def write_epilogue(self):
        """Write the closing tags of the body and html."""
        return self.output(u'</div></body></html>\n')


def write_html(bib, path):
    """Write an bibliography into a path as html.
    
    :param bib: The bibliography that should be written
    :param path: The path of the file where the html is written.
    """
    style = HtmlStyle()
    style.sort = lambda x: sorted(x, key=lambda e: -int(e.fields['year']))
    style.format_labels = lambda x: [int(e.fields['year']) for e in x]
    formatbib = style.format_bibliography(bib)
    HtmlBackend().write_to_file(formatbib, path)
