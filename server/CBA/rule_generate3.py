import pandas as pd
import numpy as np
# from data_clean2 import *

def preprocess_data(df):
    values = set([np.nan])
    for col in df.columns:
        values = values.union(set(df[col].unique()))
    replacement_dict = {k: v for v, k in enumerate(values)}
    inverse_dict = dict(map(reversed, replacement_dict.items()))
    preprocessed_df = df.replace(replacement_dict)
    transactions = [[element for element in row if element != 0] for row in preprocessed_df.values.tolist()]

    return transactions, replacement_dict, inverse_dict

def postprocess_data(rules, inverse_dict):
    df = pd.DataFrame(rules, columns=['LHS', 'RHS', 'Support', 'Confidence'])
    df['RHS'] = df['RHS'].apply(lambda x: inverse_dict[x])
    df['LHS'] = df['LHS'].apply(lambda x: [inverse_dict[y] for y in list(x)] )

    return df

def split_classes_ids(replacement_dict, classes_list):
    classes = set([replacement_dict[i] for i in classes_list])
    ids = set(replacement_dict.values()) - classes
    return ids, classes


class CARapriori:

    def __init__(self, transactions):
        self.transactions = transactions
    def init_pass(self, ids, target_ids, min_support, min_confidence):
        # print("Init_pass")
        candidates = self.car_candidate_gen(target_ids, ids)
        condsupCount, rulesupCount = self.init_counters(candidates)

        condsupCount, rulesupCount = self.search(self.transactions, candidates, target_ids, condsupCount, rulesupCount)
        print(condsupCount)
        counters_rc_pruned, rulesupCount_pruned = self.prune(len(self.transactions), condsupCount, rulesupCount,
                                                             min_support, min_confidence)

        return counters_rc_pruned, rulesupCount_pruned

    def init_counters(self, candidate_sets):
        rulesupCount = {}
        condsupCount = {}
        for c in candidate_sets:
            rulesupCount[c] = 0
            condsupCount[c[0]] = 0

        return condsupCount, rulesupCount
    def car_candidate_gen(self, target_ids, f_k, c_condition_set=set()):
        c = list()
        for class_ in target_ids:
            for item_ in f_k:
                item_set = c_condition_set.copy()
                if isinstance(item_, tuple):
                    item_set.add(item_[0])
                else:
                    item_set.add(item_)
                item_set = tuple(item_set)
                c.append(tuple([item_set, class_]))
        return c
    def expand(self, last_pruned, target_ids):
        common_set = set()

        for key in last_pruned.keys():
            common_set.add(key[0])

        candidate_sets = set()
        for key in last_pruned.keys():
            new_set = common_set.copy()
            new_set.remove(key[0])

            candidates = self.car_candidate_gen(target_ids, new_set, set(key[0]))
            candidate_sets = candidate_sets.union(candidates)

        return candidate_sets
    def search(self, transactions, candidate_sets, target_ids, condsupCount, rulesupCount):
        # print("Search begins, before outer loop")
        for t in transactions:
            t_set = set(t)
            classes_in_trans = t_set.intersection(target_ids)
            found_in_transaction = {}
            # print("Before inner loop")
            for c in candidate_sets:
                # print("Inner loop")
                items_set = set(c[0])
                items_in_trans = t_set.intersection(items_set)

                if items_in_trans == items_set:
                    t_item_set = tuple(items_set)
                    if t_item_set not in found_in_transaction:
                        # print(t_item_set)
                        # print(condsupCount)
                        if condsupCount.get(t_item_set) == None:
                            condsupCount[t_item_set] = 0
                        condsupCount[t_item_set] += 1
                        found_in_transaction[t_item_set] = True

                    if c[1] in classes_in_trans:
                        rulesupCount[tuple(c)] += 1
            # print(condsupCount)

        return condsupCount, rulesupCount
    def prune(self, transactions_length, condsupCount, rulesupCount, min_support, min_confidence):
        condsupCount_pruned = dict()
        rulesupCount_pruned = dict()

        for key, val in condsupCount.items():
            if val > 0:
                support = round(val / transactions_length, 3)
                if support >= min_support:
                    condsupCount_pruned[key] = support

        for key, val in rulesupCount.items():
            if val > 0 and key[0] in condsupCount_pruned:
                confidence = round(val / condsupCount[key[0]], 3)
                if confidence >= min_confidence:
                    rulesupCount_pruned[key] = confidence

        return condsupCount_pruned, rulesupCount_pruned

    def add_rules(self, rules, counters_rc_pruned, rulesupCount_pruned):

        rules_before = len(rules)
        for key, val in rulesupCount_pruned.items():
            rules.add(tuple([key[0], key[1], counters_rc_pruned[key[0]], val]))
        rules_after = len(rules)
        return rules_after > rules_before
    def run(self, ids, target_ids, min_support=0.01, min_confidence=0.5, max_length=2):
        rules = set()
        counters_rc_pruned, rulesupCount_pruned = self.init_pass(ids, target_ids, min_support, min_confidence)
        rules_added = self.add_rules(rules, counters_rc_pruned, rulesupCount_pruned)
        if rules_added:
            for iteration in range(max_length):
                candidate_sets = self.expand(rulesupCount_pruned, target_ids)
                counters_rc, rulesupCount = self.init_counters(candidate_sets)
                counters_rc, rulesupCount = self.search(self.transactions, candidate_sets, target_ids, counters_rc,
                                                        rulesupCount)
                # prune
                counters_rc_pruned, rulesupCount_pruned = self.prune(len(self.transactions), counters_rc, rulesupCount,
                                                                     min_support, min_confidence)
                # add
                rules_added = self.add_rules(rules, counters_rc_pruned, rulesupCount_pruned)

                if not rules_added:
                    break
        return rules
