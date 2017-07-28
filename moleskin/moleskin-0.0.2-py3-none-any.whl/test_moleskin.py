from .moleskin import Moleskin


def test():
    moleskin = Moleskin()
    moleskin.p('')

    moleskin.p('red', [0, 1])
    moleskin.red('red', [0, 1])
    moleskin.pprint([0, 1])


def test_file_output():
    import os
    try:
        os.remove("./test_output.log")
    except:
        pass
    m = Moleskin(file="./test_output.log")
    m.p('is this working?')
    m.green('This should be working!')
    m.red('not sure about this')

    log = open('./test_output.log', "r")
    content = log.read()
    print([content])
    assert content == 'is this working?\n\x1b[32mThis should be working!' \
                      '\x1b[0m\n\x1b[31mnot sure about this\x1b[0m\n', 'lines are incorrect'
    # remove the test file again.
    os.remove("./test_output.log")
