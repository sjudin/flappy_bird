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
        self.bird = Bird(x=100, y=20, dx=0, dy=0, ddx=0, ddy=0.4)

        # Game clock
        self.clock = pygame.time.Clock()
        self.fps = 60

        self.key = {
            pygame.K_SPACE: (0, -6)
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
        self.pipes = [PipePair(100, 3)]

        self.score = 0
        self.font = pygame.font.Font("assets/ARCADE.TTF", 72)

        self.sounds = {
            'jump': pygame.mixer.Sound("assets/jump.wav"),
            'death': pygame.mixer.Sound("assets/death.wav"),
            'score': pygame.mixer.Sound("assets/score.wav"),
        }

    def update_bird(self):
        # Draw background
        self.screen.fill(black)
        self.screen.blit(self.background, (0,0))

        # Move bird and redraw, also update bird rectangle for collision detection
        self.bird.move()
        self.screen.blit(self.bird_image, (round(self.bird.x), round(self.bird.y)))
        temp = self.bird_image.get_rect(x=round(self.bird.x), y=round(self.bird.y))

        # Make bird_rect a bit smaller than the actual bird
        self.bird_rect = pygame.Rect(temp.left + 10, temp.top + 5, temp.width - 10, temp.height - 10)
        # Draw collision box for clearer view
        #pygame.draw.rect(self.screen,black, self.bird_rect)
        

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
            #pygame.draw.rect(self.screen, black, pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height))
            #pygame.draw.rect(self.screen, black, pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height))

            #pygame.draw.rect(self.screen, black, self.pipe_top.get_rect(x=pipe_pair.x, y=pipe_pair.upper.height - 50))
            #pygame.draw.rect(self.screen, black, self.pipe_top.get_rect(x=pipe_pair.x, y=pipe_pair.lower.height))



            

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
        if self.bird.y > self.width:
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


    def run(self):

        counter = 0
        rand = random.randint(150,400)

        # Main game loop
        while 1:
            # Check user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.sounds['jump'].play()
                    self.bird.dx, self.bird.dy = self.key.get(event.key, (self.bird.dx,self.bird.dy))
                
            # Game over
            if self.game_over():
                # Bird falls down to signal game over
                self.sounds['death'].play()
                while self.bird.y < self.height:
                    self.update_bird()
                    for pipe_pair in self.pipes:
                        pipe_pair.lower.dx = 0
                        pipe_pair.upper.dx = 0
                    self.update_pipes()

                    pygame.display.flip()
                    self.clock.tick(self.fps)



                text = self.font.render('Game over, play again? y/n', False, black)
                text_rect = text.get_rect(center=(self.width/2, self.height/2))
                self.screen.blit(text, text_rect)
                
                pygame.display.flip()
                self.clock.tick(self.fps)

                # Wait for player to start again or shut down
                while 1:
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_n:
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_y:
                            self.bird = Bird(x=100, y=20, dx=0, dy=0, ddx=0, ddy=0.4)
                            self.pipes = [PipePair(100, 3)]
                            self.score = 0
                            self.run()
                        else:
                            pass

                    elif event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()


            
            # Continue game loop
            self.update_bird()
            self.update_pipes()
            self.update_score()
            pygame.display.flip()
            self.clock.tick(self.fps)

            # Spawn a new pipe every 80 frames
            if counter == 80:
                rand = random.randint(100,500)
                self.pipes.append(PipePair(rand, 3))
                counter = 0
            

            counter += 1


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
    def __init__(self, centerpos, dx):
        self.x = 1024
        self.upper = Pipe(x = self.x, dx = dx, height = centerpos - 70)
        self.lower = Pipe(x = self.x, dx = dx, height = centerpos + 70)
        self.width = self.upper.width
        

    def move(self):
        self.upper.move()
        self.lower.move()
        self.x -= self.upper.dx


game = FlappyBird()
game.run()