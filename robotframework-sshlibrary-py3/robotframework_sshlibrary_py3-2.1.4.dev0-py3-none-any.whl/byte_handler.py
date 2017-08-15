"""https://stackoverflow.com/questions/606191/convert-bytes-to-a-python-string/27527728#27527728"""
import codecs


def slashescape(err):
    """ codecs error handler. err is UnicodeDecode instance. return
    a tuple with a replacement for the unencodable part of the input
    and a position where encoding should continue"""
    # print err, dir(err), err.start, err.end, err.object[:err.start]
    thebyte = err.object[err.start:err.end]
    repl = u'\\x'+hex(ord(thebyte))[2:]
    return repl, err.end


codecs.register_error('slashescape', slashescape)


def byte_handler(stream):
    for line in stream:
        yield line.decode('utf-8', 'slashescape')
