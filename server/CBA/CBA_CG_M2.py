import functools
def is_satisfy(datacase,rulecase):
  result =  all(elem in datacase[:-1] for elem in rulecase[0])
  if not result:
    return None
  elif datacase[-1] == rulecase[1]:
    return True
  else:
    return False

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

class Classifier_m2:
    def __init__(self):
        self.rule_list = list()
        self.default_class = None
        self._default_class_list = list()
        self._total_errors_list = list()

    # insert a new rule into classifier
    def add(self, rule, default_class, total_errors):
        #print("Adding")
        self.rule_list.append(rule)
        self._default_class_list.append(default_class)
        self._total_errors_list.append(total_errors)

    def discard(self):
        index = self._total_errors_list.index(min(self._total_errors_list))
        self.rule_list = self.rule_list[:(index + 1)]
        self._total_errors_list = None

        self.default_class = self._default_class_list[index]
        self._default_class_list = None

    # just print out rules and default class label
    def print(self):
        print("Selected Rules: ")
        for rule in self.rule_list:
            print(rule[:4])
        print("default_class:", self.default_class)

def return_cases(dataset):
        class_column = [x[-1] for x in dataset]
        class_label = set(class_column)
        x = dict((x, 0) for x in class_label)
        #print(x)
        return x

# convert ruleitem of class RuleItem to rule of class Rule
def ruleitem2rule(rule_item, dataset):
    rule_item.append(return_cases(dataset))
    rule_item.append(set())
    #rule = Rule(rule_item.cond_set, rule_item.class_label, dataset)
    #print(rule_item)
    return rule_item


# finds the highest precedence rule that covers the data case d from the set of rules having the same class as d.
def maxCoverRule_correct(cars_list, data_case):
    for i in range(len(cars_list)):
        if cars_list[i][1] == data_case[-1]:
            if is_satisfy(data_case, cars_list[i]):
                return i
    return None


# finds the highest precedence rule that covers the data case d from the set of rules having the different class as d.
def maxCoverRule_wrong(cars_list, data_case):
    for i in range(len(cars_list)):
        if cars_list[i][1] != data_case[-1]:
            temp_data_case = data_case[:-1]
            temp_data_case.append(cars_list[i][1])
            if is_satisfy(temp_data_case, cars_list[i]):
                return i
    return None


# compare two rule, return the precedence.
#   -1: rule1 < rule2, 0: rule1 < rule2 (randomly here), 1: rule1 > rule2
def compare(rule1, rule2):
    if rule1 is None and rule2 is not None:
        return -1
    elif rule1 is None and rule2 is None:
        return 0
    elif rule1 is not None and rule2 is None:
        return 1

    if rule1[3] < rule2[3]:     # 1. the confidence of ri > rj
        return -1
    elif rule1[3] == rule2[3]:
        if rule1[2] < rule2[2]:       # 2. their confidences are the same, but support of ri > rj
            return -1
        elif rule1[2] == rule2[2]:
            if len(rule1[0]) < len(rule2[0]):   # 3. confidence & support are the same, ri earlier than rj
                return 1
            elif len(rule1[0]) == len(rule2[0]):
                return 0
            else:
                return -1
        else:
            return 1
    else:
        return 1


# finds all the rules in U that wrongly classify the data case and have higher precedences than that of its cRule.
def allCoverRules(u, data_case, c_rule, cars_list):
    w_set = []
    for rule_index in u:
        # have higher precedences than cRule
        if compare(cars_list[rule_index], c_rule) > 0:
            # wrongly classify the data case
            if is_satisfy(data_case, cars_list[rule_index]) == False:
                w_set.append(rule_index)
    return w_set


# counts the number of training cases in each class
def compClassDistr(dataset):
    class_distr = dict()

    if len(dataset) <= 0:
        class_distr = None

    dataset_without_null = dataset
    while [] in dataset_without_null:
        dataset_without_null.remove([])

    class_column = [x[-1] for x in dataset_without_null]
    class_label = set(class_column)
    for c in class_label:
        class_distr[c] = class_column.count(c)
    return class_distr


