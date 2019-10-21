from Game import FlappyBird

class Environment:
    def __init__(self, graphics_enabled=False, sound_enabled=False, moving_pipes=False):
        self.graphics_enabled = graphics_enabled
        self.sound_enabled = sound_enabled
        self.moving_pipes = moving_pipes

        self.env = FlappyBird(graphics_enabled, sound_enabled, moving_pipes)

    def step(self,action):
        return self.env.step(action)

    def reset(self):
        del self.env
        self.env = FlappyBird(self.graphics_enabled, self.sound_enabled, self.moving_pipes)
        return self.env.state
