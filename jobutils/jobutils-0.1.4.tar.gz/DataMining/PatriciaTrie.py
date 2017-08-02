import Queue
import copy
from itertools import chain

from DataMining.PatriciaNode import PatriciaNode


class PatriciaTrie(object):

    def __init__(self):
        self.root = PatriciaNode('', True, 0)


    def build_tree(self, transactions):
        for transaction in transactions:
            self.root.insert_transaction(transaction)


    def get_top_k_itemset(self, k):
        """

        :param k:
        :return:
        """
        priority_queue = Queue.PriorityQueue(k)
        result = []

        for child in self.root.children:
            priority_queue.put(([child.value], 0-child.support, child.children))

        while (not priority_queue.empty()) and (len(result) <= k):

            node_value, node_support, children = priority_queue.get()
            result.append((node_value, -1*node_support))

            for child in children:
                if type(node_value[0]) is not list:
                    value = copy.deepcopy([node_value])
                else:
                    value = copy.deepcopy(node_value)

                value.append(child.value)
                priority_queue.put((value, 0 - child.support, child.children))

        return result


    def find_association_rules(self, patterns ,confidence):
        """

        :param patterns:
        :param confidence:
        :return:
        """
        # patterns = [pattern for pattern in patterns if 1.0 * pattern[1] / patterns[0][1] > confidence]

        rules_raw = []
        known_rules = []
        for pattern in patterns:
            for i in range(len(pattern[0]), 0, -1):
                rule = (pattern[0][0], pattern[0][1:i], pattern[1])
                if rule[:-1] not in known_rules:
                    known_rules.append(rule[:-1])
                    rules_raw.append(rule)
                else:
                    break

        rules_raw = sorted(rules_raw, self.sort_rules_raw)
        rules = self.extract_association_rules(rules_raw)
        return [rule for rule in rules if rule[-1] > confidence]


    def convert_rules_to_characters(self, rules_raw):
        """

        :param rules_raw:
        :return:
        """
        mapping = {}
        result = []
        i = 0

        for rule in rules_raw:

            if str(rule[0]) not in mapping:
                mapping[str(rule[0])] = i
                key = i
                i += 1

            else:
                key = mapping[str(rule[0])]

            items = []
            for item in rule[1]:
                if str(item) not in mapping:
                    mapping[str(item)] = i
                    items.append(i)
                    i += 1
                else:
                    items.append(mapping[str(item)])

            result.append((key, items, rule[-1]))

        return result, mapping


    def sort_rules_raw(self, rule_a, rule_b):
        """

        :param rule_a:
        :param rule_b:
        :return:
        """
        for i in range(0, min(len(rule_a[1]), len(rule_b[1]))):
            if len(rule_b[1]) == 0:
                return -1
            elif len(rule_a[1]) == 0:
                return 1

            if rule_a[1][i] == rule_b[1][i]:
                continue
            elif rule_a[1][i] > rule_b[1][i]:
                return -1
            elif rule_a[1][i] < rule_b[1][i]:
                return 1

        return 0


    def sort_rules_pretty(self, rule_a, rule_b):
        """

        :param rule_a:
        :param rule_b:
        :return:
        """
        segments_a = rule_a[0].split('->')
        segments_b = rule_b[0].split('->')

        len_a = len(segments_a[-1].split(','))
        len_b = len(segments_b[-1].split(','))

        if len_a > len_b:
            return 1
        if len_a < len_b:
            return -1

        if segments_a[0] > segments_b[0]:
            return 1
        if segments_a[0] < segments_b[0]:
            return -1


        return 0


    def extract_association_rules(self, rules_sequence):
        """

        :param rules_sequence:
        :return:
        """
        result = []

        for rule in filter(lambda x: len(x[1]) > 0, rules_sequence):
            parent_rule = self.find_parent_rule(rule, filter(lambda x: len(x[1]) < len(rule[1]), rules_sequence))
            result.append((rule[1][-1], parent_rule[0] + list(chain(*parent_rule[1])), rule[-1]*1.0/parent_rule[-1]))

        return result


    def find_parent_rule(self, rule, rules):
        """

        :param rule:
        :param rules:
        :return:
        """
        largest_intersection = []
        rule_ix = 0

        for r in rules:

            intersection = []
            for i in range(0, len(r[1])):
                if r[1][i] == rule[1][i]:
                    intersection.append(rule[1][i])

            if len(intersection) > len(largest_intersection):
                largest_intersection = intersection
                rule_ix = rules.index(r)

        return rules[rule_ix]


    def generate_pretty_rules(self, rules, mapping):
        """

        :param rules:
        :return:
        """
        reverse_mapping = dict((v, k) for k, v in mapping.items())
        result = []

        for rule in rules:
            target = ','.join(reversed([str(item) for item in [reverse_mapping[item] for item in rule[1]]]))
            source = ','.join([str(item) for item in [reverse_mapping[item] for item in rule[0]]])
            result.append(("%s -> %s" % (source, target), "%.3f" % rule[-1]))

        return result


def generate_transaction_mapping(transactions):
    """

    :param transactions:
    :return:
    """
    mapping = {}
    result = []
    map_ix = 1


    for transaction in transactions:
        new_transaction = []
        prev_item = {}

        for item in transaction:

            if item == prev_item:
                continue

            if item in mapping:
                new_transaction.append(mapping[item])
            else:
                new_transaction.append(map_ix)
                mapping[item] = map_ix
                map_ix += 1

            prev_item = item

        result.append(new_transaction)

    return result, mapping