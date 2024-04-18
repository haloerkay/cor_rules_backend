from __future__ import annotations
from collections import OrderedDict
from ordered_set import OrderedSet
from server.CMAR.FP_Tree import DataEntry,RuleEntry
from functools import cmp_to_key
MAXCOVERAGE = 5

class CRTreeNode:
    """
    The CR tree node class as the element, notice that only one label should be stored in one node if confidence > 50%
    """
    def __init__(self, name: str, support: int, confidence: float, parent: CRTreeNode | None, label=None):
        self.name = name
        self.confidence = confidence
        self.support = support
        self.next = None
        self.parent = parent
        # dict[str:TreeNode]
        self.children = {}
        self.label = label

    def display(self, depth=1):
        # # print("node ", self.name, " . display:")
        if not self.label:
            # # print('  ' * depth, self.name + ':' + str(str(self.support)) + ' ' + str(self.confidence))
            # print('  ' * depth, self.name)
            pass
        else:
            # print('  ' * depth, self.name + ':' + str(str(self.support)) + ' ' + str(self.confidence) + ' ' + str(self.label))
            pass
        for child in self.children.values():
            child.display(depth + 1)

    def _checkSelf_nothighRankThanRule(self, rule: RuleEntry):
        # self.label != rule.label may need to change, not proven by analysis that it's correct to prune rules
        if self.label is None or self.support is None or self.confidence is None or self.label != rule.label:
            return 1
        selfRule = RuleEntry(OrderedSet(self.findRootPath() + [self.name]), self.label,
                             self.support, self.confidence)
        return compare_rules(rule, selfRule)

    def insertRule(self, rule: RuleEntry, header_table) -> None:
        """
        the method to insert a rule to this tree node.
        NOTICE THAT this should be only called with root nodes, otherwise tree structure would be spoilt.
        :param header_table: the header table possibly to be updated.
        :param rule: the rule entry object to be inserted.
        :return: None.
        """
        if self.parent:
            raise AssertionError("the node to be called with this function must be a root node.")
        curNode = self
        deviateFlag = False
        # item_num = len(rule.items)
        for index, item in enumerate(rule.items):
            # if a passing node has higher rank, just prune the inserted rule
            if not deviateFlag and curNode._checkSelf_nothighRankThanRule(rule) == -1:
                # print("rule insertion pruned by predecessor: ")
                rule.display()
                return
            if deviateFlag or item not in curNode.children:
                deviateFlag = True
                """
                the old code does not handle the case where the rule ends up at an existing storage node.
                """
                # if index + 1 == item_num:
                #     node = CRTreeNode(item, rule.support, rule.confidence, self, rule.label)
                # else:
                #     node = CRTreeNode(item, 0, 0, self)
                node = CRTreeNode(item, 0, 0, None)
                curNode._insertChild(node)
                if not header_table[item]:
                    header_table[item] = node
                else:
                    updateHeader(header_table[item], node)
            curNode = curNode.children[item]
        """
        remember to prune sucessors here!!!!!!!!!!!!!!!!!!!!!!!!!
        """
        self.pruneSucessor(rule)

        curNode.label = rule.label
        curNode.support = rule.support
        curNode.confidence = rule.confidence

    def pruneSucessor(self, rule: RuleEntry):
        """
        the function called to prune successor nodes from this nade
        recursively call this function and call _pruneThis for each node itself
        use bottom-up recursion to also eliminate empty branches of nodes
        :param rule: the rule used to prune sucessors
        :return: None
        """
        for name in self.children:
            self.children[name].pruneSucessor(rule)
        if self.label is None or self.support is None or self.confidence is None:
            self._pruneThis(rule)
        if self.children is None:
            return

    def _pruneThis(self, rule: RuleEntry):
        """
        the function is called with a predecessor node.
        if self rule has lower rank, prune rule stored in this node.
        :param rule: the rule to be compared from a predecessor.
        :return: None
        """
        if self._checkSelf_nothighRankThanRule(rule):
            self.label = None
            self.support = None
            self.confidence = None
            self.label = None
        # empty this node if it is a leaf and pruned
        if self.children is None:
            self.parent.children.pop(self.name)

    def _insertChild(self, child: CRTreeNode) -> None:
        """
        the method to insert a child for current tree node.
        may overwrite the existing child if the name of child already exists.
        :param child: a treenode object to be inserted as child.
        :return: None
        """
        if isinstance(child, CRTreeNode):
            self.children[child.name] = child
            # update parent also as find prefix path needs parent
            child.parent = self
        else:
            pass
            # print("insertChild expects a child object, receive ", type(child), " instead")

    def getRule(self) -> RuleEntry | None:
        # # print("node ", self.name, " retrieved record: ", self.label)
        rootPath = self.findRootPath()
        if not rootPath:
            return None
        if self.label:
            # tempRecord = DataEntry([self] + rootPath, self.labels, self.count)
            # no need self node
            rule = RuleEntry(set(rootPath), self.label, self.support, self.confidence)
        else:
            raise RuntimeError("getRule should not be called with a non-storing node.")
        return rule

    def findRootPath(self) -> list[str]:
        """
        this function finds the path to root of FP tree given a tree node.
        :return: the path to root, including root but exluding given node.
        """
        path = [self.name]
        cur_element = self
        while cur_element.parent.name and cur_element.parent.name != 'CR Root':
            cur_element = cur_element.parent
            path.append(cur_element.name)
        return path[::-1]

    def getAllRules(self, header_table):
        rule_list = []
        for item in header_table:
            node = header_table[item]
            while node:
                if node.label:
                    rule_list.append(node.getRule())
                node = node.next
        return rule_list


