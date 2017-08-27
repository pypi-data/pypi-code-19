import time
import pickle


def cached_to_file(file_name=None):
    scope = dict(file_name=file_name)

    def decorator(original_func):
        fn_name = original_func.__name__
        file_name = scope['file_name'] or '/tmp/{}.pkl'.format(original_func.__name__)
        try:
            ts = time.time()
            cache = pickle.load(open(file_name, 'rb'))
            print('Loaded cache for {} in {}'.format(fn_name, round(time.time() - ts, 1)))
        except (IOError, ValueError):
            print('Started with a clear cache for {}'.format(fn_name))
            cache = {}

        def new_func(*a, **kw):
            name = original_func.__name__
            key = (name, a)
            if key not in cache:
                ts = time.time()
                cache[key] = original_func(*a, **kw)
                print('Fn {}({}) took {}'.format(name, a, round(time.time() - ts, 1)))
                ts = time.time()
                pickle.dump(cache, open(file_name, 'wb'))
                print('Wrote cache in {}'.format(round(time.time() - ts, 1)))
            return cache[key]

        return new_func

    return decorator
