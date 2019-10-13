import sys, pygame, time, random
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()


black = [0, 0, 0]
class FlappyBird:
    def __init__(self):

        # screen for game to play on
        self.size = self.width, self.height = 1024, 576
        self.screen = pygame.display.set_mode(self.size)

        # Initial bird
        self.bird = Bird(x=100, y=100, dx=0, dy=0, ddx=0, ddy=0.4)

        # Game clock
        self.fps = 60

        self.key = {
            pygame.K_SPACE: (0, -6),
            # pygame.K_b: (-3, -6)
        }

        # Background image
        self.background = pygame.image.load("assets/background.png").convert_alpha()
        
        # Bird image
        self.bird_image = pygame.transform.scale(pygame.image.load("assets/bird.png"), (55,38)).convert_alpha()
        self.bird_rect = self.bird_image.get_rect(x=self.bird.x, y=self.bird.y)

        # Pipe images
        self.pipe_image_lower = pygame.image.load("assets/pipe_long.png").convert_alpha()
        self.pipe_top = pygame.transform.scale(pygame.image.load("assets/pipe_top.png"), (75,50)).convert_alpha()

        #Initial pipe
        self.pipes = []

        self.score = 0
        self.font = pygame.font.Font("assets/ARCADE.TTF", 72)

        self.sounds = {
            'jump': pygame.mixer.Sound("assets/jump.wav"),
            'death': pygame.mixer.Sound("assets/death.wav"),
            # 'score': pygame.mixer.Sound("assets/RIP.wav"),
            'score': pygame.mixer.Sound("assets/score.wav")
        }

        self.counter = 0

        self.terminal_state = False
        self.state = []

    def update_bird(self):
        # Draw background
        self.screen.fill(black)
        self.screen.blit(self.background, (0,0))

        # Move bird and redraw, also update bird rectangle for collision detection
        self.bird.move()
        self.screen.blit(self.bird_image, (round(self.bird.x), round(self.bird.y)))
        temp = self.bird_image.get_rect(x=round(self.bird.x), y=round(self.bird.y))

        # print('x: ', [pipe.x-self.bird.x for pipe in self.pipes if pipe.x > self.bird.x][:2])
        # print('y: ', [pipe.lower.height-self.bird.y for pipe in self.pipes if pipe.x > self.bird.x][:2])

        # Make bird_rect a bit smaller than the actual bird
        self.bird_rect = pygame.Rect(temp.left + 10, temp.top + 5, temp.width - 10, temp.height - 10)
        # Draw collision box for clearer view
        # pygame.draw.rect(self.screen,black, self.bird_rect)
        

    def update_pipes(self):
        for pipe_pair in self.pipes:
            pipe_pair.move()

            # Draw longer part of pipe
            self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, pipe_pair.upper.height)), (pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height))
            self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, 500)), (pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height))

            # Draw tops of pipes
            self.screen.blit(self.pipe_top, (pipe_pair.x, pipe_pair.upper.height - 50))
            self.screen.blit(self.pipe_top, (pipe_pair.x, pipe_pair.lower.height))

            # Draw collision rectangles for pipes
            # pygame.draw.rect(self.screen, black, pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height))
            # pygame.draw.rect(self.screen, black, pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height))

            # pygame.draw.rect(self.screen, black, self.pipe_top.get_rect(x=pipe_pair.x, y=pipe_pair.upper.height - 50))
            # pygame.draw.rect(self.screen, black, self.pipe_top.get_rect(x=pipe_pair.x, y=pipe_pair.lower.height))

    def update_score(self):
        for pipe_pair in self.pipes:
            if self.bird.x == pipe_pair.x:
                self.score += 1
                self.sounds['score'].play()

        text = self.font.render(str(self.score), False, black)
        self.screen.blit(text, (self.width/2,50, 100, 200))

    # Keeps track of all conditions for a game over
    def game_over(self):
        # Check if bird falls down
        if self.bird.y > self.width or self.bird.y < 0:
            return True

        # Check collision with pipe
        for pipe_pair in self.pipes:
            upper_top = pygame.Rect(self.pipe_top.get_rect(x=pipe_pair.x, y=pipe_pair.upper.height - 50))
            lower_top = pygame.Rect(self.pipe_top.get_rect(x=pipe_pair.x, y=pipe_pair.lower.height))
            upper_pipe = pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height)
            lower_pipe = pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height)

            l = [upper_top, lower_top, upper_pipe, lower_pipe]
            
            # Has the birds rectagle collided with any pipes?
            if self.bird_rect.collidelist(l) > -1:
                return True
            
        else:
            return False


    def step(self, action):

        rand = random.randint(150,400)

        # If action is 1, we jump
        if action == 1:
            self.sounds['jump'].play()
            self.bird.dx, self.bird.dy = self.key.get(pygame.K_SPACE, (self.bird.dx,self.bird.dy))
            
        
        # Continue game loop
        self.state = []
        self.update_bird()
        self.update_pipes()
        self.update_score()
        pygame.display.flip()

        # Update states
        self.state.append([self.bird.x, self.bird.y])
        self.state.append([pipe.x-self.bird.x for pipe in self.pipes if pipe.x > self.bird.x][:2])
        self.state.append([pipe.lower.height-self.bird.y for pipe in self.pipes if pipe.x > self.bird.x][:2])

        # Game over
        self.terminal_state = self.game_over()
        if self.terminal_state:
            # Bird falls down to signal game over
            pygame.quit()
            return self.state, -1, True

        # Spawn a new pipe every 80 frames
        if self.counter == 100:
            rand = random.randint(100,500)
            self.pipes.append(PipePair(rand, 3, dy=1))
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
        # y coordinates do not matter
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
        # self.x = 1024
        self.y = 0
        self.upper = Pipe(x = self.x, dx = dx, height = centerpos - 70, dy=dy)
        self.lower = Pipe(x = self.x, dx = dx, height = centerpos + 70, dy=dy)
        self.width = self.upper.width
        

    def move(self):
        self.upper.move()
        self.lower.move()
        self.x -= self.upper.dx
        


if __name__ == '__main__':
    game = FlappyBird()
    import itertools
    for i in itertools.count():
        k = game.step(1) if i%32==0 else game.step(0)
        if k[2]:
            print(k)
            sys.exit()
        else:
            print(k)

