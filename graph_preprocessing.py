import numpy as np
import pandas as pd
from tqdm import tqdm
import glob
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import os
from pathlib import Path


ftt = pd.read_csv('FTTBTC-1h-data.csv')
all_files = glob.glob(path + "/*.csv")
ftt['timestamp'] = pd.to_datetime(ftt.timestamp)
start_time = ftt.iloc[0]['timestamp']

li = []

for filename in all_files:
    df = pd.read_csv(filename,index_col=None,header=0)
    li.append(df)

frame = pd.concat(li,axis=0,ignore_index=True)
frame.drop_duplicates(subset=['timestamp','token_qty_values','tx_address',
                              'from_address','to_address'],keep=False,inplace=True)
frame.drop(['Unnamed: 0'],axis=1,inplace=True)
frame.sort_values(by=['timestamp'],inplace=True)
frame.reset_index(drop=True,inplace=True)
frame.dropna(axis=0,inplace=True)
frame.reset_index(drop=True,inplace=True)

# start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
end_time = ftt.iloc[-1]['timestamp']
# end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
new_end_time = frame.iloc[-1]['timestamp']
new_end_time = str(new_end_time)
new_end_time = datetime.strptime(new_end_time,'%Y-%m-%d %H:%M:%S')
frame['timestamp'] = pd.to_datetime(frame['timestamp'])
frame = frame[frame['timestamp'] >= start_time]
frame = frame[frame['timestamp'] <= end_time]
ftt = ftt[ftt['timestamp'] <= new_end_time]
frame.reset_index(drop=True,inplace=True)

frame['timestamp'] = frame['timestamp'] - timedelta(hours=3)

frame['new_date'] = [d.date() for d in frame['timestamp']]
frame['new_time'] = [d.time() for d in frame['timestamp']]

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
for k,i in tqdm(zip(my_keys,range(n))):
    # print('current date',k)
    for j in range((k - previous_key).days - 1):
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
    for key,indexes in hour_groups.groups.items():
        from_nod = 0
        for index in indexes:
            a = Node(day_group['from_address'][index])
            if (g.add_node(a) == True) or (day_group['from_address'][index] not in day_group['from_address'][0:index]):
                from_nod += 1

            a = Node(day_group['to_address'][index])
            g.add_node(a)
            for fromm,tooo,value in zip(day_group['from_address'],day_group['to_address'],
                                        day_group['token_qty_values']):
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
flat_list1

num_zeros = len(ftt) - len(flat_list1)
flat_list1.extend([0] * num_zeros)

flat_list2 = [item for sublist in from_nods for item in sublist]
flat_list2

num_zeros = len(ftt) - len(flat_list2)
flat_list2.extend([0] * num_zeros)

ftt['Transactions_amount'] = flat_list1
ftt['New_nodes'] = flat_list2
# ftt.drop('new_date',axis = 1, inplace=True)
name = os.path.basename(price_file[0])
ftt.to_csv(r'/Users/lisaperchenko/Machine learning/Project/' + name + '.csv',index=False)

plt.figure(figsize=(15,10))
plt.subplot(2,2,1)
plt.plot(flat_list1)
plt.subplot(2,2,2)
plt.plot(flat_list2)
plt.subplot(2,2,3)
plt.plot(ftt['low'])
plt.show