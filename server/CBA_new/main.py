import pandas as pd

from server.CBA.CBA_CG_M1 import is_satisfy
from server.CBA_new.M1 import classifier_builder_m1
from server.CBA_new.M2 import classifier_builder_m2
from server.CBA_new.preprocess1 import pre_process
from server.CBA_new.rule_generate2 import preprocess_data, CARapriori, split_classes_ids, postprocess_data

def get_accuracy(classifier, dataset):
    size = len(dataset)
    correct_match = 0
    error_number = 0
    for case in dataset:
        is_satisfy_value = False
        for rule in classifier.rule_list:
            is_satisfy_value = is_satisfy(case, rule)
            #print(is_satisfy_value)
            if is_satisfy_value == True:
                correct_match += 1
                break
        if is_satisfy_value == False:
            error_number += 1
    return correct_match / (error_number + correct_match)

def get_cba_result(minsup,minconf,file):
    df = pd.read_csv('./dataset/' + file + '.csv')
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc
    d = pre_process(data, attributes, value_type)
    for i in range(len(d)):
        for j in range(len(d[i]) - 1):
            # print(df[i][j])
            d[i][j] = str("(") + str(j) + "," + str(d[i][j]) + str(
                ")")  # this has to be a datatype acceptable by pandas unique
    d = pd.DataFrame(d)
    df = d.sample(frac=0.7, random_state=25)
    test_df = d.drop(df.index)
    d = d.values.tolist()
    test_df = test_df.values.tolist()
    classLabels = pd.unique(df[len(df.columns) - 1])
    transactions, replacement_dict, inverse_dict = preprocess_data(df)
    car = CARapriori(transactions)
    ids, classes = split_classes_ids(replacement_dict, classLabels)
    
    rules = car.run(ids, classes, minsup, minconf, 3)
    print('CARs')
    final = postprocess_data(rules, inverse_dict)
    print(final)
    cars = final.values.tolist()
    df = df.values.tolist()
    classifier_m1 = classifier_builder_m1(cars, df)
    classifier_m2 = classifier_builder_m2(cars, df)
    block_size = int(len(test_df) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(test_df))
    for k in range(len(split_point) - 1):
        testt_df = d[split_point[k]:split_point[k + 1]]
        print("Accuracy", k + 1, ": ", get_accuracy(classifier_m1, testt_df))
    accuracy_m1 = get_accuracy(classifier_m1, d)
    print("Accuracy for M1: ", accuracy_m1)
    accuracy_m2 = get_accuracy(classifier_m2, d)
    print("Accuracy for M2: ", accuracy_m2)
    return [accuracy_m1, accuracy_m2]

