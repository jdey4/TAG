#%%
import pickle
import numpy as np
import pandas as pd
# %%
with open('/Users/jayantadey/TAG/data/CUB_200_2011/train_test_split.txt', 'r') as f:
    data = f.read()
# %%
data = data.split('\n')
train = ''
test = ''
i = 0
for id in data:
    if id != '':
        if id[-1] == '0':
            test += id.split(' ')[0] + '\n'
            i += 1
        else:
            train += id.split(' ')[0] + '\n'
# %%
