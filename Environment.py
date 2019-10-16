from Game import FlappyBird

class Environment:
    def __init__(self):
        self.env = FlappyBird()

    def step(self,action):
        return self.env.step(action)

    def reset(self):
        del self.env
        self.env = FlappyBird()
        return self.env.state