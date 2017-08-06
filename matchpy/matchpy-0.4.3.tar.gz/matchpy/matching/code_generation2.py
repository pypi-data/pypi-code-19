from ..expressions.expressions import Wildcard
from ..expressions.functions import op_iter
from .syntactic import OPERATION_END, is_operation


class Node:
    def __init__(self, requires, excludes):
        self.requires = requires
        self.excludes = excludes


class ConditionNode(Node):
    pass


class ActionNode(Node):
    pass


class TypeConditionNode(ConditionNode):
    pass


class ArgCountConditionNode(ConditionNode):
    pass


class EqualityConditionNode(ConditionNode):
    pass


class SetVariableNode(ActionNode):
    pass


def generate_nodes(pattern):
    nodes = []

    for expr, pos in preorder_iter_with_position(pattern.expression):
        if isinstance(expr, Operation):
            pass
