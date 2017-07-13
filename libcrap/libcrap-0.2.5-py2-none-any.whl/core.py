from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
import os
import os.path
from itertools import chain
from functools import wraps

from tqdm import tqdm
from typing import List, Iterable, Tuple, Callable, Any, TypeVar

T1 = TypeVar('T1')
T2 = TypeVar('T2')


def _decorate_for_enumeration(func: Callable[[T1], T2]) \
-> Callable[[Tuple[int, T1]], Tuple[int, T2]]:
    def decorated(pair: Tuple[int, T1]) -> Tuple[int, T2]:
        index, elem = pair
        return (index, func(elem))
    return decorated


def _enumerated_sort_key(pair: Tuple[int, Any]) -> int:
    index, elem = pair
    return index


def map_thread_parallel(
    func: Callable[[T1], T2],
    iterable: Iterable[T1],
    use_progress_bar: bool = False
) -> List[T2]:
    """Maps func over iterable in a multithreaded way. It is useful
    if func performance is bounded because of IO operations or sleeping
    or something like that. Returns a list. Very similar to map function.

    If use_progress_bar == True, then it uses tqdm to print a nice
    progress bar that works in terminal and in jupyter notebook."""
    with ThreadPoolExecutor() as executor:
        if use_progress_bar:
            decorated_func = _decorate_for_enumeration(func)
            futures = [executor.submit(decorated_func, pair)
                       for pair in enumerate(iterable)]
            results = [future.result() for future in tqdm(
                as_completed(futures), total=len(futures))]
            return [pair[1] for pair
                    in sorted(results, key=_enumerated_sort_key)]
        else:
            return list(executor.map(func, iterable))


def load_json(filename: str) -> object:
    """Reads json from file and returns it as a Python dict or array"""
    with open(filename, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def save_json(json_struct: object, filename: str) -> None:
    """Saves dict object as json to a file in a nicely formatted way"""
    with open(filename, 'w', encoding='utf-8') as file_to_write:
        json.dump(json_struct, file_to_write, sort_keys=True, indent=2)


def shuffled(iterable: Iterable[T1]) -> List[T1]:
    """Returns a shuffled list of items from iterable"""
    list_ = list(iterable)
    return random.sample(list_, len(list_))


def traverse_files(source_dir: str) -> Iterable[str]:
    '''Finds all files in source_dir and its subdirectories recursively
    and returns an iterable containing their filenames (with full paths).'''
    return chain.from_iterable(
        (os.path.join(directory, file) for file in files)
        for directory, subdirs, files in os.walk(source_dir))


def calcsave_or_load(filename, load_func, save_func):
    """This is a decorator.
    If filename exists, load it using load_func(filename) and return result.
    Otherwise run func, save its result using save_func(obj, filename) and return
    whatever it returns.

    See tests if you want an example of usage."""
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if os.path.isfile(filename):
                return load_func(filename)
            else:
                result = func(*args, **kwargs)
                save_func(result, filename)
                return result
            return func(*args, **kwargs)
        return wrapped_func
    return decorator


def json_calcsave_or_load(filename):
    """This is a decorator.
    If filename exists, load it as json and return result.
    Otherwise run func, save it result to that file as json and
    return whatever it returns.
    """
    return calcsave_or_load(filename, load_json, save_json)
