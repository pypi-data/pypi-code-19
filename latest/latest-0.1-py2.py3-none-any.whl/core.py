""":mod:`core` contains core functions for templating.


"""


import re

from .util import *
from .config import config as Config
from .exceptions import *


def eval_code(code, ctx, config=Config):
    """Parses and evaluates code converting output to a string.

    Args:
        code (str): the code to be evaluated.
        ctx (dict): the context to be evaluated in.
        config (config._Config): configuration object.

    Returns:
        str: the output converted to a string.

    Raises:
        :class:`CodeError`: raised if a :class:`SyntaxError` is raised by the builtin :func:`eval` function.
        :class:`ContextError`: raised when the context names do not match code names
            and a :class:`NameError` is raised by the builtin :func:`eval` function.

    """
    try:
        result = eval(code, ctx)
        return str(result)
    except SyntaxError:
        raise CodeError
    except NameError:
        raise ContextError


def eval_expr(expr, ctx, config=Config):
    """Evaluate a :mod:`latest` *expression*.

    An *expression* is a string of normal text with eventual code islands in between.
    The evaluation proceeds evaluating code islands and then concatenating the results with the fragments of plain text.

    Args:
        expr (str): the expression to be evaluated.
        ctx (dict): the context to be evaluated in.
        config (config._Config): configuration object.

    Returns:
        str: the output obtained concatenating the plain text fragments with the evaluation of code islands.

    """
    frags = re.split(config.code_regex, expr)
    return str().join(map(lambda i, s: eval_code(s, ctx, config=config) if i % 2 == 1 else s, range(len(frags)), frags))


def eval_namespace(ns, ctx, config=Config):
    """Translate a namespace to a list of context dictionaries.

    A *namespace* is a branch of a main context dictionary.

    The following rules apply:
    
    * if the path specified points to a scalar it is first converted to a dict with the '_value' key set to the scalar and a one-element list filled by the dict is returned
    * if the path specified points to a vector the vector is returned by the elements are treated according to these rules
    * if the path specified points to a tensor (dict or object) a one-element list filled with the tensor is returned

    Args:
        ns (str): the path for the namespace.
        ctx (dict): the main context object.
        config (config._Config): configuration object.

    Returns:
        list: a list of context dictionaries.

    """

    ctxs = select(ctx, ns, sep=config.ns_operator)

    if is_scalar(ctxs):
        ctxs = [{'_value': ctxs}]
    elif is_vector(ctxs):
        for i, c in enumerate(ctxs):
            if is_tensor(c) and hasattr(c, '__setitem__'):
                ctxs[i]['_index'] = i
            else:
                ctxs[i] = {'_index': i, '_value': c}
    else:
        ctxs = [ctxs]

    return ctxs


def eval_block(block, ctx, config=Config):
    """Evaluate a :mod:`latest` *block*.

    A *block* is a special :mod:`latest` syntax formed by two parts:
        * the `namespace` (optional) that define the branch of the context dictionary in which the `expression` must be evaluated.
        * the `expression` to be evaluated.

    Args:
        block (str): the block to be evaluated.
        ctx (dict): the context to be evaluated in.
        config (config._Config): configuration object.

    Returns:
        str: the output obtained evaluating the `expression` within the `namespace`.

    """
    m = re.match(config.inner_block_regex, block)
    if m:
        ns = m.group(config._NS_TAG)
        expr = m.group(config._EXPR_TAG)
        ctxs = eval_namespace(ns, ctx, config=config)
        return config.join_items.join(eval_expr(expr, c, config=config) for c in ctxs)
    else:
        return eval_expr(block, ctx, config=config)


def eval_template(template, ctx, config=Config):
    """Evaluates an entire template.

    Args:
        template (str): the template.
        ctx (dict): the context.
        config (config._Config): configuration object.

    Returns:
        str: the evaluated document.

    """
    frags = re.split(config.outer_block_regex, template)
    return str().join(map(lambda i, s: eval_block(s, ctx, config=config) if i % 2 == 1 else eval_expr(s, ctx, config=config), range(len(frags)), frags))



