import ast

import server.APR.apr_rg
from functools import cmp_to_key
import sys
import time


def is_satisfy(datacase, rule):

    for item in rule.cond_set:
        # print("item",item)
        if datacase[item] != rule.cond_set[item]:
            return None
    if datacase[-1] == rule.class_label:
        return True
    else:
        return False

def is_satisfy_1(rule1, rule):
    # arr=[item for item in rule.cond_set]
    brr=[item for item in rule1.cond_set]

    for item in rule.cond_set:
        if item in brr:
            if rule1.cond_set[item] != rule.cond_set[item]:
                return None
        else:
            return None
    if rule1.class_label == rule.class_label:
        return True
    else:
        return False


class Classifier:
    """
    This class is our classifier. The rule_list and default_class are useful for outer code.
    """
    def __init__(self):
        self.rule_list = list()
        self.default_class = None
        self._error_list = list()
        self._default_class_list = list()

        self.all_rules = []

    # return "[name : %s,age:%d,score : %d]" % (self.name, self.age, self.score)

    # insert a rule into rule_list, then choose a default class, and calculate the errors (see line 8, 10 & 11)
    def insert(self, rule, dataset):
        self.rule_list.append(rule)             # insert r at the end of C




    # just print out all selected rules and default class in our classifier
    def print(self):
        for rule in self.rule_list:
            # print(ast.literal_eval(str(rule)))
            rule.print_rule()
            # print(rule,11)
            self.all_rules.append(rule.one_rule)
        # print(self.all_rules)
        print("default_class:", self.default_class)

# sort the set of generated rules car according to the relation ">", return the sorted rule list

def mergesort(arr):
    # print("arr:",len(arr))
    if len(arr)>1:
        mid=len(arr)//2
        left=arr[:mid]
        right=arr[mid:]
        mergesort(left)
        mergesort(right)
        i=0
        j=0
        k=0
        while i<len(left) and j<len(right):
            a=left[i]
            b=right[j]
            if a.confidence < b.confidence:     # 1. the confidence of ri > rj
                arr[k]=right[j]
                j+=1

            elif a.confidence == b.confidence:
                if a.support < b.support:       # 2. their confidences are the same, but support of ri > rj
                    arr[k]=right[j]
                    j+=1
                elif a.support == b.support:
                    if len(a.cond_set) < len(b.cond_set):   # 3. both confidence & support are the same, ri earlier than rj
                        arr[k]=right[j]
                        j+=1
                    else:
                        arr[k]=left[i]
                        i+=1
                else:
                    arr[k]=left[i]
                    i+=1
            else:
                arr[k]=left[i]
                i+=1
            k+=1
        while i<len(left):
            arr[k]=left[i]
            i+=1
            k+=1
        while j<len(right):
            arr[k]=right[j]
            j+=1
            k+=1

def sort1(car):
    def cmp_method(a, b):
        if a.confidence < b.confidence:     # 1. the confidence of ri > rj
            return 1
        elif a.confidence == b.confidence:
            if a.support < b.support:       # 2. their confidences are the same, but support of ri > rj
                return 1
            elif a.support == b.support:
                if len(a.cond_set) < len(b.cond_set):   # 3. both confidence & support are the same, ri earlier than rj
                    return -1
                elif len(a.cond_set) == len(b.cond_set):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = list(car)
    rule_list.sort(key=cmp_to_key(cmp_method))
    return rule_list



# main method of apr-CB: M1
def classifier_builder_m1(cars, dataset,min_support,length,u):
    classifier = Classifier()

    mergesort(u)
    cars_list=u
    # print([cars_list[i].cond_set for i in range(len(cars_list))])
    while cars_list:
        # print("len:",len(cars_list))
        rule=cars_list.pop(0)
        # print("hi:",rule.cond_set," ",rule.class_label)
        temp=[]
        mark=False
        for i in range(len(dataset)):
            is_satisfy_value=is_satisfy(dataset[i],rule)
            if is_satisfy_value is not None:
                temp.append(i)
                if is_satisfy_value:
                    mark=True

        if mark:
            temp_dataset=list(dataset)
            for index in temp:
                temp_dataset[index]=[]
            while [] in temp_dataset:
                temp_dataset.remove([])
            dataset=temp_dataset
            classifier.insert(rule,dataset)

            # print(dataset)
            temp_arp=list(cars_list)
            for i in range(len(cars_list)):
                cars_list[i].cond_sup_count, cars_list[i].rule_sup_count = cars_list[i]._get_sup_count(dataset)
                cars_list[i].support = cars_list[i]._get_support(length)

                cars_list[i].confidence = cars_list[i]._get_confidence()

                if cars_list[i].support<min_support:
                    # print(cars_list[i].cond_set,"sup:",cars_list[i].support)
                    temp_arp[i]=[]


            while [] in temp_arp:
                temp_arp.remove([])
            cars_list=temp_arp

        mergesort(cars_list)


    if len(dataset)>0:
        classes=set([x[-1] for x in dataset])
        temp=[x[-1] for x in dataset]
        count=0
        choice=None
        for k in classes:
            s=temp.count(k)
            if s>count:
                count=s
                choice=k
        classifier.default_class=choice
    else:
        classes=set([x.class_label for x in classifier.rule_list])
        temp=[x.class_label for x in classifier.rule_list]
        count=0
        choice=None
        for k in classes:
            s=temp.count(k)
            if s>count:
                count=s
                choice=k
        classifier.default_class=choice

    return classifier

def sort_dict(val):
    def cmp_dict(a,b):
        s1=list(a.cond_set.keys())
        s2=list(b.cond_set.keys())
        # print("s1",s1,"s2",s2)
        for i in range(len(s1)):
            if s1[i]>s2[i]:
                return 1
            elif s1[i]<s2[i]:
                return -1

        return 1

    rule_list = list(val)
    rule_list.sort(key=cmp_to_key(cmp_dict))
    # print([x.cond_set for x in rule_list])
    return rule_list



