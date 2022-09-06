#%%
import pickle
import numpy as np
import pandas as pd
# %%
with open('/Users/jayantadey/TAG/results/five_dataset/agem.pickle', 'rb') as f:
    res = pickle.load(f)

# %%
total_tasks = 20
algo = 'tag'
# %%
df = pd.DataFrame()
df_single_task = pd.DataFrame()
shifts = []
tasks = []
base_tasks = []
accuracies_across_tasks = []
shifts_single = []
tasks_single = []
accuracy_single = []

multitask_file = 'results/mini_imagenet/'+algo+'.pickle'
singletask_file = 'results/mini_imagenet/'+algo+'_'+'single_task.pickle'

with open(multitask_file, 'rb') as f:
    res_multi = pickle.load(f)

with open(singletask_file, 'rb') as f:
    res_single = pickle.load(f)


for ii in range(5):
    tasks_single.append(ii+1)
    accuracy_single.append(res_single[ii]/100)
    for jj in range(ii+1):
        tasks.append(jj+1)
        base_tasks.append(ii+1)
        accuracies_across_tasks.append(res_multi[jj+1][ii]/100)

df['task'] = tasks
df['base_task'] = base_tasks
df['accuracy'] = accuracies_across_tasks

df_single_task = pd.DataFrame()
df_single_task['task'] = tasks_single
df_single_task['accuracy'] = accuracy_single

summary = (df,df_single_task)
file_to_save = 'converted_files/mini_imagenet/'+algo+'.pickle'
with open(file_to_save, 'wb') as f:
    pickle.dump(summary, f)
# %%
