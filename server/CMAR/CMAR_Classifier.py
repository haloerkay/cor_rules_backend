from typing import Optional
from server.CMAR.FP_Tree import RuleEntry, createFPtree, mineFPtree
from server.CMAR.CR_Tree import DataEntry
from scipy.stats import chi2_contingency
import numpy as np

CHISQTHRESHOLD = 0

class CMARClassifier:
    def __init__(self, rules: [RuleEntry], default_label: str, dataset: Optional[DataEntry], dataset_size: int):
        self.rules = rules
        self.default_label = default_label
        # used for max X2 square
        self.dataset = dataset
        self.dataset_size = dataset_size

        self.dataset_label_count = {}
        if dataset is None:
            return
        for record in dataset:
            label_dic = record.label
            for label in label_dic:
                if label in self.dataset_label_count:
                    self.dataset_label_count[label] += 1
                else:
                    self.dataset_label_count[label] = 1

    def classify(self, record: DataEntry,attributes):
        precondition = record.items
        valid_rules = {}
        rules = []
        for rule in self.rules:
            # if the rule matches the data
            if rule.items.issubset(precondition):
                # add the classified label count to the dictionary
                if rule.label in valid_rules:
                    valid_rules[rule.label].append(rule)
                else:
                    valid_rules[rule.label] = [rule]
        # processing label and counts to find the last label
        final_label = self.default_label

        for key, ruleList in valid_rules.items():
            # print(key, " rules : ")
            for rule in ruleList:
                index_map = {value: index for index, value in enumerate(attributes)}
                modified_values = {}
                # 遍历第二个数组
                for value in rule.items:
                    # 获取在第一个数组中的索引
                    index = index_map.get(value[:-1], None)
                    # 如果找到了索引，则修改对应的值
                    if index is not None:
                        modified_values[index] = int(value[-1])
                    rules.append([modified_values, rule.label, round(rule.support / len(self.dataset), 3),
                                  round(rule.confidence, 3)])


                rule.display()

        max_wchisq = 0
        for label in valid_rules:
            weighted_chisq = self.weighted_chi_square(valid_rules[label])
            if weighted_chisq >= CHISQTHRESHOLD and weighted_chisq > max_wchisq:
                final_label = label
                max_wchisq = weighted_chisq
        return final_label,rules

    @staticmethod
    def chi_squared(precondition_count: int, label_count: int, support: int, datasize: int) -> (float, float):
        nAB = support
        n_notA_notB = datasize - (precondition_count + label_count) + support
        n_A_notB = precondition_count - support
        n_notA_B = label_count - support
        g, p, _, _ = chi2_contingency(np.array([[nAB, n_A_notB], [n_notA_B, n_notA_notB]]))
        return g, p

    @staticmethod
    def max_chi_squared(precondition_count: int, label_count: int, datasize: int):
        n_notleft = datasize - precondition_count
        n_notright = datasize - label_count

        e = 1.0 / (precondition_count * label_count) + 1.0 / (precondition_count * n_notright) + \
            1.0 / (n_notleft * label_count) + 1.0 / (n_notleft * n_notright)
        return ((min(precondition_count,
                     label_count) - precondition_count * label_count / datasize) ** 2) * datasize * e

    def weighted_chi_square(self, rules: [RuleEntry]):
        sum = 0
        for rule in rules:
            precondition_count = int(rule.support / rule.confidence)
            label_count = self.dataset_label_count[rule.label]
            support = rule.support

            chisq, _ = CMARClassifier.chi_squared(precondition_count, label_count, support, self.dataset_size)
            max_chisq = CMARClassifier.max_chi_squared(precondition_count, label_count, self.dataset_size)
            sum += (chisq * chisq) / max_chisq
        return sum


def convert_data_to_dataentry(l_data, attributes):
    items = []
    for index, i in enumerate(l_data[:-1]):
        item = attributes[index] + str(i)
        items.append(item)
    label = l_data[-1]
    return DataEntry(items, {label:1}, 1)

def get_acc(classifier, dataentries: [DataEntry],attributes):
    error_count = 0
    result_counter = {}
    for dataentry in dataentries:
        label = [key for key in dataentry.label][0]
        result, rules = classifier.classify(dataentry,attributes)
        if result in result_counter:
            result_counter[result] += 1
        else:
            result_counter[result] = 1
        result_counter[result] += 1
        if result != label:
            error_count += 1

    return 1 - error_count / len(dataentries), rules
# get rules from dataset
def get_rules(data, minSup,minConf):
    myFPtree, myHeaderTab = createFPtree(data, {}, minSup)
    # print("my header_table is ", myHeaderTab)
    myFPtree.display()
    freqItems = []
    rules = []
    mineFPtree(myFPtree, myHeaderTab, minSup,minConf, set([]), freqItems, rules)
    return rules

