#%%
import pickle
import numpy as np
#%%
algo = 'agem'
shifts = 6
#%%
for degree in range(0,182,4):
    res = np.zeros(2, dtype=float)
    file_to_save = 'converted_files/'+algo+'-'+str(degree)+'.pickle'

    for shift in range(shifts):
        file_to_load = 'results/'+algo+'_'+str(degree)+'_'+str(shift+1)+'.pickle'

        with open(file_to_load, 'rb') as f:
            tmp = np.array(pickle.load(f)[1])
        res += 1 - tmp/100
    res /= shifts

    with open(file_to_save, 'wb') as f:
        pickle.dump(res, f)

# %%
