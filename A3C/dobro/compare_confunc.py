import matplotlib.pyplot as plt
from matplotlib import rc
from copy import deepcopy
import numpy as np
import pickle
import glob
import sys
import os

font = {'size'   : 14}
rc('font', **font)

#env_name = 'MountainCarContinuous'
#env_name = 'Pendulum'
#env_name = 'CartPole'
#env_name = 'DobroHalfCheetah'
env_name = "Safexp_PointGoal1"
#item_name = 'score'
item_name = 'cost'
#item_name = 'loss'
moving_period = 1000

def smoothing(steps, records):
    iters = []
    smooth = []
    for i in range(len(records)):
        if i==0:
            iters.append(steps[i])
        else:   
            iters.append(iters[i-1]+steps[i])
    for i in range(moving_period, len(records)+1):
        a = np.mean(records[i-moving_period:i])
        smooth.append(a)
    iters = iters[moving_period-1:]
    return iters, smooth

dir_names = ['{}/{}_log'.format(env_name, item_name)]

records = []
for dir_name in dir_names:
    record_names = glob.glob('./{}/*.pkl'.format(dir_name))
    record_names.sort()
    [print(record_name) for record_name in record_names]
    print('-'*10)
    temp_records = [] #log갯수 * 총step * 2(각step수, score)
    for record_name in record_names:
        with open(record_name, 'rb') as f:
            #temp_records.append(pickle.load(f))
            temp_records += pickle.load(f)
    #records.append(temp_records) #폴더수 * log갯수 * 총step * 2(각step수, score)
    records.append([temp_records]) #폴더수 * log갯수 * 총step * 2(각step수, score)

steps = []
rewards = []
for i in range(len(dir_names)):
    temp_steps = []
    temp_rewards = []
    temp_records = records[i] #log갯수 * 총step * 2(각step수, score)
    for j in range(len(temp_records)):
        temp_steps.append([record[0] for record in temp_records[j]])
        reward = [record[1] for record in temp_records[j]]
        temp_rewards.append(np.array(reward))
    steps.append(temp_steps)
    rewards.append(temp_rewards)

iters = []
for i in range(len(dir_names)):
    temp_iters = []
    temp_steps = steps[i]
    temp_rewards = rewards[i]
    for j in range(len(temp_steps)):
        temp_iter, temp_reward = smoothing(temp_steps[j], temp_rewards[j])
        temp_iters.append(temp_iter)
        temp_rewards[j] = temp_reward
    iters.append(temp_iters)

start = 0
end = int(1e10)
for i in range(len(dir_names)):
    temp_start = max([item[0] for item in iters[i]])
    temp_end = min([item[-1] for item in iters[i]])
    start = max(start, temp_start)
    end = min(end, temp_end)
lin_space = np.linspace(start, end, 100000)

stds = []
for i in range(len(dir_names)):
    temp_iters = iters[i]
    temp_rewards = rewards[i]
    for j in range(len(temp_iters)):
        temp_rewards[j] = np.interp(lin_space, temp_iters[j], temp_rewards[j])
    stds.append(np.std(temp_rewards, axis=0))
    rewards[i] = np.mean(temp_rewards, axis=0)

fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
for i in range(len(dir_names)):
    temp_rewards = rewards[i]
    temp_stds = stds[i]
    ax1.plot(lin_space, temp_rewards, lw=2)
    ax1.fill_between(lin_space, temp_rewards-temp_stds, temp_rewards+temp_stds, alpha=0.3)
ax1.set_title('{}\n{}'.format(env_name, item_name))
ax1.set_xlabel('Steps')
ax1.set_ylabel(item_name)
ax1.grid()

fig.tight_layout()
plt.savefig('{}_{}.png'.format(env_name, item_name))
plt.show()
