import pandas as pd

from CMAR_Classifier import *
from CR_Tree import *
from FP_tree import *
from cbaLib.pre_processing import *
from cbaLib.validation import *
from cbaLib.ruleitem import RuleItem
from ordered_set import OrderedSet

import csv



MINSUP = 10
MINCONF = 0.65
rules = []



# def convert_to_dataentry_and_build_tree(data, scheme):
#     dataentries = []
#     items = []
#     for index, char in enumerate(data[:-1]):
#         items.append(str(scheme[index]) + '' + char)
#     dataentry = DataEntry(items, {data[-1]: 1}, 1)
#     dataentries.append(dataentry)
#     root, head_table = createFPtree(dataentries, minSup=MINSUP)
#     print(head_table)
#     root.display()


def convert_ruleitem_to_ours(l_ruleitem:RuleItem, attributes):
    support = l_ruleitem.rule_sup_count
    label = l_ruleitem.class_label
    confidence = l_ruleitem.confidence
    items = OrderedSet()
    for cond in l_ruleitem.cond_set:
        attribute = attributes[cond]
        value = l_ruleitem.cond_set[cond]
        items.add(attribute+str(value))
    return RuleEntry(items, label, support, confidence)

def convert_data_to_dataentry(l_data,attributes ):
    items = []
    for index, i in enumerate(l_data[:-1]):
        item = attributes[index] + str(i)
        items.append(item)
    label = l_data[-1]
    return DataEntry(items, {label:1}, 1)

def get_error(classifier, dataentries: [DataEntry]):
    error_count = 0
    result_counter = {}
    for dataentry in dataentries:
        label = [key for key in dataentry.label][0]
        result = classifier.classify(dataentry)
        if result in result_counter:
            result_counter[result] += 1
        else:
            result_counter[result] = 1
        result_counter[result] += 1
        if result != label:
            error_count += 1
    print(result_counter)
    print("error count is", error_count)
    return error_count/len(dataentries)
# get rules from dataset
def get_rules(data, MINSUP):
    myFPtree, myHeaderTab = createFPtree(data, {}, minSup=MINSUP)
    print("my header_table is ", myHeaderTab)
    myFPtree.display()
    freqItems = []
    rules = []
    mineFPtree(myFPtree, myHeaderTab, MINSUP, set([]), freqItems, rules)
    return rules

def test_read_data(minsup=MINSUP, minconf=MINCONF):
    df = pd.read_csv('./car.csv')
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc

    # data, attributes, value_type = read(data_path, scheme_path)
    dataset = pre_process(data, attributes, value_type)



    block_size = int(len(dataset) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(dataset))
    running_times = len(split_point) - 1
    running_times = 1
    for k in range(running_times):
        print("\nRound %d:" % k)
    #
        training_dataset = dataset[:split_point[k]] + dataset[split_point[k+1]:]

        train_dataset_to_feed = []
        for data in training_dataset:
            train_dataset_to_feed.append(convert_data_to_dataentry(data, attributes))
        print("dataentry example is")
        train_dataset_to_feed[0].display()
        test_dataset = dataset[split_point[k]:split_point[k+1]]
        test_dataset_to_feed = []
        for data in test_dataset:
            dataentry = convert_data_to_dataentry(data, attributes)
            test_dataset_to_feed.append(dataentry)
        rules = get_rules(train_dataset_to_feed, MINSUP)
        cr_rule_list = rules
        print('rule example is')
        cr_rule_list[0].display()
        """
            newly added pruning functions
            """
        # prune by establishing the cr tree

    root, header_table = createCRtree(cr_rule_list)
    tree_pruned_rules = root.getAllRules(header_table)
    retained_rules, default_label = pruneByCoverage(train_dataset_to_feed, tree_pruned_rules)
    classifier = CMARClassifier(tree_pruned_rules, default_label, train_dataset_to_feed, len(train_dataset_to_feed))
    print(get_error(classifier, test_dataset_to_feed))
    print(len(test_dataset_to_feed), len(train_dataset_to_feed))
    print('default class is', default_label)
    print("rule number is ", len(tree_pruned_rules))

test_read_data()
# test()
