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
            # print(111,str(item))
            # itemStr += str(item) + ' '
            front = item
        arr = ast.literal_eval(str([front,self.label,round(self.support,3),round(self.confidence,3)]))
        # print(arr)
        return arr
        # print(itemStr, '-> ', self.label, self.support, self.confidence)


class TreeNode:
    """
    The tree node class as the element
    """

    def __init__(self, name: str, occurence: int, parent: TreeNode | None, label=None):

        if label is None:
            label = {}
        self.name = name
        self.count = occurence
        self.next = None
        self.parent = parent
        # dict[str:TreeNode]
        self.children = {}
        # dict[str:int]
        self.labels = label

    def inc(self, occurence):
        self.count += occurence

    def display(self, depth=1):
        # print("node ", self.name, " . display:")
        # if not self.labels:
            # print('  ' * depth, self.name + ':' + str(self.count))
        # else:
            # print('  ' * depth, self.name + ':' + str(self.count) + ' ' + str(self.labels))
        for child in self.children.values():
            child.display(depth + 1)

    def _insertChild(self, child: TreeNode) -> None:
        """
        the method to insert a child for current tree node.
        may overwrite the existing child if the name of child already exists.
        :param child: a treenode object to be inserted as child.
        :return: None
        """
        if isinstance(child, TreeNode):
            self.children[child.name] = child
            # update parent also as find prefix path needs parent
            child.parent = self
        # else:
            # print("insertChild expects a child object, receive ", type(child), " instead")

    def removeChild(self, childName: str):
        if childName in self.children:
            self.children.pop(childName)
        # else:
            # print("unexpected child name get during _removeChild: ", childName)

    # this is purely for testing of my interface, can choose to delete or adopt later
    def insertRecord_t(self, record: DataEntry, header_table) -> None:
        """
        the method to insert a record to this tree node.
        NOTICE THAT this should be only called with root nodes, otherwise tree structure would be spoilt.
        :param header_table: the header table possibly to be updated.
        :param record: the dataentry object to be inserted.
        :return: None.
        """
        # print("> enter insert record: record: ", record.items, "-> ", record.label, 'count: ', record.count)
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
        # would be in place for curNode.labels.
        unifyTwoLabelDict(curNode.labels, record.label)
        self.count += record.count

    def _deleteSubTree(self, childName: str) -> None:
        """
        the method to delete a subtree rooted by given node.
        :param childName: the name to be deleted.
        :return: None
        """
        # since we delete a subtree, can safely remove a whole by deleting that child node
        if childName in self.children:
            self.children.pop(childName)
        else:
            print("unexpected childName: ", childName)

    def findRootPath(self) -> list[str]:
        """
        this function finds the path to root of FP tree given a tree node.
        :return: the path to root, including root but exluding given node.
        """
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
        """
        the method which find all the paths to subtree leaves.
        :return: list[list[TreeNode]]
        """
        paths = []
        if not self.children:
            return [[self]]
        for key in self.children.keys():
            tempResult = self.children[key].findAllSucessorPath()
            if tempResult is not None:
                for path in tempResult:
                    paths += (path + [self])
        return paths

    # def retrieveAllRecordsPassing(self):
    #     rootPath = self.findRootPath()
    #     allSucessorPaths = self.findAllSucessorPath()
    #     result = []
    #     fullPaths = []
    #     for path in allSucessorPaths:
    #         fullPaths.append(path + rootPath)
    #
    #     return

    def retrieveRecordingFromLeaf(self) -> DataEntry | None:
        """
        the method to retrieve a data record from the given leaf.
        must be called with a leaf node, otherwise throw runtime error.
        :return: a single record retrieved.
        """
        # print("node ", self.name, " retrieved record: ", self.labels)
        rootPath = self.findRootPath()
        # if not rootPath:
        #     return None
        if self.labels:
            # tempRecord = DataEntry([self] + rootPath, self.labels, self.count)
            # no need self node
            tempRecord = DataEntry(rootPath, self.labels, self.count)
        else:
            raise RuntimeError("retrieveAllRecordingsFromLeaf should not be called with a non-storing node.")
        return tempRecord

    def retrieveRulesFromLeaf(self, prefix: set[str],minSup,minConf) -> RuleEntry | None:
        """
        the method to retrieve all the rules from the dictionary of this node.
        must be called with a storage node, otherwise throw run time error.
        :param prefix: the prefix that produced from projections of the tree.
        used as convenience for tree manipulation and rule mining.
        :return: the full list of rules from this node, or None instead (for root node).
        """
        rootPath = self.findRootPath()
        # print("node ", self.name, " retrieved rules: ", 'labels', self.labels, "with prefix: ", prefix, "and root path: ",
        #       rootPath)
        # if not rootPath:
        #     return None
        resultRule = None
        if self.labels:
            totSum = sum(self.labels.values())
            cur_label = None
            cur_maxsupport = 0
            cur_maxconf = 0
            for label in self.labels:
                confidence = self.labels[label] / totSum
                # print("debug: support, conf: ", self.labels[label], confidence)
                # print("maxcursup, maxcurconf: ", max(MINSUP, cur_maxsupport), max(MINCONF, cur_maxconf))
                if self.labels[label]  >= max(minSup, cur_maxsupport) and confidence >= max(minConf, cur_maxconf):
                    # union 3 sets to get the full data entry that passes this node
                    # print("bug check: ", set(rootPath), {self.name}, prefix)
                    # resultRules.append(RuleEntry(set.union(set(rootPath), {self.name}, prefix), label,
                    #                              self.labels[label], confidence))
                    cur_maxsupport = self.labels[label]
                    cur_maxconf = confidence
                    cur_label = label
            if cur_label is not None and cur_maxsupport != 0 and cur_maxconf != 0:
                if self.name != 'Root':
                    # print(rootPath,self.name,prefix,123456)
                    resultRule = RuleEntry(set.union(set(rootPath), {self.name}, prefix), cur_label,
                                           cur_maxsupport, cur_maxconf)
                else:
                    resultRule = RuleEntry(set.union(set(rootPath), prefix), cur_label,
                                           cur_maxsupport, cur_maxconf)

        elif self.name != 'Root':
            raise RuntimeError("retrieveAllRulesFromLeaf should not be called with a non-storing node.")
        # if resultRule is not None:
        #     print("returned: ", resultRule, "\n", resultRule.items, "->", resultRule.label,
        #           "conf = ", resultRule.confidence, "sup = ", resultRule.support)
        # else:
        #     print("retunned None")
        return resultRule


