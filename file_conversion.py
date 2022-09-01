#%%
import pickle
import numpy as np
import pandas as pd
# %%
with open('/Users/jayantadey/TAG/converted_file/er-1-1.pickle','rb') as f:
    res = pickle.load(f)
# %%
total_tasks = 10
data_fold = 6
slot_fold = 10
algo = 'er'
# %%
for fold in range(data_fold):
    for slot in range(slot_fold):
        df = pd.DataFrame()
        df_single_task = pd.DataFrame()
        shifts = []
        tasks = []
        base_tasks = []
        accuracies_across_tasks = []
        shifts_single = []
        tasks_single = []
        accuracy_single = []

        multitask_file = 'results/'+algo+'_'+str(slot+1)+'_'+str(fold+1)+'.pickle'
        with open(multitask_file, 'rb') as f:
            res_multi = pickle.load(f)


        for ii in range(10):
            tasks.append(ii+1)
            shifts.append(fold)
            accuracies_across_tasks.append(res_multi[1][ii]/100)

        df['data_fold'] = shifts
        df['task'] = tasks
        df['task_1_accuracy'] = accuracies_across_tasks

        summary = df
        file_to_save = 'converted_file/'+algo+'-'+str(slot+1)+'-'+str(fold+1)+'.pickle'
        with open(file_to_save, 'wb') as f:
            pickle.dump(summary, f)
# %% load 5000 sample files
algo = 'tag'
for fold in range(data_fold):
    df = pd.DataFrame()
    df_single_task = pd.DataFrame()
    shifts = []
    tasks = []
    base_tasks = []
    accuracies_across_tasks = []
    

    multitask_file = 'results/'+algo+'_'+str(fold+1)+'.pickle'

    with open(multitask_file, 'rb') as f:
        res_multi = pickle.load(f)



    for ii in range(10):
        tasks.append(ii+1)
        shifts.append(fold)
        accuracies_across_tasks.append(res_multi[1][ii]/100)

    df['data_fold'] = shifts
    df['task'] = tasks
    df['task_1_accuracy'] = accuracies_across_tasks


    summary = df
    file_to_save = 'converted_file/'+algo+'-'+str(fold+1)+'.pickle'
    with open(file_to_save, 'wb') as f:
        pickle.dump(summary, f)

# %%
