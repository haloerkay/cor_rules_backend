from flask import jsonify

from server.CMAR.CMAR_Classifier import *
from server.CMAR.CR_Tree import *
from server.CMAR.FP_Tree import *
from server.CMAR.cbaLib.pre_processing import *
from server.CMAR.cbaLib.validation import *

from server.CMAR.CMAR_Classifier import get_acc

MINSUP = 10
MINCONF = 0.65
rules = []

def get_cmar_result(file):
    df = pd.read_csv('./dataset/' + file + '.csv')
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc
    dataset = pre_process(data, attributes, value_type)
    block_size = int(len(dataset) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(dataset))
    # running_times = len(split_point) - 1
    running_times = 1
    for k in range(running_times):
        print("\nRound %d:" % k)
        training_dataset = dataset[:split_point[k]] + dataset[split_point[k + 1]:]
        train_dataset_to_feed = []
        for data in training_dataset:
            train_dataset_to_feed.append(convert_data_to_dataentry(data, attributes))
        print("dataentry example is")
        train_dataset_to_feed[0].display()
        test_dataset = dataset[split_point[k]:split_point[k + 1]]
        test_dataset_to_feed = []
        for data in test_dataset:
            dataentry = convert_data_to_dataentry(data, attributes)
            test_dataset_to_feed.append(dataentry)
        rules = get_rules(train_dataset_to_feed, MINSUP)
        cr_rule_list = rules
        print('rule example is')
        cr_rule_list[0].display()

    root, header_table = createCRtree(cr_rule_list)
    tree_pruned_rules = root.getAllRules(header_table)
    retained_rules, default_label = pruneByCoverage(train_dataset_to_feed, tree_pruned_rules)
    classifier = CMARClassifier(tree_pruned_rules, default_label, train_dataset_to_feed, len(train_dataset_to_feed))
    # 原输出结果
    # print('accuracy:', get_acc(classifier, test_dataset_to_feed))
    # print(len(test_dataset_to_feed), len(train_dataset_to_feed))
    # print('default class is', default_label)
    # print("rule number is ", len(tree_pruned_rules))
    acc = get_acc(classifier, test_dataset_to_feed)
    return acc

