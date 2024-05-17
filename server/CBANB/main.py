import pandas as pd

from server.CBANB.read import read
from server.CBANB.pre_processing import pre_process
from server.CBANB.cba_rg import rule_generator
from server.CBANB.cba_cb_m1 import classifier_builder_m1
from server.CBANB.cba_cb_m1 import is_satisfy
from server.CBANB.cba_cb_m2 import classifier_builder_m2
import time
import random
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

# def get_accuracy(classifier, dataset):
#     size = len(dataset)
#     correct_number = 0
#     for case in dataset:
#         for rule in classifier.rule_list:
#             is_satisfy_value = is_satisfy(case, rule)
#             if is_satisfy_value or classifier.default_class == case[-1]:
#                 correct_number += 1
#                 break
#     return correct_number / size

    # size = len(dataset)
    # error_number = 0
    # for case in dataset:
    #     is_satisfy_value = False
    #     for rule in classifier.rule_list:
    #         is_satisfy_value = is_satisfy(case, rule)
    #         print(case[-1])
    #         if is_satisfy_value == True:
    #             break
    #     if is_satisfy_value == False:
    #         if classifier.default_class != case[-1]:
    #             error_number += 1
    # return 1 - error_number / size

def cba_m1_prune(file, minsup, minconf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    random.shuffle(data)
    dataset = pre_process(data, attributes, value_type)

    train_ratio = 0.8
    train_size = int(len(dataset) * train_ratio)
    random.shuffle(dataset)
    training_dataset = dataset[:train_size]
    test_dataset = dataset[train_size:]

    start_time = time.time()
    cars = rule_generator(training_dataset, minsup, minconf)
    classifier_m1 = classifier_builder_m1(cars, training_dataset)
    end_time = time.time()
    cost = end_time - start_time

    cars.prune_rules(training_dataset)
    cars.rules = cars.pruned_rules
    classifier_m1.print()
    accuracy = get_accuracy(classifier_m1, test_dataset)

    cars.print_pruned_rule(minsup, minconf)
    # all_rules = cars.all_rules
    all_rules = classifier_m1.all_rules
    return {'accuracy': accuracy, 'cost': cost,'rules': all_rules}

def cross_validate_m1(file, minsup, minconf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    random.shuffle(data)
    dataset = pre_process(data, attributes, value_type)

    block_size = int(len(dataset) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(dataset))

    total_time = 0
    total_car_number = 0
    total_classifier_rule_num = 0
    accuracy_total = 0

    for k in range(len(split_point)-1):
        print("\nRound %d:" % k)

        training_dataset = dataset[:split_point[k]] + dataset[split_point[k+1]:]
        test_dataset = dataset[split_point[k]:split_point[k+1]]

        start_time = time.time()
        cars = rule_generator(training_dataset, minsup, minconf)
        cars.prune_rules(training_dataset)
        cars.rules = cars.pruned_rules

        cars.print_pruned_rule(minsup, minconf)
        print(cars.all_rules)

        classifier_m1 = classifier_builder_m1(cars, training_dataset)
        end_time = time.time()
        total_time += end_time - start_time

        accuracy = get_accuracy(classifier_m1, test_dataset)
        accuracy_total += accuracy

        total_car_number += len(cars.rules)
        total_classifier_rule_num += len(classifier_m1.rule_list)

        # print("CBA's error rate with pruning: %.1lf%%" % (accuracy * 100))
        # print("No. of CARs with pruning: %d" % len(cars.rules))
        # print("CBA-RG's run time with pruning: %.2lf s" % cba_rg_runtime)
        # print("CBA-CB M1's run time with pruning: %.2lf s" % cba_cb_runtime)
        # print("No. of rules in classifier of CBA-CB M1 with pruning: %d" % len(classifier_m1.rule_list))

    accuracy = accuracy_total / 10 * 100
    num_rules = int(total_classifier_rule_num) / 10
    cost = total_time / 10
    return {'accuracy': round(accuracy,3), 'num_rules': num_rules, 'cost':round(cost,4)}


def cba_m2_prune(file, minsup, minconf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')

    dataset = pre_process(data, attributes, value_type)
    train_ratio = 0.8
    train_size = int(len(dataset) * train_ratio)
    random.shuffle(dataset)
    training_dataset = dataset[:train_size]
    test_dataset = dataset[train_size:]

    start_time = time.time()
    cars = rule_generator(training_dataset, minsup, minconf)
    classifier_m2 = classifier_builder_m2(cars, training_dataset)
    end_time = time.time()
    cost = end_time-start_time

    cars.prune_rules(training_dataset)
    cars.rules = cars.pruned_rules
    classifier_m2.print()

    accuracy = get_accuracy(classifier_m2, test_dataset)
    cars.print_pruned_rule(minsup, minconf)
    # all_rules = cars.all_rules
    all_rules = classifier_m2.all_rules
    print(len(classifier_m2.rule_list),len(all_rules))
    return {'accuracy': accuracy, 'cost': cost,'rules': all_rules}

def cross_validate_m2(file, minsup, minconf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    random.shuffle(data)
    dataset = pre_process(data, attributes, value_type)

    block_size = int(len(dataset) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(dataset))

    total_time = 0
    total_car_number = 0
    total_classifier_rule_num = 0
    accuracy_total = 0

    for k in range(len(split_point)-1):
        print("\nRound %d:" % k)

        training_dataset = dataset[:split_point[k]] + dataset[split_point[k+1]:]
        test_dataset = dataset[split_point[k]:split_point[k+1]]

        start_time = time.time()
        cars = rule_generator(training_dataset, minsup, minconf)
        cars.prune_rules(training_dataset)
        cars.rules = cars.pruned_rules

        cars.print_pruned_rule(minsup, minconf)
        print(cars.all_rules)


        classifier_m2 = classifier_builder_m2(cars, training_dataset)
        end_time = time.time()
        total_time += end_time - start_time

        accuracy = get_accuracy(classifier_m2, test_dataset)
        accuracy_total += accuracy

        total_car_number += len(cars.rules)
        total_classifier_rule_num += len(classifier_m2.rule_list)
    accuracy = accuracy_total / 10 * 100
    num_rules = int(total_classifier_rule_num) / 10
    cost = total_time / 10
    return {'accuracy': round(accuracy,3), 'num_rules': num_rules, 'cost':round(cost,4)}

def get_preprocess(file):
    df = pd.read_csv('./dataset/' + file + '.csv')
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc
    divided = pre_process(data, attributes, value_type)
    divided.insert(0,attributes)
    return divided