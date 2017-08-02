import cPickle

def main():
    dump = open("memory.pickle")
    obj = cPickle.load(dump)
    print(obj)

main()