# just a hack to make use of type hinting
def _getNodeFromTable(item: str, head_table: dict[str:[int, TreeNode]]) -> TreeNode:
    if item in head_table:
        return head_table[item][1]
    # else:
    #     print("_getNodeFromTable: unexpected item str: ", item)


# purely for testing, temp code
def _getNodeFromTable_t(item: str, head_table: dict[str:[int, TreeNode]]) -> TreeNode:
    if item in head_table:
        return head_table[item][1]
    # else:
    #     print("_getNodeFromTable: unexpected item str: ", item)

def projection(item: str, header_table: dict[str:[int, TreeNode]], root: TreeNode,minSup):
    """
    the function to evaluate a projection for a given element in the head table.
    :param item: the item name to be projected.
    :param header_table: head table of the tree to be projected.
    :return: root of new fp tree and its head table.
    """
    curNode = _getNodeFromTable_t(item, header_table)
    # if root.labels:
    #     # records = [DataEntry([], root.labels, root.count)]
    #     records = [DataEntry([], root.labels, sum(root.labels.values()))]

    # else:
    #     records = []
    records = []

    while curNode is not None:
        # print("in projection, retrieve curNode name:, its parent: ", curNode.name, curNode.parent.name,
        #       "curnode label: ", curNode.labels)
        tempRecord = None
        if curNode.labels:
            tempRecord = curNode.retrieveRecordingFromLeaf()
        if tempRecord is not None:
            records.append(tempRecord)
        curNode = curNode.next
    """
    may have this function modified to support dataEntry definition.
    """
    # print("debug: temprecord: ")
    # for record in records:
    #     print(record.items, " -> ", record.label)

    new_root, new_header_table = createFPtree(records, header_table, minSup)
    for item in new_header_table:
        new_header_table[item][0][1] = header_table[item][0][1]
    return new_root, new_header_table


