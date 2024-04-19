# A block to be split
# It has 4 member:
#   data: the data table with a column of continuous-valued attribute and a column of class label
#   size: number of data case in this table
#   number_of_classes: obviously, the number of class in this table
#   entropy: entropy of dataset
import math


class Block:
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        classes = set([x[1] for x in data])     # get distinct class labels in this table
        self.number_of_classes = len(set(classes))
        self.entropy = calculate_entropy(data)


# Calculate the entropy of dataset
# parameter data: the data table to be used
def calculate_entropy(data):
    number_of_data = len(data)
    classes = set([x[1] for x in data])
    class_count = dict([(label, 0) for label in classes])
    for data_case in data:
        class_count[data_case[1]] += 1      # count the number of data case of each class
    entropy = 0
    for c in classes:
        p = class_count[c] / number_of_data
        entropy -= p * math.log2(p)         # calculate information entropy by its formula, where the base is 2
    return entropy


# Compute Gain(A, T: S) mentioned in Dougherty, Kohavi & Sahami (1995), i.e. entropy gained by splitting original_block
#   into left_block and right_block
# original_block: the block before partition
# left_block: the block split which its value below boundary
# right_block: the block above boundary
def entropy_gain(original_block, left_block, right_block):
    gain = original_block.entropy - \
            ((left_block.size / original_block.size) * left_block.entropy +
            (right_block.size / original_block.size) * right_block.entropy)
    return gain


# Get minimum entropy gain required for a split of original_block into 2 blocks "left" and "right", see Dougherty,
#   Kohavi & Sahami (1995)
# original_block: the block before partition
# left_block: the block split which its value below boundary
# right_block: the block above boundary
def min_gain(original_block, left_block, right_block):
    delta = math.log2(math.pow(3, original_block.number_of_classes) - 2) - \
            (original_block.number_of_classes * original_block.entropy -
             left_block.number_of_classes * left_block.entropy -
             right_block.number_of_classes * right_block.entropy)
    gain_sup = math.log2(original_block.size - 1) / original_block.size + delta / original_block.size
    return gain_sup


# Identify the best acceptable value to split block
# block: a block of dataset
# Return value: a list of (boundary, entropy gain, left block, right block) or
#   None when it's unnecessary to split
def split(block):
    candidates = [x[0] for x in block.data]     # candidates is a list of values can be picked up as boundary
    candidates = list(set(candidates))          # get different values in table
    candidates.sort()                           # sort ascending
    candidates = candidates[1:]                 # discard smallest, because by definition no value is smaller

    wall = []       # wall is a list storing final boundary
    for value in candidates:
        # split by value into 2 groups, below & above
        left_data = []
        right_data = []
        for data_case in block.data:
            if data_case[0] < value:
                left_data.append(data_case)
            else:
                right_data.append(data_case)

        left_block = Block(left_data)
        right_block = Block(right_data)

        gain = entropy_gain(block, left_block, right_block)
        threshold = min_gain(block, left_block, right_block)

        # minimum threshold is met, the value is an acceptable candidate
        if gain >= threshold:
            wall.append([value, gain, left_block, right_block])

    if wall:    # has candidate
        wall.sort(key=lambda wall: wall[1], reverse=True)   # sort descending by "gain"
        return wall[0]      # return best candidate with max entropy gain
    else:
        return None         # no need to split


# Top-down recursive partition of a data block, append boundary into "walls"
# block: a data block
def partition(block):
    walls = []

    # inner recursive function, accumulate the partitioning values
    # sub_block: just a data block
    def recursive_split(sub_block):
        wall_returned = split(sub_block)        # binary partition, get bin boundary
        if wall_returned:                       # still can be spilt
            walls.append(wall_returned[0])      # record this partitioning value
            recursive_split(wall_returned[2])   # recursively process left block
            recursive_split(wall_returned[3])   # recursively split right block
        else:
            return                              # end of recursion

    recursive_split(block)      # call inner function
    walls.sort()                # sort boundaries descending
    return walls

def get_mode(arr):
    mode = []
    arr_appear = dict((a, arr.count(a)) for a in arr)   # count appearance times of each key
    if max(arr_appear.values()) == 1:       # if max time is 1
        return      # no mode here
    else:
        for k, v in arr_appear.items():     # else, mode is the number which has max time
            if v == max(arr_appear.values()):
                mode.append(k)
    return mode[0]  # return first number if has many modes


# Fill missing values in column column_no, when missing values ration below 50%.
# data: original data list
# column_no: identify the column No. of that to be filled
def fill_missing_values(data, column_no):
    size = len(data)
    column_data = [x[column_no] for x in data]      # get that column
    while '?' in column_data:
        column_data.remove('?')
    mode = get_mode(column_data)
    for i in range(size):
        if data[i][column_no] == '?':
            data[i][column_no] = mode              # fill in mode
    return data


# Get the list needed by rmep.py, just glue the data column with class column.
# data_column: the data column
# class_column: the class label column
def get_discretization_data(data_column, class_column):
    size = len(data_column)
    result_list = []
    for i in range(size):
        result_list.append([data_column[i], class_column[i]])
    return result_list


# Replace numerical data with the No. of interval, i.e. consecutive positive integers.
# data: original data table
# column_no: the column No. of that column
# walls: the split point of the whole range
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


# Replace categorical values with a positive integer.
# data: original data table
# column_no: identify which column to be processed
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


# Discard all the column with its column_no in discard_list
# data: original data set
# discard_list: a list of column No. of the columns to be discarded
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


# Main method here, see Description in detail
# data: original data table
# attribute: a list of the name of attribute
# value_type: a list identifying the type of each column
# Returned value: a data table after process
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
        if value_type[i] == 'float64':
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
        elif value_type[i] == 'object':
            data, classes_no = replace_categorical(data, i)
            print(attribute[i] + ":", classes_no)   # print out replacement list

    # discard
    if len(discard_list) > 0:
        data = discard(data, discard_list)
        print("discard:", discard_list)             # print out discard list
    return data