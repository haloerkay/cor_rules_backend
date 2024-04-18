import time

import pandas as pd
from flask import jsonify

from server.CBA.CBA_CG_M1 import classifier_builder_m1, is_satisfy
from server.CBA.CBA_CG_M2 import classifier_builder_m2
from server.CBA.data_clean2 import pre_process
from server.CBA.rule_generate3 import preprocess_data, split_classes_ids, CARapriori, postprocess_data


minsup = 0.01
minconf = 0.5

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
    return [accuracy_m1,accuracy_m2]