# sort the rule list order by precedence
def sort_with_index(q, cars_list):
    def cmp_method(a, b):
        # 1. the confidence of ri > rj
        if cars_list[a][3] < cars_list[b][3]:
            return 1
        elif cars_list[a][3] == cars_list[b][3]:
            # 2. their confidences are the same, but support of ri > rj
            if cars_list[a][2] < cars_list[b][2]:
                return 1
            elif cars_list[a][2] == cars_list[b][2]:
                # 3. both confidence & support are the same, ri earlier than rj
                if len(cars_list[a][0]) < len(cars_list[b][0]):
                    return -1
                elif len(cars_list[a][0]) == len(cars_list[b][0]):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = q
    rule_list.sort(key=functools.cmp_to_key(cmp_method))
    return rule_list


# get how many errors the rule wrongly classify the data case
def errorsOfRule(rule, dataset):
    error_number = 0
    for case in dataset:
        if case:
            if is_satisfy(case, rule) == False:
                error_number += 1
    return error_number


# choose the default class (majority class in remaining dataset)
def selectDefault(class_distribution):
    if class_distribution is None:
        return None

    max = 0
    default_class = None
    for index in class_distribution:
        if class_distribution[index] > max:
            max = class_distribution[index]
            default_class = index
    return default_class


# count the number of errors that the default class will make in the remaining training data
def defErr(default_class, class_distribution):
    if class_distribution is None:
        import sys
        return sys.maxsize

    error = 0
    for index in class_distribution:
        if index != default_class:
            error += class_distribution[index]
    return error


# main method, implement the whole classifier builder
def classifier_builder_m2(cars, dataset):
    classifier = Classifier_m2()

    cars_list = prec_sort(cars)
    for i in range(len(cars_list)):
        cars_list[i] = ruleitem2rule(cars_list[i], dataset)
        #print(cars_list[i])
    #for j in range()

    # stage 1
    q = [] # set
    u = [] # set
    a = [] # set
    mark_set = [] # set
    for i in range(len(dataset)):
        c_rule_index = maxCoverRule_correct(cars_list, dataset[i])
        w_rule_index = maxCoverRule_wrong(cars_list, dataset[i])
        if c_rule_index is not None:
            u.append(c_rule_index)
        if c_rule_index:
            cars_list[c_rule_index][4][dataset[i][-1]] += 1
        if c_rule_index and w_rule_index:
            if compare(cars_list[c_rule_index], cars_list[w_rule_index]) > 0:
                q.append(c_rule_index)
                mark_set.append(c_rule_index)
            else:
                a.append((i, dataset[i][-1], c_rule_index, w_rule_index))
        elif c_rule_index is None and w_rule_index is not None:
            a.append((i, dataset[i][-1], c_rule_index, w_rule_index))

    print("a: ",a)
    print("mark_set: ",mark_set)
    # stage 2
    for entry in a:
        lol = entry[3]
        if cars_list[lol] in mark_set:
            if entry[2] is not None:
                cars_list[entry[2]][4][entry[1]] -= 1
            cars_list[entry[3]][4][entry[1]] += 1
        else:
            if entry[2] is not None:
                w_set = allCoverRules(u, dataset[entry[0]], cars_list[entry[2]], cars_list)
            else:
                w_set = allCoverRules(u, dataset[entry[0]], None, cars_list)
            for w in w_set:
                cars_list[w][5].add((entry[2], entry[0], entry[1]))
                cars_list[w][4][entry[1]] += 1
            q = list(set().union(q,w_set))
            #q |= w_set

    # stage 3
    rule_errors = 0
    q = sort_with_index(q, cars_list)
    data_cases_covered = list([False] * len(dataset))
    for r_index in q:
        if cars_list[r_index][4][cars_list[r_index][1]] != 0:
            for entry in cars_list[r_index][5]:
                if data_cases_covered[entry[1]]:
                    cars_list[r_index][4][entry[2]] -= 1
                else:
                    if entry[0] is not None:
                        cars_list[entry[0]][4][entry[2]] -= 1
            for i in range(len(dataset)):
                datacase = dataset[i]
                if datacase:
                    is_satisfy_value = is_satisfy(datacase, cars_list[r_index])
                    if is_satisfy_value:
                        dataset[i] = []
                        data_cases_covered[i] = True
            rule_errors += errorsOfRule(cars_list[r_index], dataset)
            class_distribution = compClassDistr(dataset)
            default_class = selectDefault(class_distribution)
            default_errors = defErr(default_class, class_distribution)
            total_errors = rule_errors + default_errors
            classifier.add(cars_list[r_index], default_class, total_errors)
    classifier.discard()

    return classifier