
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



def entropy_gain(original_block, left_block, right_block):
    gain = original_block.entropy - \
            ((left_block.size / original_block.size) * left_block.entropy +
            (right_block.size / original_block.size) * right_block.entropy)
    return gain



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
        wall_returned = split(sub_block)
        if wall_returned:
            walls.append(wall_returned[0])
            recursive_split(wall_returned[2])
            recursive_split(wall_returned[3])
        else:
            return

    recursive_split(block)      # call inner function
    walls.sort()                # sort boundaries descending
    return walls

