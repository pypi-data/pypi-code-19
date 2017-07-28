from .moleskin import Moleskin


def test():
    moleskin = Moleskin()
    moleskin.p('')


def test_file_output():
    import os
    os.remove("./test_output.log")
    m = Moleskin(file="./test_output.log")
    m.p('is this working?')
    m.green('This should be working!')
    m.red('not sure about this')

    log = open('./test_output.log', "r")
    content = log.read()
    print([content])
    assert content == 'is this working?\nThis should be working!' \
                      '\x1b[0m\nnot sure about this\x1b[0m\n', \
        'lines are incorrect'
    # remove the test file again.
    os.remove("./test_output.log")
