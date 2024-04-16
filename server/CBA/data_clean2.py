# from pre_procecss1 import *
# 找出众数
from CBA.pre_procecss1 import Block, partition, fill_missing_values


# 移除？后计算众数，

def get_discretization_data(data_column, class_column):
    size = len(data_column)
    result_list = []
    for i in range(size):
        result_list.append([data_column[i], class_column[i]])
    return result_list
def replace_numerical(data, column_no, walls):
    size = len(data)
    num_spilt_point = len(walls)
    for i in range(size):
        if data[i][column_no] > walls[num_spilt_point - 1]:
            data[i][column_no] = num_spilt_point + 1
            continue
        for j in range(0, num_spilt_point):
            if data[i][column_no] <= walls[j]:
                data[i][column_no] = j + 1
                break
    return data


def replace_categorical(data, column_no):
    size = len(data)
    classes = set([x[column_no] for x in data])
    classes_no = dict([(label, 0) for label in classes])
    j = 1
    for i in classes:
        classes_no[i] = j
        j += 1
    for i in range(size):
        data[i][column_no] = classes_no[data[i][column_no]]
    return data, classes_no


def discard(data, discard_list):
    size = len(data)
    length = len(data[0])
    data_result = []
    for i in range(size):
        data_result.append([])
        for j in range(length):
            if j not in discard_list:
                data_result[i].append(data[i][j])
    return data_result

def pre_process(data, attribute, value_type):
    column_num = len(data[0])
    size = len(data)
    class_column = [x[-1] for x in data]
    discard_list = []
    for i in range(0, column_num - 1):
        data_column = [x[i] for x in data]

        # process missing values
        missing_values_ratio = data_column.count('?') / size
        if missing_values_ratio > 0.5:
            discard_list.append(i)
            continue
        elif missing_values_ratio > 0:
            data = fill_missing_values(data, i)
            data_column = [x[i] for x in data]

        # discretization
        if value_type[i] == 'numerical':
            discretization_data = get_discretization_data(data_column, class_column)
            block = Block(discretization_data)
            walls = partition(block)
            if len(walls) == 0:
                max_value = max(data_column)
                min_value = min(data_column)
                print("Attribute: ",attribute[i])
                step = (max_value - min_value) / 3
                walls.append(min_value + step)
                walls.append(min_value + 2 * step)
            #print(attribute[i] + ":", walls)        # print out split points
            data = replace_numerical(data, i, walls)
        elif value_type[i] == 'categorical':
            data, classes_no = replace_categorical(data, i)
            print(attribute[i] + ":", classes_no)   # print out replacement list

    # discard
    if len(discard_list) > 0:
        data = discard(data, discard_list)
        print("discard:", discard_list)             # print out discard list
    return data