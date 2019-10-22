import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import argparse

style.use('fivethirtyeight')


parser = argparse.ArgumentParser(description='Plot training data samples for RL algorithm')
parser.add_argument(action='store', dest='file_name')
args = parser.parse_args()

with open(args.file_name, 'r') as file:
    avg_R = []
    curr_R = []
    episodes = []
    i = 0
    for line in file:
        episodes.append(i)
        i += 1

        _, a_R, R = line.replace(' ', '').split(',')
        avg_R.append(float(a_R))
        curr_R.append(float(R))

fig, ax = plt.subplots()

ax.plot(episodes, avg_R)
ax.plot(episodes, curr_R, linewidth=1)
ax.legend(['Average reward', 'Episodic reward'], prop={'size': 30})
ax.set_xlabel('Episodes')
ax.set_ylabel('Reward')

plt.show()


