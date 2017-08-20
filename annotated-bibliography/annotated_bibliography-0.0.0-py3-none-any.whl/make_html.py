import hashlib
import sys

import jinja2
import mistune
import pybtex.database as db
from pybtex.style.formatting.unsrt import Style

from annotated_bibliography.util import dict_helper, TAParser


def make_html(bibtex, markdown, output):

    # Parse bibtex
    bib_data = db.parse_file(bibtex, bib_format="bibtex")

    # Parse HTML
    html_parser = TAParser()
    html_parser.feed(mistune.markdown(open(markdown).read()))

    # Adds annotations and tags to bib
    for entry in html_parser.dict.keys():
        bib_data.entries[entry].fields['annotation'] = html_parser.dict[entry][0]
        bib_data.entries[entry].fields['tags'] = html_parser.dict[entry][1]

    # Gets a bib printer and formats it
    bib_printer = Style()
    entries = bib_printer.format_bibliography(bib_data).entries

    # Gets the html text
    authors, titles, venue = zip(*[entry.text.render_as('html').split("\n") for entry in entries])

    # Gets the user tags
    user_tags = [bib_data.entries[entry.key].fields['tags'] for entry in entries]

    # Gets the entry type
    entry_type = [[bib_data.entries[entry.key].type] for entry in entries]

    # Gets the annotations
    annotations = [bib_data.entries[entry.key].fields['annotation'] for entry in entries]

    # Gets the year
    year = [bib_data.entries[entry.key].fields['year'] for entry in entries]

    html_helper = {'range': list(range(len(titles))),
                   'titles': titles,
                   'authors': authors,
                   'venues': venue,
                   'tags': user_tags,
                   'entry_type': entry_type,
                   'annotations': annotations,
                   'year': year}

    # Gets tags helper
    hash_tags = [[hashlib.sha224(tag.encode('utf-8')).hexdigest() for tag in tags] for tags in user_tags]
    tags_helper = dict_helper(user_tags, hash_tags)

    # Gets type helper
    hash_type = [[hashlib.sha224(tag.encode('utf-8')).hexdigest() for tag in tags] for tags in entry_type]
    type_helper = dict_helper(entry_type, hash_type)

    t = jinja2.Template(open("./util/template.html").read())

    with open(output, "wb+") as file:
        file.write(t.render(html_helper=html_helper, tags_helper=tags_helper, type_helper=type_helper).encode('utf-32'))

if __name__ == "__main__":

    _, _bibtex, _markdown, _output = sys.argv
