import random
import time

from pathmap.tree import Tree

class Timer():
 
    def __init__(self):
        self.start = time.time()
 
    def __enter__(self):
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        runtime = end - self.start
        msg = 'The function took {time} seconds to complete'
        print(msg.format(time=runtime))


# ========== Fixtures ============
def get_file_fixture():
    files = []
    with open('tests/test_files/toc_benchmark.txt', 'r') as input_data:
        for line in input_data:
            files.extend(line.strip().split(','))
    return files

def main():
    toc = ','.join(get_file_fixture())
    tree = Tree()
    print('Benchmark Tree:construct_tree')
    with Timer():
        tree.construct_tree(toc)
    path = None
    print('Benchmark Tree::lookup')
    with Timer():
        path = tree.lookup('c:/projects/media-server/source/calldetailrecords/esncdr/esncdr.cpp')
    print(path)

if __name__ == '__main__':
    main()
