import numpy as np
import pandas as pd
from tqdm import tqdm
import glob
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import os
from pathlib import Path
import argparse

class Node:
    def __init__(self, n):
        self.name = n
class Graph:
    nodes = {}
    edges = []
    edge_indices = {}
    def add_node(self, node):
        if isinstance(node, Node) and node.name not in self.nodes:
            self.nodes[node.name] = node
            for row in self.edges:
                row.append(0)
            self.edges.append([0]*(len(self.edges)+1))
            self.edge_indices[node.name] = len(self.edge_indices)
            return True
        else:
            return False
    def add_edge (self, u, v, weight):
        if u in self.nodes and v in self.nodes:
            self.edges[self.edge_indices[u]][self.edge_indices[v]] += weight
            return True
        else:
            return False
    def get_adj_martix(self):
        return np.array(self.edges)

parser = argparse.ArgumentParser()
parser.add_argument("--from_item", help="from which number of item iterate",
                    type=int, default=1)
parser.add_argument("--to_item", help="till which number of item iterate",
                    type=int, default=1)
args = parser.parse_args()


tokens_price_list = sorted(glob.glob("ERC20-1h-data/*"))
transactions_csv_list = ['data/ftt.csv',
                         'data/vibe.csv',
                         'data/dlt.csv',
                         'data/lto.csv',
                         'data/oax.csv',
                         'data/celr.csv',
                         'data/hot.csv',
                         'data/sub.csv',
                         'data/nkn.csv',
                         'data/key.csv',
                         'data/fet.csv',
                         'data/appc.csv',
                         'data/sngls.csv',
                         'data/mda.csv',
                         'data/mith.csv',
                         'data/ren.csv',
                         'data/cdt.csv',
                         'data/dock.csv',
                         'data/blz.csv',
                         'data/data.csv',
                         'data/tusd.csv',
                         'data/link.csv']

print("iterating from ", args.from_item)
print("iterating to ", args.to_item)
print(transactions_csv_list[args.from_item:args.to_item])

contract_hashes = pd.read_csv("erc20_contracts_with_max_page.csv")

for path_to_csv in transactions_csv_list[args.from_item:args.to_item]:
    price_data_file = path_to_csv.split("/")[1].split(".")[0].upper() + "BTC-1h-data.csv"
    ftt = pd.read_csv( "ERC20-1h-data/" + price_data_file)
    ftt['timestamp'] = pd.to_datetime(ftt.timestamp)
    frame = pd.read_csv(path_to_csv)

    my_groups = frame.groupby('new_date')
    my_keys = my_groups.groups.keys()

    transactions_new = []
    verts_new = []
    transaction_prev = 0
    len_gg = 0
    from_nod = 0
    from_nods = []
    Graph.nodes = {}
    Graph.edges = []
    Graph.edge_indices = {}
    g = Graph()
    n = len(my_keys)
    previous_key = list(my_keys)[0]
    # cycle over days
    for k, i in tqdm(zip(my_keys,range(n))):
        # print('current date',k)
        # To check when we don't have data for several Days
        for j in range((pd.to_datetime(k) - pd.to_datetime(previous_key)).days - 1):
            # print('gddgdgf')
            verts_new.append([0] * 24)
            transactions_new.append([0] * 24)
            from_nods.append([0] * 24)
        day_group = my_groups.get_group(k)
        times = pd.to_datetime(day_group.timestamp)
        hour_groups = day_group.groupby(times.dt.hour)

        # print('Hour',hour_groups.groups)
        verts_new.append([0] * 24)
        transactions_new.append([0] * 24)
        from_nods.append([0] * 24)
        # Cycle over hours
        for key, indexes in hour_groups.groups.items():
            from_nod = 0
            # Cyvle over elements in data related to this hour
            for index in indexes:
                a = Node(day_group['from_address'][index])
                if (g.add_node(a) == True) or (
                        day_group['from_address'][index] not in day_group['from_address'][0:index]):
                    from_nod += 1

                a = Node(day_group['to_address'][index])
                g.add_node(a)
                # Adding edges
                hour_group = hour_groups.get_group(key)
                for fromm, tooo, value in zip(hour_group['from_address'],hour_group['to_address'],
                                            hour_group['token_qty_values']):
                    g.add_edge(fromm,tooo,weight=int(value))

            # print(transactions_new[i])
            transactions_new[i][key] = g.get_adj_martix().sum() - transaction_prev
            transaction_prev = g.get_adj_martix().sum()
            verts_new[i][key] = len(g.nodes) - len_gg
            len_gg = len(g.nodes)
            # print(key)
            # print(from_nod)
            from_nods[i][key] = from_nod
        previous_key = k
        # print('prev',previous_key)

    flat_list1 = [item for sublist in transactions_new for item in sublist]

    num_zeros = len(ftt) - len(flat_list1)
    flat_list1.extend([0] * num_zeros)

    flat_list2 = [item for sublist in from_nods for item in sublist]

    num_zeros = len(ftt) - len(flat_list2)
    flat_list2.extend([0] * num_zeros)

    ftt['Transactions_amount'] = flat_list1
    ftt['New_nodes'] = flat_list2
    # ftt.drop('new_date',axis = 1, inplace=True)
    name = "preprocessed/" +  path_to_csv.split("/")[1]
    ftt.to_csv(name + '.csv',index=False)