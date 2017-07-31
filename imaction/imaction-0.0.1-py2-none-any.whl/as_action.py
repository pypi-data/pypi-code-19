# encoding: utf-8
# pylint: disable=W0613

from functools import wraps
from importlib import import_module
import inspect
import re
from uuid import uuid4

from six import string_types


ACTION_NAME = 'action'
ACTIONID_NAME = 'id'

DOC_FLAG = '@as_action'
FLAG_OUTPUT = "#"

ACTION_ATTR_ACNAME = 'action_name'
ACTION_ATTR_ACPARANAMES = 'action_para_names'
ACTION_ATTR_ACPARADESC = 'action_para_descriptions'

NO_DESCRIPTION_MESSAGE = '<empty>'


def _is_action_metafunc(obj):
    return (
        inspect.isfunction(obj) and
        getattr(obj, '__doc__') and
        obj.__doc__.strip().startswith(DOC_FLAG)
    )


def _is_action_func(obj):
    return inspect.isfunction(obj) and hasattr(obj, ACTION_ATTR_ACNAME)


def isaction(obj):
    return _is_action_func(obj) or _is_action_metafunc(obj)


def _getparaminfo(docline, func_args):
    docline = docline.strip()
    for para in func_args:
        # target can be found in a string likes `- username: target part`
        title_and_content = re.split(r'^-\s+%s\s*:' % para, docline)
        if len(title_and_content) != 2:
            continue
        new_docline = title_and_content[1].strip()
        # target can be found in a string like '#para_name para-description-string'
        para_name = re.findall(
            r'^%s[a-z|_|\d]+' % FLAG_OUTPUT, new_docline, re.IGNORECASE
        )
        if para_name:
            para_name = para_name[0][len(FLAG_OUTPUT):]
            new_docline = new_docline[len(FLAG_OUTPUT) + len(para_name):].strip()
        else:
            para_name = para
        return para, para_name, new_docline
    return None


class ActionConfig(object):
    def __init__(self, action_description, para_names=None,
                 para_descriptions=None, action_name=None):
        self.action_description = action_description
        self.para_names = para_names
        self.para_descriptions = para_descriptions
        self.action_name = action_name

    @classmethod
    def from_action_func(cls, func):
        action_doc = func.__doc__.strip()
        splited_doc = [s for s in re.split(r'[\r\n|\n]', action_doc)]

        action_name = re.findall(
            r'%s:\s*%s([a-z|_|\d]+)' % (DOC_FLAG, FLAG_OUTPUT), splited_doc[0]
        )
        action_name = action_name[0] if action_name else func.func_name
        description = splited_doc[0]\
            .replace(DOC_FLAG + ':', '')\
            .replace(FLAG_OUTPUT + action_name, '')\
            .strip()

        filtered_cache = []
        para_names, para_descriptions = {}, {}
        func_args = inspect.getargspec(func).args
        for docline in splited_doc:
            if not docline.strip():
                filtered_cache.append('')
                continue
            paraminfo = _getparaminfo(docline, func_args)
            if paraminfo:
                para_names[paraminfo[0]] = paraminfo[1]
                para_descriptions[paraminfo[0]] = paraminfo[2] or NO_DESCRIPTION_MESSAGE
            else:
                filtered_cache.append(docline)

        pretty_doc = '\n'.join(filtered_cache)
        pretty_doc = re.sub(r'\n\n\n+', '\n\n', pretty_doc)

        return cls(description, para_names, para_descriptions, action_name)


def _advance_mapping(keys, values, extra_values=None):
    if not isinstance(keys, list):
        raise TypeError('`keys` must be list')
    if values is None or isinstance(values, string_types):
        values = [values for _ in keys]
    if not isinstance(values, list):
        raise TypeError('`values` must be list or string or None')
    if len(keys) != len(values):
        raise ValueError('lengths of `keys` and `values` are not the same')
    advance_dict = dict(zip(keys, values))
    if isinstance(extra_values, list):
        extra_values = dict(zip(keys, extra_values))
    elif not isinstance(extra_values, dict):
        extra_values = {}
    for k in advance_dict:
        if k in extra_values:
            advance_dict[k] = extra_values[k]
    return advance_dict


def as_action(action_description, para_names=None, para_descriptions=None, action_name=None):
    def _action(func):
        func_args = inspect.getargspec(func).args
        para_mappings = _advance_mapping(func_args, func_args, para_names)
        if ACTION_NAME in para_mappings and para_mappings[ACTION_NAME] == ACTION_NAME:
            raise SyntaxError(
                '%s is the action name field, not allowed as a parameter name' % ACTION_NAME
            )
        if ACTIONID_NAME in para_mappings and para_mappings[ACTIONID_NAME] == ACTIONID_NAME:
            raise SyntaxError(
                '%s is the action id field, not allowed as a parameter name' % ACTIONID_NAME
            )

        description_mappings = _advance_mapping(
            func_args, NO_DESCRIPTION_MESSAGE, para_descriptions
        )

        @wraps(func)
        def _real_action(*args, **kwargs):
            action_obj = inspect.getcallargs(func, *args, **kwargs)
            action_obj = {para_mappings[k]: v for k, v in action_obj.items()}
            action_obj.update({
                ACTION_NAME: action_name if action_name else func.func_name,
                ACTIONID_NAME: str(uuid4()),
            })
            return action_obj

        # Attributes that addon to real action function
        setattr(_real_action, '__doc__', action_description)
        setattr(_real_action, ACTION_ATTR_ACNAME, action_name)
        setattr(_real_action, ACTION_ATTR_ACPARANAMES, para_mappings)
        setattr(_real_action, ACTION_ATTR_ACPARADESC, description_mappings)

        return _real_action
    return _action


def collect_action_names(module_name=None):
    '''
    Return all action names in a list.

    `module_name` is None:
        Collect all the action names in the module that calls this
        function and return them in a list.

    `module_name` specified:
        Collect all the action names in the specified module and
        return them in a list.
    '''
    if module_name:
        module = import_module(module_name)
        work_block = {name: getattr(module, name) for name in dir(module)}
    else:
        # outer_global
        work_block = inspect.getargvalues(inspect.stack()[1][0])[-1]
    action_names = []
    for _, func in work_block.items():
        if _is_action_metafunc(func):
            action_names.append(ActionConfig.from_action_func(func).action_name)
        elif _is_action_func(func):
            action_names.append(getattr(func, ACTION_ATTR_ACNAME))
    return action_names


def wrap_posthandler(post_handler):
    '''
    Decorator to wrap an action with a post hander.

    The result from the action will be converted
    by the post_hander before it is returned back.
    '''
    def _action(func):
        @wraps(func)
        def _inner(*args, **kwargs):
            return post_handler(func(*args, **kwargs))
        return _inner
    return _action


def metafunc_to_action(metafunc, post_handler=None):
    config = ActionConfig.from_action_func(metafunc)
    action_func = as_action(
        config.action_description,
        config.para_names,
        config.para_descriptions,
        config.action_name,
    )(metafunc)
    if post_handler:
        action_func = wrap_posthandler(post_handler)(action_func)
    return action_func


def register_actions(post_handler=None):
    '''
    Convert all the functions that marked with `DOC_FLAG` to action function.

    `post_handler`: custom handler to convert the result.
        post_handler = lambda x: convert(x)
    '''
    outer_global = inspect.getargvalues(inspect.stack()[1][0])[-1]
    for _, func in outer_global.items():
        if _is_action_metafunc(func):
            outer_global[func.func_name] = metafunc_to_action(func, post_handler)
