from pathmap.tree import Tree


def get_file_fixture(path):
    files = []
    with open(path, 'r') as input_data:
        for line in input_data:
            files.extend(line.strip().split(','))
    print('File count: %i' % len(files))
    return ','.join(files)


toc = get_file_fixture('tests/test_files/toc_benchmark.txt')


@profile
def construct_tree():
    tree = Tree()
    tree.construct_tree(toc)


if __name__ == '__main__':
    construct_tree()
