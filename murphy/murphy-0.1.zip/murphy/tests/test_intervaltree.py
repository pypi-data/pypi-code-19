'''
Tests to test adding intervals into the tree
'''

from nose.tools import assert_equal


def test_addtree():
    from murphy import parsegtf

    tree = parsegtf.makeGeneTreeFromExons('murphy/tests/test.gtf', None)
    assert_equal(len(tree.keys()), 2, msg="Not enough chromosomes in tree")


def test_searchtree():
    from murphy import parsegtf
    from murphy.Tree import intervalTree

    tree = parsegtf.makeGeneTreeFromExons('murphy/tests/test.gtf', None)

    nodes = intervalTree.searchTree(tree['chr6'], 152415520, 152415521)
    assert_equal(nodes[0].name2, 'ESR1', msg="Gene names do not match")
