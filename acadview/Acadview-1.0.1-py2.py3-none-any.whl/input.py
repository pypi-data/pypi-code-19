# Input related functions.
from constants import CURRENT_PYTHON_VERSION

def get_int():
    # This function only takes integer value. otherwise keep prompting for input.
    result = 0
    ERROR_MESSAGE = "Invalid input. Try again"

    if CURRENT_PYTHON_VERSION >= 2 and CURRENT_PYTHON_VERSION < 3:
        # Python 2.x+ support
        while True:
            try:
                result = raw_input("")
                # Check for decimal point.
                if '.' in result:
                    print (ERROR_MESSAGE)
                    result = 0
                    continue
                else:
                    result = int(result)
                    break
            except:
                print (ERROR_MESSAGE)
                result = 0
                continue
    elif CURRENT_PYTHON_VERSION >= 3:
        # Python 3.x+ support
        while True:
            try:
                result = input("")
                # Check for decimal point.
                if '.' in result:
                    print (ERROR_MESSAGE)
                    result = 0
                    continue
                else:
                    result = int(result)
                    break
            except:
                print (ERROR_MESSAGE)
                result = 0
                continue

    else:
        print ("Python version is not supported.")
        exit(-1)
    # Return the integer
    return result