def merge(item: str, head_table: dict[str:[int, TreeNode]], root: TreeNode):
    """
    the method to merge a given element in an fp tree.
    the merged element is assumed to be a leaf node as CMAR paper proposes.
    :param item: the item name to be merged.
    :param head_table: the head table of the tree to be merged.
    :return: None.
    """
    curNode = _getNodeFromTable(item, head_table)
    # print(">> enter merge: merging node ", curNode.name)
    while curNode is not None:
        if curNode.children:
            raise AssertionError("the merged node must be a leaf for this implementation."
                                 "Please check either head table or tree to make sure the least support node"
                                 "is always merged first.")
        tempParent = curNode.parent
        # print("parent: ", tempParent.name, "ready to merge dicts")
        unifyTwoLabelDict(tempParent.labels, curNode.labels)
        """
        let garbage handling to handle break off node!
        """
        tempParent.removeChild(curNode.name)
        curNode = curNode.next

    """
    newly added to remove root labels, since they're nonsence (void record) produced by merge()

    --------FALSE. They make sense. --------zpz
    """
    # root.count -= sum(root.labels.values())
    # root.labels = {}

    head_table.pop(item)


# traverse to the end of a node and update next to target node
def updateHeader(current, target):
    while current.next:
        current = current.next
    current.next = target


# add one itemset to fp tree
def updateFPtree(dataentry, root, header_table):
    root.insertRecord_t(dataentry, header_table)


"""
would be inplace for dict 1. Please notice the arg order when you pass two dicts.
"""


def unifyTwoLabelDict(dict1: dict[str:int], dict2: dict[str:int]):
    """
    the naive approach to unify two dicts.
    embedded one cannot be used since it just replace value with dict 2, but in our case we need addition.
    :param dict1: the dict to be unioned as a BASIS.
    :param dict2: the dict to be ADDED.
    :return: None
    """

    for key in dict2.keys():
        if key in dict1:
            dict1[key] += dict2[key]
        else:
            dict1[key] = dict2[key]


# frequent item finding
# MINSUP4
def create_header_table(dataset: list[DataEntry], old_headertable, minSup):
    """
    the function creating and returning a header table from scratch.
    this is the only origin of all header tables.
    :param dataset: the dataset without a head table.
    :param minSup: minimum support for an element to be included.
    :return:
    """
    header_table = {}
    for dataentry in dataset:
        for index, item in enumerate(dataentry.items):
            count = header_table.get(item, 0)
            if count:
                header_table[item][0] = count[0] + dataentry.count
            else:
                if old_headertable:
                    # print(old_headertable)
                    header_table[item] = [dataentry.count, old_headertable[item][0][1]]
                else:
                    header_table[item] = [dataentry.count, index]
    # MINSUP5
    header_table = {k: v for k, v in header_table.items() if v[0] >= minSup}
    # for k in header_table:
    #     header_table[k] = [header_table[k], None]  # element: [count, node]
    """
    a quick patch to turn not ordered list to ordered.
    """
    ordered_header_table = OrderedDict()
    # order according to frequency, then by index
    ordered_items = [v for v in sorted(header_table.items(), key=lambda p: (p[1][0], -p[1][1]))]
    # ordered_items = [v for v in sorted(header_table.items(), key=lambda p: ( -p[1][1], p[1][0]))]
    for entry in ordered_items:
        ordered_header_table[entry[0]] = [entry[1], None]
    return ordered_header_table

# MINSUP2
def createFPtree(dataset, old_headertable, minSup):
    # print('>>>>enter create FP tree:')
    # store headers of each item
    # freq_itemset = set(header_table.keys())
    # if len(freq_itemset) == 0:
    #     print("No frequent itemset")
    #     return None, None
    # MINSUP4
    header_table = create_header_table(dataset, old_headertable, minSup)
    root = TreeNode('Root', 0, None)
    for dataentry in dataset:
        # print("current dataentry: ", dataentry.items, " -> ", dataentry.label)
        counter_dict = {}
        itemset = dataentry.items
        # newly added to fix this bug
        if not itemset:
            # print("debug: root insertion case")
            # unifyTwoLabelDict(root.labels, dataentry.label)
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
    """
    find all the data entry items (path) for a given item in the header_table, by tree backtracking.
    since header_table already points to an FP tree, no need to provide FP tree for this function.
    :param item: the item in the header_table to be find in a fp tree.
    :param header_table: the header table for the tree to be mined.
    :return: all the data records (paths to root) found in the given FP tree denoted by header_table.
    """
    node = header_table[item][1]  # first node of the item
    paths = []
    while node:
        prefixPath = []
        ascendFPtree(node, prefixPath)  # from node to root
        if len(prefixPath) > 1:
            # path_counter[frozenset(prefixPath[1:])] = node.count  # mapping of path and node (item) count
            dataentry = DataEntry(prefixPath, node.labels, 1)
            paths.append(dataentry)
        node = node.next  # scan next node
    return paths

