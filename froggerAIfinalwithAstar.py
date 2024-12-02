import pygame
import random
import time
import heapq
import numpy as np

pygame.init()
screen_width = 350
screen_height = 400
white = (255, 255, 255)

finish = False   # Check if application is running
fps = 20  # Simulation speed, can be changed if needed
frogNum = 100  # Number of frogs in each generation, can be changed if needed

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Frogger-AI')
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
backgroundImage = pygame.image.load('images1/background.gif')

turtles = pygame.sprite.Group()
frogs = pygame.sprite.Group()

frog = pygame.image.load('images1/frog10.gif')
frogDead = pygame.image.load('images1/frog11.png')

yellowCar = pygame.image.load('images1/yellowCar.gif')  # row 2
dozer = pygame.image.load('images1/dozer.gif')  # row 3
purpleCar = pygame.image.load('images1/purpleCar.gif')  # row 4
greenCar = pygame.image.load('images1/greenCar.gif')  # row 5
truck = pygame.image.load('images1/truck.gif')  # row 6

logShort = pygame.image.load('images1/logShort.gif')
logMedium = pygame.image.load('images1/logMedium.gif')
logLong = pygame.image.load('images1/logLong.gif')

twoTurtles = pygame.image.load('images1/turtletwo.gif')
twoTurtlesDive = pygame.image.load('images1/turtletwodown.gif')
threeTurtles = pygame.image.load('images1/turtlethree.gif')
threeTurtlesDive = pygame.image.load('images1/turtlethreedown.gif')

turtleCounter = 0  # Timer for turtle state

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float('inf')  # Initialize cost to reach this node as infinity
        self.h = 0  # Heuristic value, to be calculated later
        self.parent = None

    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

class Turtle(pygame.sprite.Sprite):
    def __init__(self, canDive, size, startX, startY, width, height, speed):
        pygame.sprite.Sprite.__init__(self)
        self.canDive = canDive  # 1 - does not dive, 2 - dives
        self.size = size
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = startX
        self.rect.y = startY
        self.width = width
        self.height = height
        self.speed = speed
        self.state = 0  # 0 - not diving, 1 - diving

        if (self.size == 2):
            self.image = twoTurtles
        elif (self.size == 3):
            self.image = threeTurtles

    # Updates location of turtle
    def update(self):
        self.rect.x += self.speed

        if (self.size == 2):
            if (self.rect.x + 50 < 0):
                self.rect.x = screen_width + 50
        elif (self.size == 3):
            if (self.rect.x + 75 < 0):
                self.rect.x = screen_width + 75

        self.collision()

    # Checks to see if frog is on turtle, if turtles have dived frog needs to die
    def collision(self):
        for f in frogs:
            if f.rect.colliderect(self) and f.dead == False:
                if self.state == 1:
                    f.die()
                else:
                    f.rect.x += self.speed

