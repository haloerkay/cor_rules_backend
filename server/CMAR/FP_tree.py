# coding:utf-8
from __future__ import annotations

import ast
from collections import OrderedDict



"""
header table element format:
{'n3', [[count, index], treenode}
"""


class DataEntry:
    def __init__(self, items: list[str], label: dict[str:int], count: int = 1):
        self.items = items
        self.label = label
        self.count = count

    def display(self):
        itemStr = ''
        for item in self.items:
            itemStr += str(item) + ' '

        print(itemStr,self.label)

class RuleEntry:
    def __init__(self, items, label: str, support: int, confidence: float):
        self.items = items
        self.label = label
        self.support = support
        self.confidence = confidence
    def display(self):
        # itemStr = ''
        front = ''
        for item in self.items:

            front = item
        arr = [front,self.label,round(self.support,3),round(self.confidence,3)]
        return arr


class TreeNode:

    def __init__(self, name: str, occurence: int, parent: TreeNode | None, label=None):

        if label is None:
            label = {}
        self.name = name
        self.count = occurence
        self.next = None
        self.parent = parent
        self.children = {}
        self.labels = label

    def inc(self, occurence):
        self.count += occurence

    def display(self, depth=1):

        for child in self.children.values():
            child.display(depth + 1)

    def _insertChild(self, child: TreeNode) -> None:

        if isinstance(child, TreeNode):
            self.children[child.name] = child
            child.parent = self

    def removeChild(self, childName: str):
        if childName in self.children:
            self.children.pop(childName)

    def insertRecord_t(self, record: DataEntry, header_table) -> None:

        if self.parent:
            raise AssertionError("the node to be called with this function must be a root node.")
        curNode = self
        deviateFlag = False
        """
        newly added to support root insertion
        """
        if not record.items:
            unifyTwoLabelDict(self.labels, record.label)
            # print('updating root count:', self.count, record.count)
            self.count = self.count + record.count
            return

        for index, item in enumerate(record.items):
            if deviateFlag or item not in curNode.children:
                deviateFlag = True
                node = TreeNode(item, record.count, self)
                curNode._insertChild(node)
                if not header_table[item][1]:
                    header_table[item][1] = node
                else:
                    updateHeader(header_table[item][1], node)
            else:
                curNode.children[item].count += record.count
            curNode = curNode.children[item]
        unifyTwoLabelDict(curNode.labels, record.label)
        self.count += record.count

    def _deleteSubTree(self, childName: str) -> None:

        if childName in self.children:
            self.children.pop(childName)
        else:
            print("unexpected childName: ", childName)

    def findRootPath(self) -> list[str]:

        if not self.parent:
            return []
        path = []
        cur_element = self
        while cur_element.parent.name and cur_element.parent.name != 'Root':
            cur_element = cur_element.parent
            path.append(cur_element.name)
        path.reverse()
        return path

    def findAllSucessorPath(self):

        paths = []
        if not self.children:
            return [[self]]
        for key in self.children.keys():
            tempResult = self.children[key].findAllSucessorPath()
            if tempResult is not None:
                for path in tempResult:
                    paths += (path + [self])
        return paths


    def retrieveRecordingFromLeaf(self) -> DataEntry | None:

        rootPath = self.findRootPath()
        if self.labels:
            tempRecord = DataEntry(rootPath, self.labels, self.count)
        else:
            raise RuntimeError("retrieveAllRecordingsFromLeaf should not be called with a non-storing node.")
        return tempRecord

    def retrieveRulesFromLeaf(self, prefix: set[str],minSup,minConf) -> RuleEntry | None:

        rootPath = self.findRootPath()
        resultRule = None
        if self.labels:
            totSum = sum(self.labels.values())
            cur_label = None
            cur_maxsupport = 0
            cur_maxconf = 0
            for label in self.labels:
                confidence = self.labels[label] / totSum

                if self.labels[label]  >= max(minSup, cur_maxsupport) and confidence >= max(minConf, cur_maxconf):

                    cur_maxsupport = self.labels[label]
                    cur_maxconf = confidence
                    cur_label = label
            if cur_label is not None and cur_maxsupport != 0 and cur_maxconf != 0:
                if self.name != 'Root':
                    resultRule = RuleEntry(set.union(set(rootPath), {self.name}, prefix), cur_label,
                                           cur_maxsupport, cur_maxconf)
                else:
                    resultRule = RuleEntry(set.union(set(rootPath), prefix), cur_label,
                                           cur_maxsupport, cur_maxconf)

        elif self.name != 'Root':
            raise RuntimeError("retrieveAllRulesFromLeaf should not be called with a non-storing node.")
        return resultRule


def _getNodeFromTable(item: str, head_table: dict[str:[int, TreeNode]]) -> TreeNode:
    if item in head_table:
        return head_table[item][1]
def _getNodeFromTable_t(item: str, head_table: dict[str:[int, TreeNode]]) -> TreeNode:
    if item in head_table:
        return head_table[item][1]