# MINSUP3
def mineFPtree(root, header_table: dict[str, int | list[TreeNode | None]],
               minSup: int, minConf,prefix: set[str], fre_itemlist: list[set], rule_list: list[RuleEntry]):
    # print("in mine tree: ordered item: ", header_table)

    """
    newly added to support mining from single root node.
    otherwise merge or projection should be performed on the tree.
    """
    if not root.children:
        rule = root.retrieveRulesFromLeaf(prefix,minSup,minConf)
        if rule:
            # print("RRRRRRRRRRRRRRRRRRRRRRnew rule appended: ", rule.items, "->", rule.label, "sup=", rule.support,
            #       "conf=", rule.confidence)

            rule_list.append(root.retrieveRulesFromLeaf(prefix,minSup,minConf))

    copy_head_table = header_table.copy()
    """
        since each item in header_table is used only once, safe to get a deep copy and loop with original one
        and since unvisited node is always valid, safe to ignore danging reference check
    """
    for fre_item in header_table.keys():  # for every frequent item
        # print(">>>>>>>>>>iteration for fre_item: ", fre_item, ", current tree: ")
        # print('header table is', header_table)
        root.display()
        cur_node = _getNodeFromTable_t(fre_item, header_table)
        # newly added to mine rules
        while cur_node is not None:
            # print("when retrieving record, curNode: ", cur_node.name, cur_node.count)
            cur_rules = cur_node.retrieveRulesFromLeaf(prefix,minSup,minConf)

            # print("cur rules: ", cur_rules)
            if cur_rules:
                # print("%%%%%%%%%%%%%%%%%%%%%%new rule appended: ", cur_rules.items, "->", cur_rules.label)
                rule_list.append(cur_rules)
            cur_node = cur_node.next
        new_freq_set = prefix.copy()
        new_freq_set.add(fre_item)
        fre_itemlist.append(new_freq_set)
        # paths = findPrefixPath(fre_item, header_table)  # find all the paths of the current item
        # new_root, new_header_table = createFPtree(paths, minSup)  # construct FP tree of the current item
        new_root, new_header_table = projection(fre_item, copy_head_table, root,minSup)
        if new_root:
            # print("after projection: ")
            new_root.display()
            # MINSUP6
            mineFPtree(new_root, new_header_table, minSup,minConf,new_freq_set, fre_itemlist,rule_list)  # recursively construct FP tree
        merge(fre_item, copy_head_table, root)

    """
    remember to mine the root here!!!!!
    """
    # the case where there's a single root remaining
    # check whether the root is a single node, if not so, there must be some problem with tree structure
    if not root.parent and not root.children and root.labels:
        cur_rules = root.retrieveRulesFromLeaf(prefix,minSup,minConf)

        # print("cur rules: ", cur_rules)
        if cur_rules:
            # print("%%%%%%%%%%%%%%%%%%%%%%new rule appended: ", cur_rules.items, "->", cur_rules.label)
            rule_list.append(cur_rules)


def printRules(rules: list[RuleEntry] | RuleEntry):
    # print("whole view of rule object: ", rules)
    if rules is None:
        return
    if isinstance(rules, RuleEntry):
        # print("rule: ", rules.items, "->", rules.label, ": ", "sup: ", rules.support, "conf: ", rules.confidence)
        return
    # for rule in rules:
        # if rule is None:
        #     continue
        # print("rule object: ", rule)
        # print("rule: ", rule.items, "->", rule.label, ": ", "sup: ", rule.support, "conf: ", rule.confidence)




