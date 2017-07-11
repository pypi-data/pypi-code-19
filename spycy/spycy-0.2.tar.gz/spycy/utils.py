def compose(*funcs):
    """
    Returns the function composition of two functions.
    
    Args:
        funcs ([function]): Each function should have exactly one argument.

    Returns:
        x |-> (f o g o ... o h)(x)

    """

    def fog(arg):
        for f in funcs:
            arg = f(arg)
        return arg
    return 

