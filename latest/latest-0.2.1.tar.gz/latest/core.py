""":mod:`core` contains core functions for templating.

"""

import re
import copy

from .util import *
from .config import config as Config
from .exceptions import *


def parse_options(options, config=Config):
    """Parses a string of options.

    Args:
        options (str): the string that defines options.

    Returns:
        dict: the dictionary with options as key-value pairs.

    """

    opts = {}

    if options:
        for m in re.finditer(config.opt_regex, options):
            key = m.group(config.OPT_KEY_TAG)

            try:
                value = bytes(m.group(config.OPT_VALUE_TAG), encoding='utf').decode('unicode_escape')
            except TypeError:
                value = m.group(config.OPT_VALUE_TAG).decode('string_escape')

            opts[key] = value

    return opts


def eval_code(code, context, config=Config):
    """Parses and evaluates code converting output to a string.

    Args:
        code (str): the code to be evaluated.
        context (dict): the context to be evaluated in.
        config (config._Config): configuration object.

    Returns:
        str: the output converted to a string.

    Raises:
        :class:`CodeError`: raised if a :class:`SyntaxError` is raised by the builtin :func:`eval` function.
        :class:`ContextError`: raised when the context names do not match code names
            and a :class:`NameError` is raised by the builtin :func:`eval` function.

    """

    try:
        ctx = copy.deepcopy(context)
        result = eval(code, ctx)
        return str(result)
    except SyntaxError:
        raise CodeError
    except NameError:
        raise ContextError


def eval_ns(path, context, config=Config):
    """Translates a path to a list of context dictionaries, a.k.a *namespace*.

    A *namespace* is a branch of a main context dictionary.

    The following rules apply:
    
    * if the path specified points to a scalar it is first converted to a dict with the '_value' key set to the scalar and a one-element list filled by the dict is returned
    * if the path specified points to a vector the vector is returned by the elements are treated according to these rules
    * if the path specified points to a tensor (dict or object) a one-element list filled with the tensor is returned

    Args:
        path (str): the path for the namespace.
        context (dict): the main context object.
        config (config._Config): configuration object.

    Returns:
        list: the namespace, a list of context dictionaries.

    """

    ctxs = select(path, context, sep=config.ns_operator)

    if is_scalar(ctxs):
        ctxs = [{'_value': ctxs}]
    elif is_vector(ctxs):
        for i, ctx in enumerate(ctxs):
            if is_tensor(ctx) and hasattr(ctx, '__setitem__'):
                ctxs[i]['_index'] = i
            else:
                ctxs[i] = {'_index': i, '_value': ctx}
    else:
        ctxs = [ctxs]

    return ctxs


def eval_cmd(code, context, config=Config, ns=None, join_items=str()):
    """Evaluate a :mod:`latest` *command*.

    A *command* is a :mod:`latest` directive to execute code within a namespace and output a string. The *command* directive specify a *code island*. If the namespace is a list of context dictionary the code island is evaluated against every context and the results are joined (concatenated) with a special string, which by default is specified as the :code:`join_items` attribute of the configuration object.

    Args:
        code (str): the code to be executed.
        context (dict): the global context.
        config (config._Config): configuration object.
        ns (str): the namespace to be executed in.
        join_items (str): the string used to join the results from the contexts in the namespace.

    Returns:
        str: the output of the code executed within the namespace and converted to string. If the namespace target a list of contexts the code is evaluated for every context and the results are concatenated by the string defined in the :code:`join_items` attribute of the configuration object or in the keyword argument :code:`join_items`.

    """

    ctxs = eval_ns(ns, context, config=Config)
    return join_items.join(eval_code(code, c, config=config) for c in ctxs)


def eval_expr(expression, context, config=Config):
    """Evaluate a :mod:`latest` *expression*.

    An *expression* is a string of plain text with eventual code islands (:mod:`latest` commands) in between.
    The evaluation proceeds evaluating code islands and then concatenating the results with the fragments of plain text.

    Args:
        expression (str): the expression to be evaluated.
        context (dict): the context to be evaluated in.
        config (config._Config): configuration object.

    Returns:
        str: the output obtained concatenating the plain text fragments with the output of code islands evaluation process.

    """

    frags = split(expression, config.cmd_regex)
    matches = list(re.finditer(config.cmd_regex, expression))

    for i, match in enumerate(matches):
        code = match.group(config.CMD_CONTENT_TAG)
        options = parse_options(match.group(config.OPT_TAG))

        frags.insert(2 * i + 1, eval_cmd(code, context, config=config, **options))

    return str().join(frags)


def eval_env(content, namespace, context, config=Config, join_items=str()):
    """Evaluate a :mod:`latest` *environment*.

    An *environment* is a section of a template to be executed within a namespace.

    Args:
        content (str): the content of the environment to be evaluated.
        namespace (str): the namespace within the global context to be evaluated in.
        context (dict): the global context.
        config (config._Config): configuration object.
        join_items (str): the string used to join the results from the evaluation process over the expression inside the environment against the contexts within the namespace.

    Returns:
        str: the output obtained evaluating the expression within the namespace. If the namespace targets a list of context dictionaries, the expression is evaluated against every context and the results are joined with a special string which by default is specified in the :code:`join_items` attribute of the configuration object.

    """

    ctxs = eval_ns(namespace, context, config=config)
    return join_items.join(eval_expr(content, c, config=config) for c in ctxs)


def eval_latest(code, context, config=Config):
    """Evaluates an entire latest code/template.

    Args:
        code (str): the :mod:`latest` formatted template code.
        context (dict): the global context.
        config (config._Config): configuration object.

    Returns:
        str: the evaluated document.

    """

    frags = split(code, config.env_regex)
    frags = list(map(lambda expr: eval_expr(expr, context, config=config), frags))
    matches = list(re.finditer(config.env_regex, code))

    for i, match in enumerate(matches):
        content = match.group(config.ENV_CONTENT_TAG)
        namespace = match.group(config.NS_TAG)
        options = parse_options(match.group(config.OPT_TAG))

        frags.insert(2 * i + 1, eval_env(content, namespace, context, config=config, **options))

    return str().join(frags)



