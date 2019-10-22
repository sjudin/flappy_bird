import torch
import torch.nn
import itertools
import sys
import numpy as np
import random
from Game import Environment
from collections import namedtuple
from dqn_model import DoubleQLearningModel, ExperienceReplay

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

class Agent:
    def __init__(self, env, pretrained, animate=False):
        # Parameters
        self.num_actions = 2
        self.num_states = 4
        self.num_episodes = 1000
        self.batch_size = 256
        self.gamma = 0.95
        self.learning_rate = 0.1e-5
        self.device = torch.device("cpu")

        self.eps = 0.008
        self.eps_end = 0.001
        self.eps_decay = 0.0001
        self.tau = 1000

        self.curr_episode = None
        self.curr_R_avg = None
        self.curr_R = None
        self.animate = animate


        if animate:
            self.fig = plt.figure()
            self.ax1 = self.fig.add_subplot(1,1,1)
            plt.ion()

        self.buffer_size = 1e+6

        # Replay buffer
        self.replay_buffer = ExperienceReplay(self.device, self.num_states, self.buffer_size)

        # Environment
        self.env = env
        
        # Object holding our online / offline Q-Networks
        self.ddqn = ddqn = DoubleQLearningModel(self.device, self.num_states, self.num_actions, self.learning_rate, pretrained)

        # Data structure for saving transitions
        self.Transition = namedtuple("Transition", ["s", "a", "r", "next_s", "t"])

    def eps_greedy_policy(self, q_values, eps):
        """
        Epsilon greedy policy implementation according to:

        """
        length = len(q_values)
        if eps == 1:
            policy = 1/length*np.ones([length])
        else:
            policy = np.ones(length)*eps/(length-1)
            policy[np.argmax(q_values)] = 1-eps  
            
        return policy

    def calc_q_and_take_action(self, state, eps):
        '''
        Calculate Q-values for current state, and take an action according to an epsilon-greedy policy.
        Inputs:
            ddqn   - DDQN model. An object holding the online / offline Q-networks, and some related methods.
            state  - Current state. Numpy array, shape (1, num_states).
            eps    - Exploration parameter.
        Returns:
            q_online_curr   - Q(s,a) for current state s. Numpy array, shape (1, num_actions) or  (num_actions,).
            curr_action     - Selected action (0 or 1, i.e. left or right), sampled from epsilon-greedy policy. Integer.
        '''

        state = torch.tensor(state, dtype=torch.float)
        q_online_curr = self.ddqn.online_model(state).detach().numpy()
        policy = self.eps_greedy_policy(q_online_curr[0], eps)
        curr_action = np.random.choice([0,1], p=policy)
        
        return q_online_curr, curr_action

    def calculate_q_targets(self, q1_batch, q2_batch, r_batch, nonterminal_batch):
        '''
        Calculates the Q target used for the loss
        : param q1_batch: Batch of Q(s', a) from online network. FloatTensor, shape (N, num actions)
        : param q2_batch: Batch of Q(s', a) from target network. FloatTensor, shape (N, num actions)
        : param r_batch: Batch of rewards. FloatTensor, shape (N,)
        : param nonterminal_batch: Batch of booleans, with False elements if state s' is terminal and True otherwise. BoolTensor, shape (N,)
        : param gamma: Discount factor, float.
        : return: Q target. FloatTensor, shape (N,)
        '''
                
        Y = r_batch + nonterminal_batch.type(torch.FloatTensor)*self.gamma*q2_batch[np.arange(r_batch.shape[0]),torch.argmax(q1_batch, axis=1)]
        
        return Y

    def sample_batch_and_calculate_loss(self):
        # Sample a minibatch of transitions from replay buffer
        curr_state, curr_action, reward, next_state, nonterminal = self.replay_buffer.sample_minibatch(self.batch_size)

        q_online_next = self.ddqn.online_model(next_state)
        q_online_curr = self.ddqn.online_model(curr_state)
        with torch.no_grad():
            q_offline_next = self.ddqn.offline_model(next_state)

        q_target = self.calculate_q_targets(q_online_next, q_offline_next, reward, nonterminal)
        loss = self.ddqn.calc_loss(q_online_curr, q_target, curr_action)

        return loss

    def train_ddqn(self, train=False):
        cnt_updates = 0
        R_buffer = []
        R_avg = []
        eps = self.eps

        if self.animate:
            # self.fig.show()
            pass

        for i in range(self.num_episodes):
            state = np.asarray(self.env.reset()) # Initial state
            state = state[None,:] # Add singleton dimension, to represent as batch of size 1.
            finish_episode = False # Initialize
            ep_reward = 0 # Initialize "Episodic reward", i.e. the total reward for episode, when disregarding discount factor.
            q_buffer = []
            steps = 0

            self.curr_episode = i
            
            while not finish_episode:
                steps += 1

                q_online_curr, curr_action = self.calc_q_and_take_action(state, eps)
                q_buffer.append(q_online_curr)
                new_state, reward, finish_episode = self.env.step(curr_action) # take one step in the evironment
                new_state = np.asarray(new_state)[None,:]
                
                # Store experienced transition to replay buffer
                self.replay_buffer.add(self.Transition(s=state, a=curr_action, r=reward, next_s=new_state, t=not finish_episode))

                state = new_state
                ep_reward += reward
                 
                # If replay buffer contains more than 1000 samples, perform one training step
                if self.replay_buffer.buffer_length > 1000 and train:
                    
                    loss = self.sample_batch_and_calculate_loss()
                    self.ddqn.optimizer.zero_grad()
                    loss.backward()
                    self.ddqn.optimizer.step()

                    cnt_updates += 1
                    if cnt_updates % self.tau == 0:
                        self.ddqn.update_target_network()

            eps = max(eps - self.eps_decay, self.eps_end) # decrease epsilon        
            R_buffer.append(ep_reward)
            
            # Running average of episodic rewards (total reward, disregarding discount factor)
            R_avg.append(.05 * R_buffer[i] + .95 * R_avg[i-1]) if i > 0 else R_avg.append(R_buffer[i])

            print('Episode: {:d}, Total Reward (running avg): {:4.0f} ({:.2f}) Epsilon: {:.3f}, Avg Q: {:.4g}'.format(i, ep_reward, R_avg[-1], eps, np.mean(np.array(q_buffer))))
            self.curr_R_avg = R_avg[-1]
            self.curr_R = ep_reward

            if self.animate:
                self.update_plot()
            
            if train:
                torch.save(self.ddqn.offline_model.state_dict(), "offline_model")
                torch.save(self.ddqn.online_model.state_dict(), "online_model")

        return R_buffer, R_avg

    def update_plot(self):
        with open('agent_plot.csv', mode='a') as file:
            file.write('{}, {}, {}\n'.format(self.curr_episode, self.curr_R_avg, self.curr_R))
        # self.ax1.clear()
        # plot = self.ax1.plot(self.curr_episode, self.curr_R_avg)
        # plot.append(self.ax1.plot(self.curr_episode, self.curr_R, linewidth=1)[0])
        # plot[0].set_label('Average reward')
        # plot[1].set_label('Episodic reward')
        # self.ax1.legend()
        # self.ax1.set_xlabel('Episodes')
        # plt.pause(0.1)

if __name__ == '__main__':
    env = Environment(graphics_enabled=False, sound_enabled=False, moving_pipes=False)

    agent = Agent(env, pretrained=True, animate=True)
    R_avg = 0

    _, R_avg = agent.train_ddqn(train=True)
