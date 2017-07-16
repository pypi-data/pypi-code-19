# -*- coding: utf-8 -*-

'''
cli
---


console script for pynlai.
'''


import pprint
from six.moves import input

import click
import en_core_web_sm as en

from pynlai.core import (
    create_view,
    to_ent,
    to_nc,
    to_obj,
    to_pos,
    to_sub,
)

from pynlai.views import (
    _DEP_SPAN,
    _DEP_TOKEN,
    _ENT_SPAN,
    _POS_TOKEN,
)


views = {
    'dep_span': _DEP_SPAN,
    'dep_token': _DEP_TOKEN,
    'ent_span': _ENT_SPAN,
    'pos_token': _POS_TOKEN,
}

func_view = {
    'ent': (to_ent, _ENT_SPAN['HR']),
    'nc': (to_nc, _DEP_SPAN['HR']),
    'obj': (to_obj, _DEP_TOKEN['HR']),
    'pos': (to_pos, _POS_TOKEN['HR']),
    'sub': (to_sub, _DEP_TOKEN['HR']),
}

pp = pprint.PrettyPrinter(indent=4, width=200)


@click.group()
@click.pass_context
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='interactive prompt for sentence input'
)
@click.option(
    '--pipeline', '-p',
    default=('pos',),
    multiple=True,
    type=click.Choice(func_view.keys()),
    help='nl function(s) and paired view to use in processing pipeline'
)
@click.option(
    '--view', '-v',
    multiple=True,
    type=click.Choice(views.keys()),
    help='override paired view(s) with view(s)'
)
def main(ctx, interactive, pipeline, view):
    '''
    pynlai command line interface
    '''

    if view:
        vs = [e for v in view for e in views[v]['HR']]
        fv = {k: (v[0], vs) for k, v in func_view.items()}
    else:
        fv = func_view

    ctx.obj['i'] = interactive
    ctx.obj['pipeline'] = [fv[k] for k in pipeline]
    ctx.obj['nlp'] = en.load()


@main.command()
@click.pass_context
@click.argument('sent', required=False)
def parse(ctx, sent):
    '''
    parse a sentence
    '''

    nlp = ctx.obj['nlp']

    while True:

        sent = input('parse>  ') if ctx.obj['i'] else sent

        try:

            for f, v in ctx.obj['pipeline']:
                r = [create_view(e, v) for e in f(doc=sent, nlp=nlp)]
                click.echo(pp.pprint((f.__name__, r)))

            if not ctx.obj['i']:
                break

        except KeyboardInterrupt:
            break


@main.command()
@click.pass_context
@click.argument('files', nargs=-1)
def parsefile(ctx, files):
    '''
    parse document(s), globs ok
    '''

    nlp = ctx.obj['nlp']

    for f in files:

        click.echo(f)

        with open(f, 'r') as f_obj:

            doc = nlp(f_obj.read())

            for sent in doc.sents:
                click.echo(sent)
                ctx.invoke(parse, sent=sent.text)


def entry_point():
    '''
    required to make setuptools and click play nicely (context object)
    '''

    return main(obj={})


if __name__ == "__main__":
    entry_point()