def compare_rules(r1, r2):
    if r1.confidence > r2.confidence:
        return 1
    elif r1.confidence < r2.confidence:
        return -1
    else:
        if r1.support > r2.support:
            return 1
        elif r1.support < r2.support:
            return -1
        else:
            if len(r1.items) < len(r2.items):
                return 1
            elif len(r1.items) > len(r2.items):
                return -1
            else:
                # print("actually, the two rules are identical")
                return 0


# just for testing, will be replaced by original header table
def create_header_table(rule_list: list[RuleEntry]):
    s = set()
    count_dict = {}
    for rule in rule_list:
        for item in rule.items:
            if item in count_dict:
                count_dict[item] += 1
            else:
                count_dict[item] = 1
        s = s.union(rule.items)
    s_list = list(s)
    # ordered_items = sorted(s_list, key=lambda p: (count_dict[p], p), reverse=True)
    ordered_items = sorted(s_list) # sort just based on element alphabetical order

    header_table = OrderedDict.fromkeys(ordered_items, None)
    # print("debug: in create header table, header table returned: ", header_table)
    return header_table


def createCRtree(rule_list: [RuleEntry]):
    header_table = create_header_table(rule_list)
    # print("createCRTree: head table: ", header_table.keys())
    root = CRTreeNode('CR Root', 0, 0, None)
    for rule in rule_list:
        root.insertRule(rule, header_table)
    return root, header_table


# traverse to the end of a node and update next to target node
def updateHeader(current, target):
    while current.next:
        current = current.next
    current.next = target


# for test data conversion
"""
changed to ordered set for this function. may cause further problem,
remember to go back and take care of this guy!
"""


def convert_to_rule(rule):
    return RuleEntry(OrderedSet(rule[0]), rule[1], rule[2], rule[3])


def pruneByCoverage(dataset: list[DataEntry], rules: list[RuleEntry]) -> (list[RuleEntry], str):
    # the rule traversal is performed based on CBA ranking
    ordered_rules = sorted(rules, key=cmp_to_key(compare_rules), reverse=True)
    mark_count_dict = {}
    retained_rules = []
    """
    since a rule can take middle few elements of a record, i cannot come up a way
    to make use of FP tree to simplify matching process
    hence here i just use the very naive approach
    """
    uncovered = {i for i in range(len(dataset))}

    for rule in ordered_rules:
        retain_this_rule = False
        marked = []
        for record_idx in range(len(dataset)):
            record = dataset[record_idx]
            # check whether the rule correctly classify any label
            if rule.items.issubset(record.items) and record_idx in mark_count_dict \
                    and mark_count_dict[record_idx] <= MAXCOVERAGE:
                marked.append(record_idx)
                if rule.label == record.label and not retain_this_rule:
                    retain_this_rule = True
        # update dataset and remove fully k-marked entries only if the rule is retained
        if retain_this_rule:
            retained_rules.append(rule)
            for record_idx in marked:
                if record_idx in mark_count_dict and mark_count_dict[record_idx] <= MAXCOVERAGE:
                    mark_count_dict[record_idx] += 1
                else:
                    mark_count_dict[record_idx] = 1
                    # added to compute default label
                if mark_count_dict[record_idx] > MAXCOVERAGE:
                    uncovered.remove(record_idx)

    """ newly added to perform default class computation """
    label_counts = {}
    for record_idx in uncovered:
        record = dataset[record_idx]
        label = [key for key in record.label][0]
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1
    """ 反手一个擂台算法摁干 """
    default_label = None
    max_label_count = 0
    for label, count in label_counts.items():
        if count > max_label_count:
            max_label_count = count
            default_label = label
    return retained_rules, default_label


def test():
    rules = []
    data_list = [[['a', 'b', 'c'], 'A', 80, 0.8], [['a', 'b', 'c', 'd'], 'A', 63, 0.9], [['a', 'b', 'e'], 'B', 36, 0.6],
                 [['b', 'c', 'd'], 'C', 210, 0.7], [['a', 'b', 'c', 'e'], 'A', 60, 0.7],
                 [['b', 'c', 'd', 'e'], 'C', 80, 0.75]]
    for data in data_list:
        rules.append(convert_to_rule(data))
    # print()
    for rule in rules:
        rule.display()
    root, header_table = createCRtree(rules)
    # print(header_table)
    root.display()
    rules = root.getAllRules(header_table)
    # print("result rules: ")
    for rule in rules:
        rule.display()


# test()