def projection(item: str, header_table: dict[str:[int, TreeNode]], root: TreeNode,minSup):

    curNode = _getNodeFromTable_t(item, header_table)

    records = []

    while curNode is not None:

        tempRecord = None
        if curNode.labels:
            tempRecord = curNode.retrieveRecordingFromLeaf()
        if tempRecord is not None:
            records.append(tempRecord)
        curNode = curNode.next

    new_root, new_header_table = createFPtree(records, header_table, minSup)
    for item in new_header_table:
        new_header_table[item][0][1] = header_table[item][0][1]
    return new_root, new_header_table


def merge(item: str, head_table: dict[str:[int, TreeNode]], root: TreeNode):

    curNode = _getNodeFromTable(item, head_table)
    while curNode is not None:
        if curNode.children:
            raise AssertionError("the merged node must be a leaf for this implementation."
                                 "Please check either head table or tree to make sure the least support node"
                                 "is always merged first.")
        tempParent = curNode.parent
        unifyTwoLabelDict(tempParent.labels, curNode.labels)
        tempParent.removeChild(curNode.name)
        curNode = curNode.next

    head_table.pop(item)


def updateHeader(current, target):
    while current.next:
        current = current.next
    current.next = target

def updateFPtree(dataentry, root, header_table):
    root.insertRecord_t(dataentry, header_table)

def unifyTwoLabelDict(dict1: dict[str:int], dict2: dict[str:int]):

    for key in dict2.keys():
        if key in dict1:
            dict1[key] += dict2[key]
        else:
            dict1[key] = dict2[key]

def create_header_table(dataset: list[DataEntry], old_headertable, minSup):

    header_table = {}
    for dataentry in dataset:
        for index, item in enumerate(dataentry.items):
            count = header_table.get(item, 0)
            if count:
                header_table[item][0] = count[0] + dataentry.count
            else:
                if old_headertable:
                    header_table[item] = [dataentry.count, old_headertable[item][0][1]]
                else:
                    header_table[item] = [dataentry.count, index]

    ordered_header_table = OrderedDict()
    ordered_items = [v for v in sorted(header_table.items(), key=lambda p: (p[1][0], -p[1][1]))]
    for entry in ordered_items:
        ordered_header_table[entry[0]] = [entry[1], None]
    return ordered_header_table

# MINSUP2
def createFPtree(dataset, old_headertable, minSup):
    header_table = create_header_table(dataset, old_headertable, minSup)
    root = TreeNode('Root', 0, None)
    for dataentry in dataset:
        counter_dict = {}
        itemset = dataentry.items
        if not itemset:

            updateFPtree(dataentry, root, header_table)

        for item in itemset:
            if item in header_table:  # filtering, only get frequent items
                counter_dict[item] = header_table[item][0]
        if counter_dict:
            # update fp tree
            ordered_items = [v[0] for v in
                             sorted(counter_dict.items(), key=lambda p: (p[1][0], -p[1][1]), reverse=True)]
            dataentry.items = ordered_items
            updateFPtree(dataentry, root, header_table)
    return root, header_table


# backtrack
def ascendFPtree(leaf, prefixPath):
    if leaf.parent is not None:
        prefixPath.append(leaf.name)
        ascendFPtree(leaf.parent, prefixPath)


def findPrefixPath(item, header_table: dict[str, int | list[TreeNode | None]]):
    node = header_table[item][1]  # first node of the item
    paths = []
    while node:
        prefixPath = []
        ascendFPtree(node, prefixPath)  # from node to root
        if len(prefixPath) > 1:
            dataentry = DataEntry(prefixPath, node.labels, 1)
            paths.append(dataentry)
        node = node.next  # scan next node
    return paths

# MINSUP3
def mineFPtree(root, header_table: dict[str, int | list[TreeNode | None]],
               minSup: int, minConf,prefix: set[str], fre_itemlist: list[set], rule_list: list[RuleEntry]):

    if not root.children:
        rule = root.retrieveRulesFromLeaf(prefix,minSup,minConf)
        if rule:


            rule_list.append(root.retrieveRulesFromLeaf(prefix,minSup,minConf))

    copy_head_table = header_table.copy()

    for fre_item in header_table.keys():  # for every frequent item

        root.display()
        cur_node = _getNodeFromTable_t(fre_item, header_table)
        while cur_node is not None:
            cur_rules = cur_node.retrieveRulesFromLeaf(prefix,minSup,minConf)
            if cur_rules:
                rule_list.append(cur_rules)
            cur_node = cur_node.next
        new_freq_set = prefix.copy()
        new_freq_set.add(fre_item)
        fre_itemlist.append(new_freq_set)
        new_root, new_header_table = projection(fre_item, copy_head_table, root,minSup)
        if new_root:
            # print("after projection: ")
            new_root.display()
            # MINSUP6
            mineFPtree(new_root, new_header_table, minSup,minConf,new_freq_set, fre_itemlist,rule_list)  # recursively construct FP tree
        merge(fre_item, copy_head_table, root)

    if not root.parent and not root.children and root.labels:
        cur_rules = root.retrieveRulesFromLeaf(prefix,minSup,minConf)

        if cur_rules:
            rule_list.append(cur_rules)


def printRules(rules: list[RuleEntry] | RuleEntry):
    if rules is None:
        return
    if isinstance(rules, RuleEntry):
        return