class Log(pygame.sprite.Sprite):
    def __init__(self, startX, startY, size, width, height, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = startX
        self.rect.y = startY
        self.size = size
        self.width = width
        self.height = height
        self.speed = speed

        if (self.size == 'short'):
            self.image = logShort
        elif (self.size == 'medium'):
            self.image = logMedium
        elif (self.size == 'long'):
            self.image = logLong

    # Updating log position
    def update(self):
        self.rect.x += self.speed

        if (self.size == 'short' or self.size == 'medium'):
            if (self.rect.x - 100 > screen_width):
                self.rect.x = -100
        else:
            if (self.rect.x - 200 > screen_width):
                self.rect.x = -200

        self.collision()

    # Checking for collision with frogs
    def collision(self):
        for f in frogs:
            if f.rect.colliderect(self) and f.dead == False:
                f.rect.x += self.speed

# Car Object
class Car(pygame.sprite.Sprite):
    def __init__(self, startX, startY, img, speed, direction, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = startX
        self.rect.y = startY
        self.img = img
        self.speed = speed
        self.direction = direction  # -1 - left, 1 - right
        self.width = width
        self.height = height

        if (self.img == 'yellow'):
            self.image = yellowCar
        elif (self.img == 'green'):
            self.image = greenCar
        elif (self.img == 'truck'):
            self.image = truck
        elif (self.img == 'dozer'):
            self.image = dozer
        elif (self.img == 'purple'):
            self.image = purpleCar

    # Update car position
    def update(self):
        if (self.direction == -1):
            self.rect.x += self.speed
        elif (self.direction == 1):
            self.rect.x -= self.speed

        if (self.direction == -1 and self.rect.x - 75 > screen_width):
            self.rect.x = -75
        elif (self.direction == 1 and self.rect.x + 75 < 0):
            self.rect.x = screen_width + 75
        self.collision()

    # Checks car collision with frogs
    def collision(self):
        for f in frogs:
            if (self.rect.colliderect(f) and f.dead == False):
                f.die()

class Frog(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, size, brain, mode='q_learning'):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images1/frog10.gif')
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        self.size = size
        self.brain = brain
        self.mode = mode
        self.path = []
        self.path_index = 0
        if self.mode == 'astar':
            self.calculate_path()

    def calculate_path(self):
        # Define start and goal for A*
        start = Node(int(self.rect.x / 25), int(self.rect.y / 25))  # Assuming grid size of 25 pixels
        goal = Node(int(self.rect.x / 25), 0)  # Goal is top of the screen
        self.path = a_star(start, goal)
        self.path_index = 0

    def update(self):
        if self.mode == 'q_learning':
            # Existing Q-learning logic
            stepNum = self.brain.step
            if stepNum < self.size and not self.dead:
                direction = self.brain.directions[stepNum]
                self.move_based_on_direction(direction)
                self.brain.step += 1
        elif self.mode == 'astar' and self.path:
            # A* pathfinding logic
            if self.path_index < len(self.path):
                next_x, next_y = self.path[self.path_index]
                self.rect.x, self.rect.y = next_x * 25, next_y * 25
                self.path_index += 1
            else:
                self.calculate_path()  # Recalculate path if needed

        self.check_river_and_die()

    def move_based_on_direction(self, direction):
        if direction == 1 and self.rect.y > 0:
            self.rect.y -= 25
            self.fitness += 1
        elif direction == 2 and self.rect.y < 375:
            self.rect.y += 25
            self.fitness -= 1
        elif direction == 3 and self.rect.x > 25:
            self.rect.x -= 25
        elif direction == 4 and self.rect.x < 300:
            self.rect.x += 25

    def check_river_and_die(self):
        # River logic remains unchanged
        if self.rect.y <= 175 and self.rect.y != 50 and not self.dead:
            if not any(self.rect.colliderect(x.rect) for x in all_sprites.union(turtles)):
                self.die()
        elif self.rect.y == 50 and not self.dead:
            self.fitness = 13
            self.die()

    def die(self):
        self.image = pygame.image.load('images1/frog11.png')
        self.dead = True
        Population.frogsAlive -= 1


class Population:
    bestFrog = 0  # The index for the most fit frog
    fitnessSum = 0  # Sum of all frogs' fitness
    frogsAlive = frogNum  # All frogs are alive at the beginning
    isFinished = False  # Sets to True when a frog reaches the end of the game
    generation = 1 # Set to 1 in the beginning

    def __init__(self, alive, size):
        self.size = size # Number of directions given to a frog
        self.alive = alive
        self.randomize()

    # Randomizes the frog's directions
    def randomize(self):
        for i in range(0, self.alive):
            directions = []
            for z in range(0, self.size):
                randomNum = random.randint(0, 4)
                directions.append(randomNum)

            dir = FrogDirections(1000, directions)
            frogs.add(Frog(167.5, 350, self.size, dir))

    # Finding the sum of all the fitnesses from previous generation
    def setFitnessSum(self):
        sum = 0
        for frog in frogs:
            sum += frog.fitness
        self.fitnessSum = sum

    # Randomly selecting a parent frog from previous generation
    def selectParent(self):
        self.setFitnessSum()
        max_num = min(frogNum, self.fitnessSum)
        rand = random.randint(0, max_num)
        runningSum = 0
        for frog in frogs:
            runningSum += frog.fitness
            if runningSum >= rand:
                return frog.brain.directions

    # Selecting a new generation of frogs
    def selection(self):
        best = list(self.bestFrogDirections())
        newFrogs = []
        if (self.isFinished == False):
            dir = list(best)
            newDirections = FrogDirections(1000, dir)
            newFrogs.append(Frog(167.5, 350, self.size, newDirections)) # Save the best frog

            for x in range(1, frogNum):
                dir = list(self.selectParent())
                newDirections = FrogDirections(1000, mutate(dir))
                newFrogs.append(Frog(167.5, 350, self.size, newDirections))
            Population.frogsAlive = frogNum

            frogs.empty()
            for frog in newFrogs:
                frogs.add(frog)
        else: # If a frog has gotten to the end reset his position to the start of the game
            frogs.empty()
            for x in range(0, 1):
                dir = list(best)
                directions = FrogDirections(1000, dir)
                frogs.add(Frog(167.5, 350, self.size, directions))
            Population.frogsAlive = 1

    # Determine the best frog directions from the previous generation and return its directions
    def bestFrogDirections(self):
        if (self.isFinished == False):
            sortedFrogs = []
            for frog in frogs:
                sortedFrogs.append(frog)

            sortedFrogs.sort(key = lambda frog: frog.fitness) # Sort frogs by fitness

            best = frogNum - 1
            for i in range(0, frogNum - 1):
                if sortedFrogs[i].brain.step < sortedFrogs[frogNum - 1].brain.step and sortedFrogs[i].fitness == sortedFrogs[frogNum - 1].fitness:
                    best = i

            if (sortedFrogs[best].fitness == 13):
                self.isFinished = True
            else:
                self.generation += 1

            for frog in frogs:
                if (sortedFrogs[best].fitness == frog.fitness and sortedFrogs[best].brain.step == frog.brain.step):
                    bestFrogDirections = list(frog.brain.directions)
                    break
            return bestFrogDirections
        else:
            for frog in frogs:
                bestFrogDirections = list(frog.brain.directions)
            return bestFrogDirections

class FrogDirections:
    step = 0
    def __init__(self, size, directions):
        self.size = size
        self.directions = directions

# Randomly mutates the direction vectors of the frog
def mutate(d):
    for i in range(0, len(d)):
        randomNum = random.randint(0, 4)
        if randomNum == 1:
            d[i] = random.randint(0, 4)
    return d

# A* Pathfinding Algorithm
def a_star(start, goal):
    open_list = []
    closed_list = set()

    heapq.heappush(open_list, (0, start))
    start.g = 0

    while open_list:
        current_node = heapq.heappop(open_list)[1]

        if current_node == goal:
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]

        closed_list.add(current_node)

        for next_node in get_neighbors(current_node):
            if next_node in closed_list:
                continue

            tentative_g = current_node.g + 1  # Assuming each move has a cost of 1

            if tentative_g < next_node.g:
                next_node.parent = current_node
                next_node.g = tentative_g
                next_node.h = abs(next_node.x - goal.x) + abs(next_node.y - goal.y)
                next_node.f = next_node.g + next_node.h

                if next_node not in open_list:
                    heapq.heappush(open_list, (next_node.f, next_node))

    return None

def get_neighbors(node):
    neighbors = []
    # Define the grid size and possible movements
    movements = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    grid_width = 7  # Adjust according to your grid size
    grid_height = 5  # Adjust according to your grid size

    for dx, dy in movements:
        new_x = node.x + dx
        new_y = node.y + dy
        if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
            neighbors.append(Node(new_x, new_y))

    return neighbors

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.g = float('inf')
        self.h = 0
        self.f = 0

# Q-Learning Algorithm
class QLearning:
    def __init__(self, num_states, num_actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1):
        self.num_states = num_states
        self.num_actions = num_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = np.zeros((350*400, 4))  # Adjust size here

    def select_action(self, state):
        if np.random.rand() < self.exploration_rate:
            return np.random.choice(self.num_actions)
        else:
            return np.argmax(self.q_table[state, :])

    def update_q_table(self, state, action, reward, next_state):
        old_q_value = self.q_table[state, action]
        temporal_difference = reward + self.discount_factor * np.max(self.q_table[next_state, :]) - old_q_value
        new_q_value = old_q_value + self.learning_rate * temporal_difference
        self.q_table[state, action] = new_q_value

# Environment Representation
class FroggerEnvironment:
    def __init__(self):
        self.num_states = 35  # Define your state space size
        self.num_actions = 4  # Define your action space size
        self.goal_state = (6, 0)  # Define the goal state
        self.agent_position = (0, 2)  # Define the initial agent position

    def reset(self):
        self.agent_position = (0, 2)  # Reset the agent position
        return self.agent_position

    def step(self, action):
        # Define the transition dynamics and reward function
        if action == 0:  # Move up
            self.agent_position = (self.agent_position[0], max(self.agent_position[1] - 1, 0))
        elif action == 1:  # Move down
            self.agent_position = (self.agent_position[0], min(self.agent_position[1] + 1, 4))
        elif action == 2:  # Move left
            self.agent_position = (max(self.agent_position[0] - 1, 0), self.agent_position[1])
        elif action == 3:  # Move right
            self.agent_position = (min(self.agent_position[0] + 1, 6), self.agent_position[1])

        reward = self.calculate_reward()
        done = self.agent_position == self.goal_state
        return self.agent_position, reward, done

    def calculate_reward(self):
        # Define your reward function
        return -1  # For each step until reaching the goal

class FrogMovementIntegration:
    def __init__(self):
        self.env = FroggerEnvironment()
        # Adjust num_states and num_actions based on Q-table dimensions
        self.q_learning = QLearning(num_states=350*400, num_actions=4)
        self.goal_state = (6, 0)  # Define the goal state

    def get_state_from_position(self, x, y):
        # Define how to map position to state
        return x + y * 350  # Assuming the grid is 350x400 pixels

    def update_frog_movement(self, frog):
        current_state = self.get_state_from_position(frog.rect.x, frog.rect.y)
        action = self.q_learning.select_action(current_state)
        next_position, reward, done = self.env.step(action)
        next_state = self.get_state_from_position(*next_position)
        self.q_learning.update_q_table(current_state, action, reward, next_state)
        if done:
            frog.rect.x, frog.rect.y = self.env.reset()
            self.q_learning.exploration_rate *= 0.99  # Decrease exploration rate over time

    def get_state_from_position(self, x, y):
        # Define how to map position to state
        return x + y * 7  # Assuming the grid is 7x5

# Update frog movement integration in the main loop
frog_integration = FrogMovementIntegration()

# Define the text display functions
def text_objects(text, font):
    textSurface = font.render(text, True, white)
    return textSurface, textSurface.get_rect()

def message_display(text, position):
    largeText = pygame.font.Font('freesansbold.ttf', 16) # default pygame font
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((screen_width / 2), 10 + position)
    screen.blit(TextSurf, TextRect)

# Define the set function to initialize the game environment
def set():
    # Clear existing sprites
    for t in turtles:
        t.kill()
    for a in all_sprites:
        a.kill()

    # Create new sprites
    # Turtles
    for i in range(0, 8):
        if i < 4:
            if i % 3 == 0:  # Every third turtle should be able to dive
                turtles.add(Turtle(2, 3, 100 * (4 - i), 175, 75, 25, -2))
            else:
                turtles.add(Turtle(1, 3, 100 * (4 - i), 175, 75, 25, -2))
        else:
            if i % 3 == 0:
                turtles.add(Turtle(2, 2, 87.5 * (8 - i), 100, 50, 25, -2))
            else:
                turtles.add(Turtle(1, 2, 87.5 * (8 - i), 100, 50, 25, -2))

    # Logs
    for i in range(0, 9):
        if i < 3:
            all_sprites.add(Log(-100 + 150 * (3 - i), 150, 'short', 62.5, 25, 3))
        elif i < 6:
            all_sprites.add(Log(-150 + 200 * (6 - i), 125, 'long', 150, 25, 4))
        else:
            all_sprites.add(Log(-200 + 150 * (9 - i), 75, 'medium', 87.5, 25, 6))

    # Cars
    for i in range(0, 12):
        if i < 3:
            all_sprites.add(Car(100 + 75 * (3 - i), 325, 'yellow', 6, 1, 25, 25))
        elif i < 6:
            all_sprites.add(Car(-150 + 75 * (6 - i), 300, 'dozer', 2, -1, 25, 25))
        elif i < 9:
            all_sprites.add(Car(50 + 75 * (9 - i), 275, 'purple', 4, 1, 25, 25))
        elif i < 10:
            all_sprites.add(Car(25 + 75 * (10 - i), 250, 'green', 10, -1, 25, 25))
        else:
            all_sprites.add(Car(50 + 150 * (12 - i), 225, 'truck', 3, 1, 50, 25))

    # Initialize frogs with a mix of Q-learning and A* pathfinding
    directions = []
    for z in range(1000): 
        randomNum = random.randint(0, 4)
        directions.append(randomNum)

    for i in range(frogNum):
        brain = FrogDirections(1000, directions)
        mode = 'astar' if i % 2 == 0 else 'q_learning'  
        frogs.add(Frog(167.5, 350, 1000, brain, mode=mode))


# Initialize the population of frogs
pop = Population(frogNum, 1000)
set()

# Main game loop
finish = False


while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True

    screen.blit(backgroundImage, (0, 0))

    # If all frogs are dead, reset game board
    if (Population.frogsAlive == 0):
        pop.selection()
        set()
        time.sleep(2.5) # Sleeps so that the frogs are given a chance to reset properly before the game restarts

    message_display('Generation: ' + str(pop.generation), 0)
    message_display('Frogs alive: ' + str(pop.frogsAlive), 18)
    # Update and draw all sprites
    all_sprites.update()
    all_sprites.draw(screen)
    turtles.update()
    turtles.draw(screen)

    # frog updates according to its assigned AI mode
    for frog in frogs:
        if frog.mode == 'astar' and not frog.dead:
            if not frog.path or frog.path_index >= len(frog.path):
                frog.calculate_path()
            # Continue on the calculated path
            if frog.path_index < len(frog.path):
                next_x, next_y = frog.path[frog.path_index]
                frog.rect.x, frog.rect.y = next_x * 25, next_y * 25  
                frog.path_index += 1
        elif frog.mode == 'q_learning':
            # Q-learning movement update
            frog_integration.update_frog_movement(frog)

        frog.update()  # Regular update (collision checks, etc.)

    frogs.draw(screen)

    pygame.display.update()
    clock.tick(fps)

    # Handling diving of turtles
    turtleCounter += 1
    if turtleCounter == 50:
        turtleCounter = 0
        for t in turtles:
            if t.canDive == 2:
                t.state = 1 - t.state  # Toggle diving state
                if t.size == 2:
                    t.image = twoTurtlesDive if t.state == 1 else twoTurtles
                else:
                    t.image = threeTurtlesDive if t.state == 1 else threeTurtles

pygame.quit()
quit()