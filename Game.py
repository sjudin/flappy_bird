import sys, pygame, time, random
pygame.init()


black = [0, 0, 0]
class FlappyBird:
    def __init__(self):

        # screen for game to play on
        self.size = self.width, self.height = 1024, 576
        self.screen = pygame.display.set_mode(self.size)

        # Initial bird
        self.bird = Bird(x=100, y=20, dx=0, dy=0, ddx=0, ddy=0.3)

        # Game clock
        self.clock = pygame.time.Clock()
        self.fps = 90

        self.key = {
            pygame.K_SPACE: (0, -5)
        }

        # Background image
        self.background = pygame.image.load("assets/background.png")
        # Bird image
        self.bird_image = pygame.transform.scale(pygame.image.load("assets/bird.png"), (50,50))
        # Game over image
        self.game_over_image = pygame.image.load("assets/game_over.png")

        self.pipe_image_lower = pygame.image.load("assets/pipe.png")
        self.pipe_image_upper = pygame.transform.flip(pygame.image.load("assets/pipe.png"), False, True)

        self.pipes = [PipePair(100, 3)]

        self.score = 0
        self.font = pygame.font.Font("assets/ARCADE.TTF", 72)

    def update_bird(self):
        # Draw background
        self.screen.fill(black)
        self.screen.blit(self.background, (0,0))

        # Move bird and redraw
        self.bird.move()
        self.screen.blit(self.bird_image, (round(self.bird.x), round(self.bird.y)))

    def update_pipes(self):
        for pipe_pair in self.pipes:
            pipe_pair.move()

            self.screen.blit(pygame.transform.scale(self.pipe_image_upper, (75, pipe_pair.upper.height)), (pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height))
            self.screen.blit(pygame.transform.scale(self.pipe_image_lower, (75, 500)), (pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height))

    def update_score(self):
        for pipe_pair in self.pipes:
            if self.bird.x == pipe_pair.x:
                self.score += 1

        text = self.font.render(str(self.score), False, black)
        self.screen.blit(text, (self.width/2,50, 100, 200))

    # Keeps track of all conditions for a game over
    def game_over(self):
        

        if self.bird.y > self.width:
            return True

        for pipe_pair in self.pipes:
            if pygame.Rect(pipe_pair.x, pipe_pair.lower.height, pipe_pair.width, self.height).collidepoint(self.bird.x + 25, self.bird.y + 25) or pygame.Rect(pipe_pair.x, 0, pipe_pair.width, pipe_pair.upper.height).collidepoint(self.bird.x + 25, self.bird.y + 25):
                return True
            

        else:
            return False


    def run(self):
        counter = 0
        rand = random.randint(100,500)

        while 1:
            # Check user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.bird.dx, self.bird.dy = self.key.get(event.key, (self.bird.dx,self.bird.dy))
                
            # Game over
            if self.game_over():
                self.screen.blit(self.game_over_image, ((self.width - self.game_over_image.get_width())/2, (self.height - self.game_over_image.get_height())/2))
                pygame.display.flip()
                self.clock.tick(self.fps)

                continue

            # Continue game loop
            self.update_bird()
            self.update_pipes()
            self.update_score()
            pygame.display.flip()
            self.clock.tick(self.fps)

            if counter == 100:
                rand = random.randint(100,300)
                self.pipes.append(PipePair(rand, 3))
                counter = 0
            

            counter += 1
            print(self.score)



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
    def __init__(self, x, dx, height, width=75, y=0, dy=0):
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
        self.upper = Pipe(x = self.x, dx = dx, height = centerpos - 60)
        self.lower = Pipe(x = self.x, dx = dx, height = centerpos + 60)
        self.width = self.upper.width
        

    def move(self):
        self.upper.move()
        self.lower.move()
        self.x -= self.upper.dx

test = FlappyBird()
test.run()