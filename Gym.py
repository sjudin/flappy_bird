from Game import FlappyBird

class Environment:
    def __init__(self):
        self.env = FlappyBird()

    def step(self, action):
        return self.env.step(action)
    
    def reset(self):
        del self.env
        self.env = FlappyBird()
        return self.env.state

def eps_greedy_policy(q_values, eps):
    '''
    Creates an epsilon-greedy policy
    :param q_values: set of Q-values of shape (num actions,)
    :param eps: probability of taking a uniform random action 
    :return: policy of shape (num actions,)
    '''
    policy = np.zeros(q_values.shape[0],)
    
    i = np.argwhere(q_values == np.max(q_values))
    
    policy[i] = eps/q_values.shape[0] + (1 - eps)/i.shape[0]
    policy[policy==0] = eps/q_values.shape[0]
        
    return policy
