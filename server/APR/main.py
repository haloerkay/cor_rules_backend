import random
import time

from server.APR.apr_cb_m1 import is_satisfy, sort_dict, classifier_builder_m1
from server.APR.apr_rg import rule_generator
from server.APR.pre_processing import pre_process
from server.APR.read import read
from server.APR.validation import acc


def get_accuracy(classifier, dataset):
    size = len(dataset)
    correct_number = 0
    for case in dataset:
        for rule in classifier.rule_list:
            is_satisfy_value = is_satisfy(case, rule)
            if is_satisfy_value or classifier.default_class == case[-1]:
                correct_number += 1
                break
    return correct_number / size

def apr(file, minsup, minconf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    dataset = pre_process(data, attributes, value_type)

    train_ratio = 0.8
    train_size = int(len(dataset) * train_ratio)
    random.shuffle(dataset)
    training_dataset = dataset[:train_size]
    test_dataset = dataset[train_size:]

    start_time = time.time()
    cars = rule_generator(training_dataset, minsup, minconf)
    arr=list(cars.rules_list)
    max=-1
    for i in range(len(arr)):
        if len(arr[i].cond_set)>max:
            max=len(arr[i].cond_set)
    T=[[] for i in range(max)]
    for i in range(len(arr)):
        T[len(arr[i].cond_set)-1].append(arr[i])
    u=[]
    for i in range(len(T)):
        T[i]=sort_dict(T[i])

        for j in T[i]:
            u.append(j)

    classifier = classifier_builder_m1(cars, training_dataset,minsup,len(training_dataset),u)
    end_time = time.time()
    cost = end_time - start_time

    # 得到最终关联规则的方法:现在ruleitem类中获得一个完整的一维数组（one_rule）
    # 在classifier的for循环中得到完整的二维数组（all_rules）
    # 这个函数不能删，用于的到结果classifier.all_rules
    classifier.print()

    accuracy = get_accuracy(classifier,test_dataset)
    # print(res,classifier.all_rules,cost)

    return {'accuracy': accuracy, 'cost': cost, 'rules': classifier.all_rules}



# if __name__ == "__main__":
#     # using the relative path, all data sets are stored in datasets directory
#     file = 'iris.csv'
#
#     # just choose one mode to experiment by removing one line comment and running
#     min_support=0.01
#     min_conf=0.5
#     apr(file,min_support,min_conf)