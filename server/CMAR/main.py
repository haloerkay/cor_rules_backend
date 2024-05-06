import time

from server.CMAR.CMAR_Classifier import *
from server.CMAR.CR_Tree import *
from server.CMAR.FP_Tree import *
from server.CMAR.cbaLib.pre_processing import *
from server.CMAR.cbaLib.validation import *
from server.CMAR.CMAR_Classifier import get_acc

def get_cmar_result(file,minSup,minConf):
    df = pd.read_csv('./dataset/' + file + '.csv')
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc
    dataset = pre_process(data, attributes, value_type)

    train_ratio = 0.9
    train_size = int(len(dataset) * train_ratio)
    minSup = train_size * minSup
    random.shuffle(dataset)
    training_dataset = dataset[:train_size]
    test_dataset = dataset[train_size:]

    train_dataset_to_feed = []
    for data in training_dataset:
        train_dataset_to_feed.append(convert_data_to_dataentry(data, attributes))
    print("dataentry example is")
    train_dataset_to_feed[0].display()
    test_dataset_to_feed = []
    for data in test_dataset:
        dataentry = convert_data_to_dataentry(data, attributes)
        test_dataset_to_feed.append(dataentry)
    # MINSUP1
    start = time.time()
    rules = get_rules(train_dataset_to_feed, minSup,minConf)
    cr_rule_list = rules
    print('rule example is')
    # cr_rule_list[0].display()

    root, header_table = createCRtree(cr_rule_list)
    tree_pruned_rules = root.getAllRules(header_table)
    retained_rules, default_label = pruneByCoverage(train_dataset_to_feed, tree_pruned_rules)
    classifier = CMARClassifier(tree_pruned_rules, default_label, train_dataset_to_feed, len(train_dataset_to_feed))
    end = time.time()
    cost = end - start
    # 原输出结果
    # print('accuracy:', get_acc(classifier, test_dataset_to_feed))
    # print(len(test_dataset_to_feed), len(train_dataset_to_feed))
    # print('default class is', default_label)
    # print("rule number is ", len(tree_pruned_rules))
    # print(111,str(tree_pruned_rules))
    accuracy,rules = get_acc(classifier, test_dataset_to_feed)
    # print( {'accuracy': accuracy, 'cost': cost,'rules':rules })
    return {'accuracy': accuracy, 'cost': cost,'rules':rules }

# get_cmar_result('iris',0.01,0)