
def retry(func, max_retry=10):

    for i in range(max_retry):
        try:
            response = func()
            print('Retry successful')
            return response
        except Exception as e:
            print(e)

    raise TimeoutError('Max retries reached')


def add_up(a, b):
    return a + b

