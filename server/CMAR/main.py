import json

from server.CMAR.CMAR_Classifier import *
from server.CMAR.CR_Tree import *
from server.CMAR.cbaLib.pre_processing import *
from server.CMAR.cbaLib.validation import *
from server.CMAR.CMAR_Classifier import get_acc

def str2numerical(data, value_type):
    size = len(data)
    columns = len(data[0])
    for i in range(size):
        for j in range(columns-1):
            if value_type[j] == 'float64' and data[i][j] != '?':
                data[i][j] = float(data[i][j])
    return data
def read(data_path):
    df = pd.read_csv(data_path)
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc
    data = str2numerical(data, value_type)
    return data, attributes, value_type

def get_cmar_result(file,minSup,minConf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    random.shuffle(data)
    dataset = pre_process(data, attributes, value_type)

    # print(attributes)
    train_ratio = 0.9
    train_size = int(len(dataset) * train_ratio)
    minSup = int(train_size * minSup)
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

    start = time.time()
    rules = get_rules(train_dataset_to_feed, minSup,minConf)
    cr_rule_list = rules
    print('rule example is')

    root, header_table = createCRtree(cr_rule_list)
    tree_pruned_rules = root.getAllRules(header_table)
    retained_rules, default_label = pruneByCoverage(train_dataset_to_feed, tree_pruned_rules)
    classifier = CMARClassifier(tree_pruned_rules, default_label, train_dataset_to_feed, len(train_dataset_to_feed))
    end = time.time()
    cost = end - start
    accuracy,rules = get_acc(classifier, test_dataset_to_feed,attributes)

    seen = {}
    result = []

    for item in rules:
        key = json.dumps(item[0])
        if key not in seen:
            seen[key] = True
            result.append(item)

    rules = result

    return {'accuracy': accuracy, 'cost': cost,'rules':rules,'default':classifier.default_label,'nums':len(rules)}

def cross_validate_cmar(file,minSup,minConf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    random.shuffle(data)
    dataset = pre_process(data, attributes, value_type)

    block_size = int(len(dataset) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(dataset))
    total_acc = 0
    total_time = 0
    total_rules_nums = 0
    train_size = int(len(dataset) * 0.9)
    minSup = int(train_size * minSup)

    for k in range(len(split_point) - 1):
        print("\nRound %d:" % k)
        training_dataset = dataset[:split_point[k]] + dataset[split_point[k + 1]:]
        test_dataset = dataset[split_point[k]:split_point[k + 1]]

        train_dataset_to_feed = []
        for data in training_dataset:
            train_dataset_to_feed.append(convert_data_to_dataentry(data, attributes))
        print("dataentry example is")
        train_dataset_to_feed[0].display()
        test_dataset_to_feed = []
        for data in test_dataset:
            dataentry = convert_data_to_dataentry(data, attributes)
            test_dataset_to_feed.append(dataentry)

        start = time.time()
        rules = get_rules(train_dataset_to_feed, minSup, minConf)
        cr_rule_list = rules

        root, header_table = createCRtree(cr_rule_list)
        tree_pruned_rules = root.getAllRules(header_table)
        retained_rules, default_label = pruneByCoverage(train_dataset_to_feed, tree_pruned_rules)
        classifier = CMARClassifier(tree_pruned_rules, default_label, train_dataset_to_feed, len(train_dataset_to_feed))

        accuracy, rules = get_acc(classifier, test_dataset_to_feed, attributes)
        end = time.time()
        total_time = end - start

        seen = {}
        result = []

        for item in rules:
            key = json.dumps(item[0])
            if key not in seen:
                seen[key] = True
                result.append(item)

        rules = result

        total_time = total_time + (end - start)
        total_acc += accuracy
        total_rules_nums += len(rules)

    return {'accuracy': round(total_acc / 10 * 100,3), 'num_rules': total_rules_nums / 10, 'cost': round(total_time / 10,3)}
