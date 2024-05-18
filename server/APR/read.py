"""
Description: Read initial dataset and decode it into a list. Here we replace all missing value and discretizate
    the numerical values.
Input: initial dataset stored in *.data file, and scheme description stored in *.names file.
Output: a data list after pre-processing.
Author: CBA Studio
"""
import csv

import pandas as pd
# convert string-type value into float-type.
# data: data list returned by read_data.
# value_type: list returned by read_scheme.
def str2numerical(data, value_type):
    size = len(data)
    columns = len(data[0])
    for i in range(size):
        for j in range(columns-1):
            if value_type[j] == 'float64' and data[i][j] != '?':
                data[i][j] = float(data[i][j])
    return data

# Main method in this file, to get data list after processing and scheme list.
# data_path: tell where *.data file stores.
# scheme_path: tell where *.names file stores.
def read(data_path):
    # data = read_data(data_path)
    df = pd.read_csv(data_path)
    data = df.values.tolist()
    attributes = df.columns.tolist()
    value_type = df.dtypes.iloc
    data = str2numerical(data, value_type)
    return data, attributes, value_type

