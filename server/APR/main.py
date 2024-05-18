import random
import time

from server.APR.apr_cb_m1 import is_satisfy, sort_dict, classifier_builder_m1
from server.APR.apr_rg import rule_generator
from server.APR.pre_processing import pre_process
from server.APR.read import read
from server.APR.validation import acc

# def get_accuracy(classifier, dataset):
#     size = len(dataset)
#     correct_match = 0
#     error_number = 0
#     for case in dataset:
#         is_satisfy_value = False
#         for rule in classifier.rule_list:
#             is_satisfy_value = is_satisfy(case, rule)
#             #print(is_satisfy_value)
#             if is_satisfy_value == True:
#                 correct_match += 1
#                 break
#         if is_satisfy_value == False:
#             error_number += 1
#     return correct_match / (error_number + correct_match)
def get_accuracy(apr,test):
    temp=[]
    actual=[x[-1] for x in test]
    count=0
    for i in range(len(test)):
        flag1=True
        for j in range(len(apr.rule_list)):
            flag=True
            for item in apr.rule_list[j].condition_set:
                if test[i][item]!=apr.rule_list[j].condition_set[item]:
                    flag=False
                    break
            if flag:
                temp.append(apr.rule_list[j].class_label)
                if temp[-1]==actual[i]:
                    count+=1
                flag1=False
                break

        if flag1:
            temp.append(apr.default_class)
            if temp[-1]==actual[i]:
                count+=1

    res=count/len(test)
    return res

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
        if len(arr[i].condition_set)>max:
            max=len(arr[i].condition_set)
    T=[[] for i in range(max)]
    for i in range(len(arr)):
        T[len(arr[i].condition_set)-1].append(arr[i])
    u=[]
    for i in range(len(T)):
        T[i]=sort_dict(T[i])

        for j in T[i]:
            u.append(j)

    classifier = classifier_builder_m1(training_dataset,minsup,len(training_dataset),u)


    # 得到最终关联规则的方法:现在ruleitem类中获得一个完整的一维数组（one_rule）
    # 在classifier的for循环中得到完整的二维数组（all_rules）
    # 这个函数不能删，用于的到结果classifier.all_rules
    classifier.print()
    accuracy = get_accuracy(classifier,test_dataset)
    # print(res,classifier.all_rules,cost)
    end_time = time.time()
    cost = end_time - start_time
    return {'accuracy': accuracy, 'cost': cost, 'rules': classifier.all_rules}
def cross_validate_apr(file, minsup, minconf):
    data, attributes, value_type = read('./dataset/' + file + '.csv')
    random.shuffle(data)
    dataset = pre_process(data, attributes, value_type)

    block_size = int(len(dataset) / 10)
    split_point = [k * block_size for k in range(0, 10)]
    split_point.append(len(dataset))

    total_time = 0
    total_car_number = 0
    total_classifier_rule_num = 0
    total_accuracy = 0
    for k in range(len(split_point)-1):
        print("\nRound %d:" % k)

        training_dataset = dataset[:split_point[k]] + dataset[split_point[k+1]:]
        test_dataset = dataset[split_point[k]:split_point[k+1]]

        start_time = time.time()
        cars = rule_generator(training_dataset, minsup, minconf)


        arr=list(cars.rules_list)
        max=-1

        for i in range(len(arr)):
            if len(arr[i].condition_set)>max:
                max=len(arr[i].condition_set)
        T=[[] for i in range(max)]
        for i in range(len(arr)):
            T[len(arr[i].condition_set)-1].append(arr[i])
        u=[]
        for i in range(len(T)):
            T[i]=sort_dict(T[i])

            for j in T[i]:
                u.append(j)
        classifier= classifier_builder_m1(training_dataset,minsup,len(training_dataset),u)



        classifier.print()
        accuracy = get_accuracy(classifier, test_dataset)
        end_time = time.time()
        total_time += end_time - start_time

        total_accuracy += accuracy

        total_car_number += len(cars.rules)
        # yuanlaide
        total_classifier_rule_num += len(classifier.rule_list)
        # xiugaide
        # total_classifier_rule_num += len(classifier.all_rules)

    accuracy = total_accuracy / 10 *100
    total_rules = total_classifier_rule_num / 10
    cost = total_time / 10
    return {'accuracy': round(accuracy,3), 'num_rules': total_rules, 'cost':round(cost,4)}
    #
    # print("\n Average APR's accuracy :",(acc_total/10*100))
    # print("Average No. of CARs : ",(total_car_number / 10))
    # print("Average apr-RG's run time : " ,(apr_rg_total_runtime / 10))
    # print("Average apr-CB run time :  " ,(apr_cb_total_runtime / 10))
    # print("Average No. of rules in classifier of apr: " ,(total_classifier_rule_num / 10))

