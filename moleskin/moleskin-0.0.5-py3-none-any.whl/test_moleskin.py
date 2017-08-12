from .moleskin import Moleskin
import shutil


def test():
    moleskin = Moleskin()
    moleskin.p('')

    moleskin.p('red', [0, 1])
    moleskin.red('red', [0, 1])
    moleskin.pprint([0, 1])


def test_file_output():
    import os
    try:
        shutil.rmtree("./logs")
    except:
        pass
    m = Moleskin(file="./logs/test_output.log")
    m.debug('this line')

    # create file again to test
    m = Moleskin(file="./logs/logs/test_output.log")

    # create file again to test
    m = Moleskin(file="./logs/logs/logs/test_output.log")

    # create file again to test
    m = Moleskin(file="./logs/logs/logs/test_output.log")

    m.p('is this working?')
    m.green('This should be working!')
    m.red('not sure about this')

    log = open('./logs/logs/logs/test_output.log', "r")
    content = log.read()
    print([content])
    assert content == 'is this working?\n\x1b[32mThis should be working!' \
                      '\x1b[0m\n\x1b[31mnot sure about this\x1b[0m\n', 'lines are incorrect'
    # remove the test file again.
    shutil.rmtree("./logs")
