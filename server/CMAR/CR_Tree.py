from __future__ import annotations
from collections import OrderedDict
from ordered_set import OrderedSet
from server.CMAR.FP_Tree import DataEntry,RuleEntry
from functools import cmp_to_key
MAXCOVERAGE = 5

class CRTreeNode:

    def __init__(self, name: str, support: int, confidence: float, parent: CRTreeNode | None, label=None):
        self.name = name
        self.confidence = confidence
        self.support = support
        self.next = None
        self.parent = parent
        self.children = {}
        self.label = label

    def display(self, depth=1):
        if not self.label:
            pass
        else:
            pass
        for child in self.children.values():
            child.display(depth + 1)

    def _checkSelf_nothighRankThanRule(self, rule: RuleEntry):
        if self.label is None or self.support is None or self.confidence is None or self.label != rule.label:
            return 1
        selfRule = RuleEntry(OrderedSet(self.findRootPath() + [self.name]), self.label,
                             self.support, self.confidence)
        return compare_rules(rule, selfRule)

    def insertRule(self, rule: RuleEntry, header_table) -> None:

        if self.parent:
            raise AssertionError("the node to be called with this function must be a root node.")
        curNode = self
        deviateFlag = False
        for index, item in enumerate(rule.items):
            if not deviateFlag and curNode._checkSelf_nothighRankThanRule(rule) == -1:
                rule.display()
                return
            if deviateFlag or item not in curNode.children:
                deviateFlag = True
                node = CRTreeNode(item, 0, 0, None)
                curNode._insertChild(node)
                if not header_table[item]:
                    header_table[item] = node
                else:
                    updateHeader(header_table[item], node)
            curNode = curNode.children[item]
        self.pruneSucessor(rule)

        curNode.label = rule.label
        curNode.support = rule.support
        curNode.confidence = rule.confidence


    def pruneSucessor(self, rule: RuleEntry):

        for name in self.children:
            self.children[name].pruneSucessor(rule)
        if self.label is None or self.support is None or self.confidence is None:
            self._pruneThis(rule)
        if self.children is None:
            return

    def _pruneThis(self, rule: RuleEntry):

        if self._checkSelf_nothighRankThanRule(rule):
            self.label = None
            self.support = None
            self.confidence = None
            self.label = None
        if self.children is None:
            self.parent.children.pop(self.name)

    def _insertChild(self, child: CRTreeNode) -> None:

        if isinstance(child, CRTreeNode):
            self.children[child.name] = child
            child.parent = self
        else:
            pass

    def getRule(self) -> RuleEntry | None:
        rootPath = self.findRootPath()
        if not rootPath:
            return None
        if self.label:
            rule = RuleEntry(set(rootPath), self.label, self.support, self.confidence)
        else:
            raise RuntimeError("getRule should not be called with a non-storing node.")
        return rule

    def findRootPath(self) -> list[str]:
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
                return 0


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
    ordered_items = sorted(s_list)

    header_table = OrderedDict.fromkeys(ordered_items, None)
    return header_table


def createCRtree(rule_list: [RuleEntry]):
    header_table = create_header_table(rule_list)
    root = CRTreeNode('CR Root', 0, 0, None)
    for rule in rule_list:
        root.insertRule(rule, header_table)
    return root, header_table


def updateHeader(current, target):
    while current.next:
        current = current.next
    current.next = target

def convert_to_rule(rule):
    return RuleEntry(OrderedSet(rule[0]), rule[1], rule[2], rule[3])


def pruneByCoverage(dataset: list[DataEntry], rules: list[RuleEntry]) -> (list[RuleEntry], str):
    ordered_rules = sorted(rules, key=cmp_to_key(compare_rules), reverse=True)
    mark_count_dict = {}
    retained_rules = []
    uncovered = {i for i in range(len(dataset))}

    for rule in ordered_rules:
        retain_this_rule = False
        marked = []
        for record_idx in range(len(dataset)):
            record = dataset[record_idx]
            if rule.items.issubset(record.items) and record_idx in mark_count_dict \
                    and mark_count_dict[record_idx] <= MAXCOVERAGE:
                marked.append(record_idx)
                if rule.label == record.label and not retain_this_rule:
                    retain_this_rule = True
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

    label_counts = {}
    for record_idx in uncovered:
        record = dataset[record_idx]
        label = [key for key in record.label][0]
        if label in label_counts:
            label_counts[label] += 1
        else:
            label_counts[label] = 1

    default_label = None
    max_label_count = 0
    for label, count in label_counts.items():
        if count > max_label_count:
            max_label_count = count
            default_label = label
    return retained_rules, default_label
