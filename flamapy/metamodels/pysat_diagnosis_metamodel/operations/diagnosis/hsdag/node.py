"""
A Java version of this implementation is available at:
https://github.com/HiConfiT/hiconfit-core/blob/main/ca-cdr-package/src/main/java/at/tugraz/ist/ase/cacdr/algorithms/hs/Node.java
"""
from enum import Enum

from .labeler.labeler import AbstractHSParameters


class NodeStatus(Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'
    PRUNED = 'Pruned'
    CHECKED = 'Checked'  # Checked - the label of this node is a Conflict or a Diagnosis


# pylint: disable=too-many-instance-attributes
class Node:
    """
    A data structure representing a node of an HS-dag.
    """
    generating_node_id = -1

    def __init__(self, parent: 'Node' = None, arc_label: int = None,
                 parameters: AbstractHSParameters = None):
        self.node_id = Node.generating_node_id = Node.generating_node_id + 1
        self.status = NodeStatus.OPEN  # node status
        # label of the node - it can be a minimal conflict or a diagnosis or null
        self.label = []
        # the constraint associated to the arch which comes to this node
        self.arc_label = arc_label
        self.parameters = parameters
        self.path_label = None  # labels of the path to here
        self.parents = None  # the node's parents. Can be null for the root node.
        self.children = {}  # the node's children

        if parent is None:
            self.level = 0  # tree level
        else:
            self.level = parent.level + 1  # tree level
            self.parents = []
            self.parents.append(parent)
            if parent.path_label is not None:
                self.path_label = parent.path_label.copy()
            else:
                self.path_label = []
            self.path_label.append(arc_label)

            parent.children[arc_label] = self

    @staticmethod
    def create_root(label: list[int], parameters: AbstractHSParameters) -> 'Node':
        Node.generating_node_id = -1

        root = Node()
        root.label = label
        root.parameters = parameters

        return root

    def add_parent(self, parent: 'Node'):
        if self.is_root():
            raise ValueError("The root node cannot have parents.")
        self.parents.append(parent)

    def add_child(self, arc_label: int, child: 'Node'):
        self.children[arc_label] = child
        child.add_parent(self)

    def is_root(self) -> bool:
        return self.parents is None

    def __str__(self):
        return (f"Node{{id={self.node_id}, level={self.level}, status={self.status}, "
                f"label={self.label}, parameter={self.parameters}, arcLabel={self.arc_label}, "
                f"pathLabels={self.path_label}}}")
