import pygame
import sys, os, time
import random 

black = [0, 0, 0]

colors = [[0,0,0], [255, 255, 255], [255, 0, 0], [0, 255, 0], [0, 0, 255], [0, 255, 255], [255, 0, 255], [255, 255, 0]]

class FlappyBird:
    def __init__(self, render_graphics, sound_enabled, moving_pipes):
        self.render_graphics = render_graphics
        self.sound_enabled = sound_enabled
        self.moving_pipes = moving_pipes
        
        if not self.render_graphics:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()

        # screen for game to play on
        self.size = self.width, self.height = 1024, 576
        self.screen = pygame.display.set_mode(self.size)

        # Initial bird
        self.bird = Bird(x=100, y=300, dx=0, dy=0, ddx=0, ddy=1)

        # Game clock
        self.fps = 60

        # Bird and background images
        # if self.render_graphics:
        #     self.background = pygame.image.load("assets/background.png").convert_alpha()
        #     self.bird_image = pygame.transform.scale(pygame.image.load("assets/bird.png"), (55,38)).convert_alpha()

        #     # Pipe images
        #     self.pipe_image_lower = pygame.image.load("assets/pipe_long.png").convert_alpha()
        #     self.pipe_top = pygame.transform.scale(pygame.image.load("assets/pipe_top.png"), (75,50)).convert_alpha()

        #Initial pipe
        self.pipes = []
        self.pipe_rects = []

        pipe_pair = PipePair(300, 3, dy=random.randint(-1,1)) if self.moving_pipes else PipePair(300, 3, dy=0)
        self.pipes.append(pipe_pair)

        # upper_pipe_rect = pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height)
        upper_pipe_rect = pygame.Rect(0, 0, pipe_pair.width, self.height)
        upper_pipe_rect.bottomleft = (pipe_pair.x, pipe_pair.upper.height)

        lower_pipe_rect = pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height)

        # Append corresponding PipePair rects
        self.pipe_rects.append((upper_pipe_rect, lower_pipe_rect))

        self.score = 0
        self.font = pygame.font.Font("assets/ARCADE.TTF", 72)

        if self.sound_enabled:
            pygame.mixer.pre_init(44100, -16, 1, 512)
            self.sounds = {
                'jump': pygame.mixer.Sound("assets/jump.wav"),
                'death': pygame.mixer.Sound("assets/death.wav"),
                'score': pygame.mixer.Sound("assets/score.wav")
            }

        self.counter = 0
        self.state = []

        # Update states
        self.state.extend([self.bird.y, self.bird.dy])

        # Initial set of pipes, (none on screen)
        self.state.append([(pipe.y+pipe.center_offset/2)-(self.bird.y + 30) for pipe in self.pipes if (pipe.x + pipe.width) > self.bird.x][:1][0])
        self.state.append([(pipe.y-pipe.center_offset/2)-(self.bird.y) for pipe in self.pipes if (pipe.x + pipe.width) > self.bird.x][:1][0])

        self.state.append([(pipe.x+pipe.width)-self.bird.x for pipe in self.pipes if (pipe.x+pipe.width) > self.bird.x][:1][0]) # Closest pipe dist to end

    def update_bird(self):

        # Move bird and redraw, also update bird rectangle for collision detection
        self.bird.move()

        if self.render_graphics:
            # self.screen.blit(self.background, (0,0))
            self.screen.fill(black)
            # self.screen.fill(colors[random.randint(0, len(colors)-1)])
            pygame.draw.rect(self.screen, (255, 255, 0), self.bird)
            # pygame.draw.rect(self.screen, colors[random.randint(0, len(colors)-1)], self.bird_rect)

        

    def update_pipes(self):
        for pipe_pair, pipe_pair_rects in zip(self.pipes, self.pipe_rects):
            if pipe_pair.x < -pipe_pair.width:
                self.pipes.remove(pipe_pair)
                self.pipe_rects.remove(pipe_pair_rects)
                continue

            if self.height - pipe_pair.y - pipe_pair.center_offset/2 <= 0 or pipe_pair.y - pipe_pair.center_offset/2 <= 0:
                pipe_pair.upper.dy *= -1

            old_x, old_y = pipe_pair.x, pipe_pair.y
            pipe_pair.move()
            for pipe_pair_rect in pipe_pair_rects:
                pipe_pair_rect.move_ip(pipe_pair.x - old_x, pipe_pair.y - old_y)


            if self.render_graphics:
                # Draw longer part of pipe
                # self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, pipe_pair.upper.height)), \
                #                 (pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height))
                # self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, 500)), (pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height))

                # # # Draw tops of pipes
                # self.screen.blit(self.pipe_top, (pipe_pair.x, pipe_pair.upper.height - 50))
                # self.screen.blit(self.pipe_top, (pipe_pair.x, pipe_pair.lower.height))

                # Draw pipe collision rects for debugging
                for rect in pipe_pair_rects:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect)
                    # pygame.draw.rect(self.screen, colors[random.randint(0, len(colors)-1)], rect)

    def update_score(self):
        for pipe_pair in self.pipes:
            if self.bird.x == pipe_pair.x:
                self.score += 1

                if hasattr(self, 'sounds'):
                    self.sounds['score'].play()

        if self.render_graphics:
            text = self.font.render(str(self.score), False, (0, 255, 0))
            self.screen.blit(text, (self.width/2,50, 100, 200))

    # Keeps track of all conditions for a game over
    def game_over(self):
        # Check if bird falls down
        if self.bird.y > self.width or self.bird.y < 0:
            return True
            
        # Has the birds rectagle collided with any pipes?
        for pipe_rect in self.pipe_rects:
            if self.bird.collidelist(pipe_rect) > -1:
                return True
            
        return False

    def step(self, action):
        # If action is 1, we jump
        if action == 1:
            self.bird.dx, self.bird.dy = (0, -6)

            if hasattr(self, 'sounds'):
                self.sounds['jump'].play()
            
        # Continue game loop
        self.state = []
        self.update_bird()
        self.update_pipes()
        self.update_score()
        pygame.display.flip()

        # Update states
        self.state.extend([self.bird.y, self.bird.dy])
        self.state.append([(pipe.y+pipe.center_offset/2)-(self.bird.y + 30) for pipe in self.pipes if (pipe.x + pipe.width) > self.bird.x][:1][0])
        self.state.append([(pipe.y-pipe.center_offset/2)-(self.bird.y) for pipe in self.pipes if (pipe.x + pipe.width) > self.bird.x][:1][0])

        self.state.append([(pipe.x+pipe.width)-self.bird.x for pipe in self.pipes if (pipe.x+pipe.width) > self.bird.x][:1][0]) # Closest pipe dist to end

        # Game over
        self.terminal_state = self.game_over()
        if self.terminal_state:
            # Bird falls down to signal game over
            # pygame.quit()
            return self.state, 0, True

        # Spawn a new pipe every 100 frames
        if self.counter == 150:
            rand = random.randint(100,450)
            r = random.randint(3,5)
            pipe_pair = PipePair(rand, 3, dy=r) if self.moving_pipes else PipePair(rand, 3, dy=0)
            self.pipes.append(pipe_pair)

            # upper_pipe_rect = pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height)
            upper_pipe_rect = pygame.Rect(0, 0, pipe_pair.width, self.height)
            upper_pipe_rect.bottomleft = (pipe_pair.x, pipe_pair.upper.height)
            lower_pipe_rect = pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height)

            # Append corresponding PipePair rects
            self.pipe_rects.append((upper_pipe_rect, lower_pipe_rect))
            self.counter = 0
        
        self.counter += 1

        # Return current state, reward and terminal_state
        return self.state, 1, False


