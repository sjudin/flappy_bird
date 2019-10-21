import torch
import torch.nn
import itertools
import sys
import numpy as np
import random
from Environment import Environment
from collections import namedtuple
from dqn_model import DoubleQLearningModel, ExperienceReplay

device = torch.device("cpu")

def eps_greedy_policy(q_values, eps):
    '''
    Creates an epsilon-greedy policy
    :param q_values: set of Q-values of shape (num actions,)
    :param eps: probability of taking a uniform random action 
    :return: policy of shape (num actions,)
    '''
    # YOUR CODE HERE
    length = len(q_values)
    if eps == 1:
        policy = 1/length*np.ones([length])
    else:
        policy = np.ones(length)*eps/(length-1)
        policy[np.argmax(q_values)] = 1-eps  
        
    return policy

def calc_q_and_take_action(ddqn, state, eps):
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
    # FYI:
    # ddqn.online_model & ddqn.offline_model are Pytorch modules for online / offline Q-networks, which take the state as input, and output the Q-values for all actions.
    # Input shape (batch_size, num_states). Output shape (batch_size, num_actions).

    state = torch.tensor(state, dtype=torch.float)
    q_online_curr = ddqn.online_model(state).detach().numpy()
    policy = eps_greedy_policy(q_online_curr[0], eps)
    curr_action = np.random.choice([0,1], p=policy)
    
    return q_online_curr, curr_action

def calculate_q_targets(q1_batch, q2_batch, r_batch, nonterminal_batch, gamma=.99):
    '''
    Calculates the Q target used for the loss
    : param q1_batch: Batch of Q(s', a) from online network. FloatTensor, shape (N, num actions)
    : param q2_batch: Batch of Q(s', a) from target network. FloatTensor, shape (N, num actions)
    : param r_batch: Batch of rewards. FloatTensor, shape (N,)
    : param nonterminal_batch: Batch of booleans, with False elements if state s' is terminal and True otherwise. BoolTensor, shape (N,)
    : param gamma: Discount factor, float.
    : return: Q target. FloatTensor, shape (N,)
    '''
            
    Y = r_batch + nonterminal_batch.type(torch.FloatTensor)*gamma*q2_batch[np.arange(r_batch.shape[0]),torch.argmax(q1_batch, axis=1)]
    
    return Y

def sample_batch_and_calculate_loss(ddqn, replay_buffer, batch_size, gamma):
    '''
    Sample mini-batch from replay buffer, and compute the mini-batch loss
    Inputs:
        ddqn          - DDQN model. An object holding the online / offline Q-networks, and some related methods.
        replay_buffer - Replay buffer object (from which smaples will be drawn)
        batch_size    - Batch size
        gamma         - Discount factor
    Returns:
        Mini-batch loss, on which .backward() will be called to compute gradient.
    '''
    # Sample a minibatch of transitions from replay buffer
    curr_state, curr_action, reward, next_state, nonterminal = replay_buffer.sample_minibatch(batch_size)

    # FYI:
    # ddqn.online_model & ddqn.offline_model are Pytorch modules for online / offline Q-networks, which take the state as input, and output the Q-values for all actions.
    # Input shape (batch_size, num_states). Output shape (batch_size, num_actions).

    q_online_next = ddqn.online_model(next_state)
    q_online_curr = ddqn.online_model(curr_state)
    with torch.no_grad():
        q_offline_next = ddqn.offline_model(next_state)

    q_target = calculate_q_targets(q_online_next, q_offline_next, reward, nonterminal, gamma=gamma)
    loss = ddqn.calc_loss(q_online_curr, q_target, curr_action)

    return loss

def train_loop_ddqn(ddqn, env, replay_buffer, num_episodes, enable_visualization=False, batch_size=64, gamma=.94):        
    Transition = namedtuple("Transition", ["s", "a", "r", "next_s", "t"])
    eps = 0.00
    eps_end = 0.00
    eps_decay = 0
    tau = 5000
    cnt_updates = 0
    R_buffer = []
    R_avg = []
    for i in range(num_episodes):
        state = np.asarray(env.reset()) # Initial state
        state = state[None,:] # Add singleton dimension, to represent as batch of size 1.
        finish_episode = False # Initialize
        ep_reward = 0 # Initialize "Episodic reward", i.e. the total reward for episode, when disregarding discount factor.
        q_buffer = []
        steps = 0
        
        while not finish_episode:
            steps += 1

            # Take one step in environment. No need to compute gradients,
            # we will just store transition to replay buffer, and later sample a whole batch
            # from the replay buffer to actually take a gradient step.
            q_online_curr, curr_action = calc_q_and_take_action(ddqn, state, eps)
            q_buffer.append(q_online_curr)
            new_state, reward, finish_episode = env.step(curr_action) # take one step in the evironment
            new_state = np.asarray(new_state)[None,:]
            
            # Assess whether terminal state was reached.
            nonterminal_to_buffer = not finish_episode
            
            # Store experienced transition to replay buffer
            replay_buffer.add(Transition(s=state, a=curr_action, r=reward, next_s=new_state, t=nonterminal_to_buffer))

            state = new_state
            ep_reward += reward
             
            # If replay buffer contains more than 1000 samples, perform one training step
            # if replay_buffer.buffer_length > 1000:
            #     
            #     loss = sample_batch_and_calculate_loss(ddqn, replay_buffer, batch_size, gamma)
            #     ddqn.optimizer.zero_grad()
            #     loss.backward()
            #     ddqn.optimizer.step()

            #     cnt_updates += 1
            #     if cnt_updates % tau == 0:
            #         print("updated target")
            #         ddqn.update_target_network()
                

        eps = max(eps - eps_decay, eps_end) # decrease epsilon        
        R_buffer.append(ep_reward)
        
        # Running average of episodic rewards (total reward, disregarding discount factor)
        R_avg.append(.05 * R_buffer[i] + .95 * R_avg[i-1]) if i > 0 else R_avg.append(R_buffer[i])

        print('Episode: {:d}, Total Reward (running avg): {:4.0f} ({:.2f}) Epsilon: {:.3f}, Avg Q: {:.4g}'.format(i, ep_reward, R_avg[-1], eps, np.mean(np.array(q_buffer))))
        
        torch.save(ddqn.offline_model.state_dict(), "offline_model")
        torch.save(ddqn.online_model.state_dict(), "online_model")

    return R_buffer, R_avg


# Initializations
num_actions = 2
num_states = 4
num_episodes = 500
batch_size = 256
gamma = 0.95
learning_rate = 0.1e-5

env = Environment(graphics_enabled=True, sound_enabled=False, moving_pipes=True)
# Object holding our online / offline Q-Networks
ddqn = DoubleQLearningModel(device, num_states, num_actions, learning_rate,
        pretrained=True)

# Create replay buffer, where experience in form of tuples <s,a,r,s',t>, gathered from the environment is stored 
# for training
replay_buffer = ExperienceReplay(device, num_states, 1e+6)

# Train
R, R_avg = train_loop_ddqn(ddqn, env, replay_buffer, num_episodes, [], batch_size=batch_size, gamma=gamma)
