import functools
import sys


def is_satisfy(datacase,rulecase):

  result =  all(elem in datacase[:-1] for elem in rulecase[0])
  if not result:
  #if datacase[:-2] != rulecase[0] or datacase[-1] != rulecase[1]: #if datacase elements do not match condset, return none
    return None
  elif datacase[-1] == rulecase[1]: #if condset & class label match
    return True
  else:
    return False

# main method of CBA-CB: M1
class Classifier:
    """
    This class is our classifier.
    """
    def __init__(self):
        self.rule_list = list()
        self.default_class = None
        self._error_list = list()
        self._default_class_list = list()

    # insert a rule into rule_list, then choose a default class, and calculate the errors (see line 8, 10 & 11)
    def insert(self, rule, dataset):
        #print("Insert")
        self.rule_list.append(rule)             # insert r at the end of C
        self.sel_defclass(dataset)     # select a default class for the current C
        self.comp_err(dataset)            # compute the total number of errors of C

    # select the majority class in the remaining data
    def sel_defclass(self, dataset):
        #print("Select default class")
        class_column = [x[-1] for x in dataset]
        class_label = set(class_column)
        max = 0
        current_default_class = None
        for label in class_label:
            if class_column.count(label) >= max:
                max = class_column.count(label)
                current_default_class = label
        self._default_class_list.append(current_default_class)

    # compute the total number of errors
    def comp_err(self, dataset):
        #print("Compute error")
        if len(dataset) <= 0:
            self._error_list.append(sys.maxsize)
            return

        error_number = 0

        # the total number of errors that have been made by all the selected rules in C
        for case in dataset:
            is_cover = False
            for rule in self.rule_list:
                if is_satisfy(case, rule):
                    is_cover = True
                    break
            if not is_cover:
                error_number += 1

        # the number of errors to be made by the default class in the training set
        class_column = [x[-1] for x in dataset]
        error_number += len(class_column) - class_column.count(self._default_class_list[-1])
        self._error_list.append(error_number)

    # see line 14 and 15, to get the final classifier
    def discard(self):
        #print("discard")
        # find the first rule p in C with the lowest total number of errors and drop all the rules after p in C
        index = self._error_list.index(min(self._error_list))
        self.rule_list = self.rule_list[:(index+1)]
        self._error_list = None

        # assign the default class associated with p to default_class
        self.default_class = self._default_class_list[index]
        self._default_class_list = None

    # just print out all selected rules and default class in our classifier
    def print(self):
        print("Selected Rules: ")
        for rule in self.rule_list:
            print(rule)
        print("default_class:", self.default_class)

# sort the set of generated rules car according to the precedence and return the sorted rule list
def prec_sort(car):
    def cmp_method(a, b):
        if a[3] < b[3]:     # 1. the confidence of ri > rj
            return 1
        elif a[3] == b[3]:
            if a[2] < b[2]:       # 2. their confidences are the same, but support of ri > rj
                return 1
            elif a[2] == b[2]:
                if len(a[0]) < len(b[0]):   # 3. both confidence & support are the same, ri earlier than rj
                    return -1
                elif len(a[0]) == len(b[0]):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = car
    rule_list.sort(key=functools.cmp_to_key(cmp_method))
    # for a,b in itertools.combinations_with_replacement(rule_list,2):
    #   while(rule_list.index(a)!=rule_list.index(a)):
    #     cmp_method(a,b)
    return rule_list




def classifier_builder_m1(cars, dataset):
    #print("Entered builder")
    classifier = Classifier()
    #print("after Classifier()")
    cars_list = prec_sort(cars)
    print(cars_list)
    for rule in cars_list:
        #print("inside loop")
        temp = []
        mark = False
        for i in range(len(dataset)):
            #print("inside inner loop")
            is_satisfy_value = is_satisfy(dataset[i], rule)
            #print("is_satisfy_value: ",is_satisfy_value)
            if is_satisfy_value is not None:
                temp.append(i)
                if is_satisfy_value:
                    mark = True
        #print("mark: ",mark,"dataset: ",dataset[i])
        if mark:
            temp_dataset = list(dataset)
            for index in temp:
                temp_dataset[index] = []
            while [] in temp_dataset:
                temp_dataset.remove([])
            dataset = temp_dataset
            classifier.insert(rule, dataset)
            #print("inserted")
    classifier.discard()
    return classifier

# classifier_m1 = classifier_builder_m1(cars, df)