# Keeps track of bird positions
class Bird(pygame.Rect):
    def __init__(self, x, y, dx, dy, ddx, ddy):
        super().__init__(x, y, 50, 30)
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        self.ddx = ddx
        self.ddy = ddy

        # We need this to prevent the rect from drifting over time
        self.counter = 0

    def move(self):
        old_x, old_y = (self.x, self.y)

        self.x += self.dx
        self.y += self.dy
        self.dx += self.ddx
        self.dy += self.ddy
        
        if self.counter > 100:
            super().__init__(self.x, self.y, 50, 30)
            self.counter = 0
        else:
            self.move_ip(self.x - old_x, self.y - old_y)

        self.counter += 1

# Keeps track of pipe position
class Pipe:
    def __init__(self, x, dx, height, width=90, y=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height

    def move(self):
        self.x -= self.dx
        self.y += self.dy

class PipePair:
    def __init__(self, centerpos, dx, dy=0, x=None):
        self.center_offset = 200
        self.x = 1024 if x is None else x
        self.y = centerpos
        self.upper = Pipe(x = self.x, dx = dx, height = centerpos - self.center_offset/2, dy=dy)
        self.lower = Pipe(x = self.x, dx = dx, height = centerpos + self.center_offset/2, dy=dy)
        self.width = self.upper.width

    def move(self):
        self.upper.move()
        self.lower.move()
        self.x -= self.upper.dx
        self.y += self.upper.dy


class Environment:
    """
    Simple wrapper environment that a RL agent uses to interact with the flappy bird game.
    inputs:
        graphics_enabled: Tells the environment if you want to open a window to show the agent playing
        sound_enabled: Want sound?
        moving_pipes: with this enabled, the pipes will move up and down to increase difficulty
    """

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
