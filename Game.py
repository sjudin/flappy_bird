import pygame
import sys, os, time
import random 

pygame.mixer.pre_init(44100, -16, 1, 512)
black = [0, 0, 0]

class FlappyBird:
    def __init__(self):
        self.render_graphics = False
        
        if not self.render_graphics:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()

        # screen for game to play on
        self.size = self.width, self.height = 1024, 576
        self.screen = pygame.display.set_mode(self.size)

        # Initial bird
        self.bird = Bird(x=100, y=100, dx=0, dy=0, ddx=0, ddy=0.4)

        # Game clock
        self.fps = 60

        # Bird rectangle for collision detection
        self.bird_rect = pygame.Rect(self.bird.x, self.bird.y, 50, 30)

        # Bird and background images
        if self.render_graphics:
            self.background = pygame.image.load("assets/background.png").convert_alpha()
            self.bird_image = pygame.transform.scale(pygame.image.load("assets/bird.png"), (55,38)).convert_alpha()

            # Pipe images
            self.pipe_image_lower = pygame.image.load("assets/pipe_long.png").convert_alpha()
            self.pipe_top = pygame.transform.scale(pygame.image.load("assets/pipe_top.png"), (75,50)).convert_alpha()

        #Initial pipe
        self.pipes = []
        self.pipe_rects = []

        pipe_pair = PipePair(random.randint(100,500), 3, dy=1)
        self.pipes.append(pipe_pair)

        upper_pipe_rect = pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height)
        lower_pipe_rect = pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height)

        # Append corresponding PipePair rects
        self.pipe_rects.append((upper_pipe_rect, lower_pipe_rect))

        self.score = 0
        self.font = pygame.font.Font("assets/ARCADE.TTF", 72)

        self.sounds = {
            'jump': pygame.mixer.Sound("assets/jump.wav"),
            'death': pygame.mixer.Sound("assets/death.wav"),
            'score': pygame.mixer.Sound("assets/score.wav")
        }

        self.counter = 0

        self.terminal_state = False
        self.state = []

        # Update states
        self.state.append([self.bird.x, self.bird.y, self.bird.dx, self.bird.dy])

        # Initial set of pipes, (none on screen)
        self.state.append([pipe.x-self.bird.x for pipe in self.pipes if pipe.x > self.bird.x][:1][0])
        self.state.append([pipe.lower.height-self.bird.y for pipe in self.pipes if pipe.x > self.bird.x][:1][0])

    def update_bird(self):
        # Draw background
        if self.render_graphics:
            self.screen.fill(black)
            self.screen.blit(self.background, (0,0))

        # Move bird and redraw, also update bird rectangle for collision detection
        old_x, old_y = self.bird.x, self.bird.y
        self.bird.move()

        if self.render_graphics:
            self.screen.blit(self.bird_image, (round(self.bird.x), round(self.bird.y)))

        self.bird_rect.move_ip(self.bird.x - old_x, self.bird.y - old_y)

        # Draw bird collision box for debugging
        # pygame.draw.rect(self.screen,black, self.bird_rect)
        

    def update_pipes(self):
        for pipe_pair, pipe_pair_rects in zip(self.pipes, self.pipe_rects):
            if pipe_pair.x < -75:
                self.pipes.remove(pipe_pair)
                self.pipe_rects.remove(pipe_pair_rects)
                continue

            old_x, old_y = pipe_pair.x, pipe_pair.y
            pipe_pair.move()
            for pipe_pair_rect in pipe_pair_rects:
                pipe_pair_rect.move_ip(pipe_pair.x - old_x, pipe_pair.y - old_y)

            if self.render_graphics:
                # Draw longer part of pipe
                self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, pipe_pair.upper.height)), \
                                (pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height))
                self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, 500)), (pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height))

                # # Draw tops of pipes
                self.screen.blit(self.pipe_top, (pipe_pair.x, pipe_pair.upper.height - 50))
                self.screen.blit(self.pipe_top, (pipe_pair.x, pipe_pair.lower.height))

                # Draw pipe collision rects for debugging
                # for rect in pipe_pair_rects:
                #     pygame.draw.rect(self.screen, black, rect)

    def update_score(self):
        for pipe_pair in self.pipes:
            if self.bird.x == pipe_pair.x:
                self.score += 1
                self.sounds['score'].play()

        if self.render_graphics:
            text = self.font.render(str(self.score), False, black)
            self.screen.blit(text, (self.width/2,50, 100, 200))

    # Keeps track of all conditions for a game over
    def game_over(self):
        # Check if bird falls down
        if self.bird.y > self.width or self.bird.y < 0:
            return True
            
        # Has the birds rectagle collided with any pipes?
        for pipe_rect in self.pipe_rects:
            if self.bird_rect.collidelist(pipe_rect) > -1:
                return True
            
        return False

    def step(self, action):
        rand = random.randint(150,400)

        # If action is 1, we jump
        if action == 1:
            if self.render_graphics:
                self.sounds['jump'].play()
            self.bird.dx, self.bird.dy = (0, -6)
            
        # Continue game loop
        self.state = []
        self.update_bird()
        self.update_pipes()
        self.update_score()
        pygame.display.flip()

        # Update states
        self.state.append([self.bird.x, self.bird.y, self.bird.dx, self.bird.dy])
        self.state.append([pipe.x-self.bird.x for pipe in self.pipes if pipe.x > self.bird.x][:1][0])
        self.state.append([pipe.lower.height-self.bird.y for pipe in self.pipes if pipe.x > self.bird.x][:1][0])

        # Game over
        self.terminal_state = self.game_over()
        if self.terminal_state:
            # Bird falls down to signal game over
            pygame.quit()
            return self.state, -1, True

        # Spawn a new pipe every 100 frames
        if self.counter == 100:
            rand = random.randint(100,500)
            pipe_pair = PipePair(rand, 3, dy=1)
            self.pipes.append(pipe_pair)

            upper_pipe_rect = pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height)
            lower_pipe_rect = pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height)

            # Append corresponding PipePair rects
            self.pipe_rects.append((upper_pipe_rect, lower_pipe_rect))
            self.counter = 0
        
        self.counter += 1

        # Return current state, reward and terminal_state
        return self.state, 0, False


# Keeps track of bird positions
class Bird:
    def __init__(self,x,y,dx,dy, ddx, ddy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        self.ddx = ddx
        self.ddy = ddy

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.dx += self.ddx
        self.dy += self.ddy

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
        self.x = 1024 if x is None else x
        self.y = 0
        self.upper = Pipe(x = self.x, dx = dx, height = centerpos - 70, dy=dy)
        self.lower = Pipe(x = self.x, dx = dx, height = centerpos + 70, dy=dy)
        self.width = self.upper.width

    def move(self):
        self.upper.move()
        self.lower.move()
        self.x -= self.upper.dx


if __name__ == '__main__':
    import itertools
    for episode in range(10):
        print("Episode: {}".format(episode))
        game = FlappyBird()
        t = time.time()

        for i in itertools.count():
            k = game.step(1) if i%32==0 else game.step(0)
            if k[2]:
                print(k)
                print(time.time()-t)
                del game
                break
