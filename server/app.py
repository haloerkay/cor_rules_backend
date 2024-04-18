from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import pandas as pd
from CBA.CBA_CG_M1 import classifier_builder_m1, is_satisfy
from CBA.CBA_CG_M2 import classifier_builder_m2
from CBA.data_clean2 import pre_process
from CBA.rule_generate3 import preprocess_data, split_classes_ids, CARapriori, postprocess_data
from CMAR.CMAR_Classifier import *
from CMAR.CR_Tree import *
from CMAR.FP_Tree import *
from CMAR.cbaLib.pre_processing import *
from CMAR.cbaLib.validation import *

MINSUP = 10
MINCONF = 0.65
rules = []

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=[ 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']

        upload_folder = 'dataset'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        return "success"
    else:
        return 'file not uploaded'


@app.route('/cba/<file>', methods=[ 'GET'])
def get_cba_result(file):
    df = pd.read_csv('./dataset/'+file+'.csv')
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc

    d = pre_process(data, attributes, value_type)
    for i in range(len(d)):
        for j in range(len(d[i]) - 1):
            d[i][j] = str("(") + str(j) + "," + str(d[i][j]) + str(")")
    d = pd.DataFrame(d)
    # 原数据70% 作为样本，随机种子为25
    df = d.sample(frac=0.7, random_state=10)
    test_df = d.drop(df.index)
    d = d.values.tolist()
    test_df = test_df.values.tolist()
    classLabels = pd.unique(df[len(df.columns) - 1])

    transactions, replacement_dict, inverse_dict = preprocess_data(df)
    car = CARapriori(transactions)
    print("Car: ", car)
    ids, classes = split_classes_ids(replacement_dict, classLabels)

    minsup = 0.01
    minconf = 0.5
    rules = car.run(ids, classes, minsup, minconf, 3)
    final = postprocess_data(rules, inverse_dict)
    cars = final.values.tolist()
    df = df.values.tolist()

    t1 = time.time()
    classifier_m1 = classifier_builder_m1(cars, df)
    print(f'M1-coast:{time.time() - t1:.4f}s')

    t2 = time.time()
    classifier_m2 = classifier_builder_m2(cars, df)
    print(f'M2-coast:{time.time() - t2:.4f}s')

    # calculates and returns the accuracy of the classifier on the dataset
    def get_accuracy(classifier, dataset):
        size = len(dataset)
        correct_match = 0
        error_number = 0
        for case in dataset:
            is_satisfy_value = False
            for rule in classifier.rule_list:
                is_satisfy_value = is_satisfy(case, rule)
                # print(is_satisfy_value)
                if is_satisfy_value == True:
                    correct_match += 1
                    break
            if is_satisfy_value == False:
                error_number += 1
        return correct_match / (error_number + correct_match)

    block_size = int(len(test_df) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(test_df))
    for k in range(len(split_point) - 1):
        testt_df = d[split_point[k]:split_point[k + 1]]
        print("Accuracy", k + 1, ": ", get_accuracy(classifier_m1, testt_df))

    accuracy_m1 = get_accuracy(classifier_m1, d)
    print("Accuracy for M1: ", accuracy_m1)

    # accuracy of M2
    accuracy_m2 = get_accuracy(classifier_m2, d)
    print("Accuracy for M2: ", accuracy_m2)
    return jsonify([accuracy_m1,accuracy_m2])


@app.route('/cmar/<file>', methods=[ 'GET'])
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
    return jsonify(acc)


if __name__ == '__main__':
    app.run(debug = True)
