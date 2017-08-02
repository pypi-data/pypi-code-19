import copy


class PatriciaNode(object):

    def __init__(self, value, is_root=False, support=1):
        """

        :param value:
        :param is_root:
        :param support:
        """
        self.value = value
        self.isRoot = is_root
        self.children = []
        self.support = support


    def add_child_to_existing_node(self, transaction, subset_index, child_index):
        """

        :param transaction:
        :param subset_index:
        :param child_index:
        :return:
        """
        disjunction_node = copy.deepcopy(self.children[child_index])
        intersection, diff_left, diff_right = self.get_node_value_diff(disjunction_node.value, transaction, subset_index)

        self.children[child_index].value = intersection
        self.children[child_index].increment_support()

        if len(diff_left) > 0:
            disjunction_node.value = diff_left
            disjunction_node.children = copy.deepcopy(self.children[child_index].children)
            self.children[child_index].children = []
            self.children[child_index].add_new_child(disjunction_node)

        if len(diff_right) > 0:
            self.children[child_index].insert_transaction(diff_right)
        else:
            self.children[child_index].add_new_child(PatriciaNode(diff_right, False, 1))

        pass


    def increment_support(self):
        """

        :return:
        """
        self.support = self.support + 1


    def add_new_child(self, new_node):
        """

        :param new_node:
        :return:
        """
        self.children.append(new_node)


    def insert_transaction(self, transaction):
        """

        :param transaction:
        :return:
        """
        subset_exist, subset_index, child_index = self.subset_exist(transaction)
        if subset_exist:
            self.add_child_to_existing_node(transaction, subset_index, child_index)
        else:
            self.add_new_child(PatriciaNode(transaction))


    def subset_exist(self, transaction):
        """

        :param transaction:
        :return:
        """
        subset_ix = -1
        child_ix = []

        for child in self.children:
            for i in range(0, min([len(transaction), len(child.value)])):
                if child.value[i] == transaction[i]:
                    subset_ix = i
                    child_ix = self.children.index(child)
                else:
                    break

        if subset_ix > -1:
            return True, subset_ix + 1, child_ix

        return False, subset_ix, -1


    def get_node_value_diff(self, node_value, transaction, subset_index):
        """

        :param node_value:
        :param transaction:
        :param subset_index:
        :return:
        """
        intersection = transaction[:subset_index]
        diff_left = node_value[subset_index:]
        diff_right = transaction[subset_index:]

        return intersection, diff_left, diff_right