#! /usr/bin/env python
import pygame
import random as Random
from pygame.locals import *
from sys import exit
import heapq


pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)

font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)
info_font = pygame.font.SysFont(font_name, 24)
menu_font = pygame.font.SysFont(font_name, 36)

screen = pygame.display.set_mode((448,546), 0, 32)

# Upload the images
background_filename = './images/bg.png'
frog_filename = './images/sprite_sheets_up.png'
arrived_filename = './images/frog_arrived.png'
car1_filename = './images/car1.png'
car2_filename = './images/car2.png'
car3_filename = './images/car3.png'
car4_filename = './images/car4.png'
car5_filename = './images/car5.png'
platform_filename = './images/tronco.png'

background = pygame.image.load(background_filename).convert()
sprite_sapo = pygame.image.load(frog_filename).convert_alpha()
sprite_arrived = pygame.image.load(arrived_filename).convert_alpha()
sprite_car1 = pygame.image.load(car1_filename).convert_alpha()
sprite_car2 = pygame.image.load(car2_filename).convert_alpha()
sprite_car3 = pygame.image.load(car3_filename).convert_alpha()
sprite_car4 = pygame.image.load(car4_filename).convert_alpha()
sprite_car5 = pygame.image.load(car5_filename).convert_alpha()
sprite_platform = pygame.image.load(platform_filename).convert_alpha()

# Load the sound effects
hit_sound = pygame.mixer.Sound('./sounds/boom.wav')
agua_sound = pygame.mixer.Sound('./sounds/agua.wav')
chegou_sound = pygame.mixer.Sound('./sounds/success.wav')
trilha_sound = pygame.mixer.Sound('./sounds/guimo.wav')


# Define sprite filenames for each direction
sprite_filenames = {
    'up': './images/sprite_sheets_up.png',
    'down': './images/sprite_sheets_down.png',
    'left': './images/sprite_sheets_left.png',
    'right': './images/sprite_sheets_right.png'
}

# Load each sprite
sprites_sapo = {direction: pygame.image.load(filename).convert_alpha() for direction, filename in sprite_filenames.items()}

pygame.display.set_caption('Frogger AI')
clock = pygame.time.Clock()

# Constants for the grid and pathfinding
GRID_WIDTH = 16
GRID_HEIGHT = 13
CELL_SIZE = 34
grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 1
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 2
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 3
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 4
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 5
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 6
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 7
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 8
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 10
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 11
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Row 12: bottom
]

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __lt__(self, other):
        return self.f < other.f

def manhattan_distance(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

def get_neighbors(node):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down
    neighbors = []
    for dx, dy in directions:
        nx, ny = node.x + dx, node.y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT and grid[ny][nx] == 0:
            neighbors.append(Node(nx, ny))
    return neighbors

def astar(start, end):
    open_list = []
    closed_set = set()
    heapq.heappush(open_list, start)
    start.g = 0
    start.h = manhattan_distance(start, end)
    start.f = start.g + start.h

    while open_list:
        current = heapq.heappop(open_list)
        if (current.x, current.y) == (end.x, end.y):
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed_set.add((current.x, current.y))

        for neighbor in get_neighbors(current):
            if (neighbor.x, neighbor.y) in closed_set:
                continue

            tentative_g = current.g + 1
            if (neighbor.x, neighbor.y) not in [(n.x, n.y) for n in open_list] or tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = manhattan_distance(neighbor, end)
                neighbor.f = neighbor.g + neighbor.h
                heapq.heappush(open_list, neighbor)

    return None  # No path found


class Object():
    def __init__(self,position,sprite):
        self.sprite = sprite
        self.position = position

    def draw(self):
        screen.blit(self.sprite,(self.position))

    def rect(self):
        return Rect(self.position[0],self.position[1],self.sprite.get_width(),self.sprite.get_height())


class Frog(Object):
    def __init__(self,position,sprites):
        self.sprites = sprites
        self.sprite = sprites['up']
        self.position = position
        self.lives = 3
        self.animation_counter = 0
        self.animation_tick = 1
        self.way = "UP"
        self.can_move = 1

    def updateSprite(self,key_pressed):
        if self.way != key_pressed:
            self.way = key_pressed
            self.sprite = self.sprites[self.way]


    def moveFrog(self,key_pressed, key_up):
        if self.animation_counter == 0 :
            self.updateSprite(key_pressed)
        self.incAnimationCounter()
        if key_up == 1:
            if key_pressed == "up":
                if self.position[1] > 39:
                    self.position[1] = self.position[1]-13
            elif key_pressed == "down":
                if self.position[1] < 473:
                    self.position[1] = self.position[1]+13
            if key_pressed == "left":
                if self.position[0] > 2:
                    if self.animation_counter == 2 :
                        self.position[0] = self.position[0]-13
                    else:
                        self.position[0] = self.position[0]-14
            elif key_pressed == "right":
                if self.position[0] < 401:
                    if self.animation_counter == 2 :
                        self.position[0] = self.position[0]+13
                    else:
                        self.position[0] = self.position[0]+14

    def animateFrog(self,key_pressed,key_up):
        if self.animation_counter != 0 :
            if self.animation_tick <= 0 :
                self.moveFrog(key_pressed,key_up)
                self.animation_tick = 1
            else :
                self.animation_tick = self.animation_tick - 1

    def setPos(self,position):
        self.position = position

    def decLives(self):
        self.lives = self.lives - 1

    def cannotMove(self):
        self.can_move = 0

    def incAnimationCounter(self):
        self.animation_counter = self.animation_counter + 1
        if self.animation_counter == 3 :
            self.animation_counter = 0
            self.can_move = 1

    def frogDead(self,game):
        self.setPositionToInitialPosition()
        self.decLives()
        game.resetTime()
        self.animation_counter = 0
        self.animation_tick = 1
        self.way = "UP"
        self.can_move = 1

    def setPositionToInitialPosition(self):
        self.position = [207, 475]

    def draw(self):
        current_sprite = self.animation_counter * 30
        screen.blit(self.sprite,(self.position),(0 + current_sprite, 0, 30, 30 + current_sprite))

    def rect(self):
        return Rect(self.position[0],self.position[1],30,30)

class Enemy(Object):
    def __init__(self,position,sprite_enemy,way,factor):
        self.sprite = sprite_enemy
        self.position = position
        self.way = way
        self.factor = factor

    def move(self,speed):
        if self.way == "right":
            self.position[0] = self.position[0] + speed * self.factor
        elif self.way == "left":
            self.position[0] = self.position[0] - speed * self.factor


class Platform(Object):
    def __init__(self,position,sprite_platform,way):
        self.sprite = sprite_platform
        self.position = position
        self.way = way

    def move(self,speed):
        if self.way == "right":
            self.position[0] = self.position[0] + speed
        elif self.way == "left":
            self.position[0] = self.position[0] - speed


class Game():
    def __init__(self,speed,level):
        self.speed = speed
        self.level = level
        self.points = 0
        self.time = 30
        self.gameInit = 0

    def incLevel(self):
        self.level = self.level + 1

    def incSpeed(self):
        self.speed = self.speed + 1

    def incPoints(self,points):
        self.points = self.points + points

    def decTime(self):
        self.time = self.time - 1

    def resetTime(self):
        self.time = 30


#General Functions
def drawList(list):
    for i in list:
        i.draw()

def moveList(list,speed):
    for i in list:
        i.move(speed)

def destroyenemies(list):
    for i in list:
        if i.position[0] < -80:
            list.remove(i)
        elif i.position[0] > 516:
            list.remove(i)

def destroyPlatforms(list):
    for i in list:
        if i.position[0] < -100:
            list.remove(i)
        elif i.position[0] > 448:
            list.remove(i)

def createenemies(list,enemies,game):
    for i, tick in enumerate(list):
        list[i] = list[i] - 1
        if tick <= 0:
            if i == 0:
                list[0] = (40*game.speed)/game.level
                position_init = [-55,436]
                enemy = Enemy(position_init,sprite_car1,"right",1)
                enemies.append(enemy)
            elif i == 1:
                list[1] = (30*game.speed)/game.level
                position_init = [506, 397]
                enemy = Enemy(position_init,sprite_car2,"left",2)
                enemies.append(enemy)
            elif i == 2:
                list[2] = (40*game.speed)/game.level
                position_init = [-80, 357]
                enemy = Enemy(position_init,sprite_car3,"right",2)
                enemies.append(enemy)
            elif i == 3:
                list[3] = (30*game.speed)/game.level
                position_init = [516, 318]
                enemy = Enemy(position_init,sprite_car4,"left",1)
                enemies.append(enemy)
            elif i == 4:
                list[4] = (50*game.speed)/game.level
                position_init = [-56, 280]
                enemy = Enemy(position_init,sprite_car5,"right",1)
                enemies.append(enemy)

def createPlatform(list,platforms,game):
    for i, tick in enumerate(list):
        list[i] = list[i] - 1
        if tick <= 0:
            if i == 0:
                list[0] = (30*game.speed)/game.level
                position_init = [-100,200]
                platform = Platform(position_init,sprite_platform,"right")
                platforms.append(platform)
            elif i == 1:
                list[1] = (30*game.speed)/game.level
                position_init = [448, 161]
                platform = Platform(position_init,sprite_platform,"left")
                platforms.append(platform)
            elif i == 2:
                list[2] = (40*game.speed)/game.level
                position_init = [-100, 122]
                platform = Platform(position_init,sprite_platform,"right")
                platforms.append(platform)
            elif i == 3:
                list[3] = (40*game.speed)/game.level
                position_init = [448, 83]
                platform = Platform(position_init,sprite_platform,"left")
                platforms.append(platform)
            elif i == 4:
                list[4] = (20*game.speed)/game.level
                position_init = [-100, 44]
                platform = Platform(position_init,sprite_platform,"right")
                platforms.append(platform)

def carChangeRoad(enemies):
    enemy = Random.choice(enemies)
    initialPosition = enemy.position[1]

    choice = Random.randint(1,2)
    if (choice % 2 == 0):
        enemy.position[1] = enemy.position[1] + 39
    else :
        enemy.position[1] = enemy.position[1] - 39

    if enemy.position[1] > 436:
        enemy.position[1] = initialPosition
    elif enemy.position[1] < 280:
        enemy.position[1] = initialPosition


def frogOnTheStreet(frog,enemies,game):
    for i in enemies:
        enemyRect = i.rect()
        frogRect = frog.rect()
        if frogRect.colliderect(enemyRect):
            hit_sound.play()
            frog.frogDead(game)

def frogInTheLake(frog,platforms,game):
    #if the frog is on any platform Safe = 1
    safe = 0
    wayPlatform = ""
    for i in platforms:
        platformRect = i.rect()
        frogRect = frog.rect()
        if frogRect.colliderect(platformRect):
            safe = 1
            wayPlatform = i.way

    if safe == 0:
        agua_sound.play()
        frog.frogDead(game)

    elif safe == 1:
        if wayPlatform == "right":
            frog.position[0] = frog.position[0] + game.speed

        elif wayPlatform == "left":
            frog.position[0] = frog.position[0] - game.speed

def frogArrived(frog,chegaram,game):
    if frog.position[0] > 33 and frog.position[0] < 53:
        position_init = [43,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 115 and frog.position[0] < 135:
        position_init = [125,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 197 and frog.position[0] < 217:
        position_init = [207,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 279 and frog.position[0] < 299:
        position_init = [289,7]
        createArrived(frog,chegaram,game,position_init)

    elif frog.position[0] > 361 and frog.position[0] < 381:
        position_init = [371,7]
        createArrived(frog,chegaram,game,position_init)

    else:
        frog.position[1] = 46
        frog.animation_counter = 0
        frog.animation_tick = 1
        frog.can_move = 1


def whereIsTheFrog(frog, enemies, platforms, chegaram, game):
    # Determine Frog's current zone and handle interactions
    if frog.position[1] > 240:
        frogOnTheStreet(frog, enemies, game)
    elif 40 < frog.position[1] <= 240:
        frogInTheLake(frog, platforms, game)
    elif frog.position[1] <= 40:
        frogArrived(frog, chegaram, game)


def createArrived(frog,chegaram,game,position_init):
    sapo_chegou = Object(position_init,sprite_arrived)
    chegaram.append(sapo_chegou)
    chegou_sound.play()
    frog.setPositionToInitialPosition()
    game.incPoints(10 + game.time)
    game.resetTime()
    frog.animation_counter = 0
    frog.animation_tick = 1
    frog.can_move = 1


def nextLevel(chegaram,enemies,platforms,frog,game):
    if len(chegaram) == 5:
        chegaram[:] = []
        frog.setPositionToInitialPosition()
        game.incLevel()
        game.incSpeed()
        game.incPoints(100)
        game.resetTime()

# Print grid with path and targets marked
def print_grid(grid, start, targets):
    for y in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            if (x, y) == start:
                row += 'S '  # Start
            elif (x, y) in targets:
                row += 'T '  # Target
            elif grid[y][x] == 1:
                row += 'X '  # Obstacle
            else:
                row += '. '  # Open path
        print(row)

# Assuming your grid size and coordinates map directly to array indices
start_position = (207 // 34, 475 // 34)  # Convert pixel position to grid coordinates
target_positions = [(pos[0] // 34, pos[1] // 34) for pos in [(125, 7), (207, 7), (289, 7), (371, 7)]]
print_grid(grid, start_position, target_positions)

def main():
    trilha_sound.play(-1)
    text_info = menu_font.render(('Press any key to start!'), 1, (0, 0, 0))
    gameInit = 0

    while gameInit == 0:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                gameInit = 1

        screen.blit(background, (0, 0))
        screen.blit(text_info, (80, 150))
        pygame.display.update()

    game = Game(3, 1)
    key_up = 1
    frog_initial_position = [207, 475]  # Starting position of the frog in pixels
    frog = Frog([207, 475], sprites_sapo)

    enemies = []
    platforms = []
    chegaram = []
    ticks_enemies = [30, 0, 30, 0, 60]
    ticks_platforms = [0, 0, 30, 30, 30]
    ticks_time = 30

    # Define target positions where the frog tries to arrive
    end_positions = [(43, 7), (125, 7), (207, 7), (289, 7), (371, 7)]
    paths = []
    start_node = Node(frog_initial_position[0] // CELL_SIZE, frog_initial_position[1] // CELL_SIZE)

    # Find paths to each target position and store them
    for goal_pixel_pos in end_positions:
        end_node = Node(goal_pixel_pos[0] // CELL_SIZE, goal_pixel_pos[1] // CELL_SIZE)
        path = astar(start_node, end_node)
        if path:
            paths.append(path)
        else:
            print("No path found to", goal_pixel_pos)

    current_path_index = 0
    current_step_index = 0

    while frog.lives > 0:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        # Update frog position based on the path
        if current_path_index < len(paths) and current_step_index < len(paths[current_path_index]):
            next_x, next_y = paths[current_path_index][current_step_index]
            frog.setPos([next_x * CELL_SIZE, next_y * CELL_SIZE])
            current_step_index += 1
        else:
            current_path_index += 1
            current_step_index = 0

        if current_path_index >= len(paths):
            break  # End game or loop back to start

        if not ticks_time:
            ticks_time = 30
            game.decTime()
        else:
            ticks_time -= 1

        if game.time == 0:
            frog.frogDead(game)

        createenemies(ticks_enemies, enemies, game)
        createPlatform(ticks_platforms, platforms, game)

        moveList(enemies, game.speed)
        moveList(platforms, game.speed)

        whereIsTheFrog(frog, enemies, platforms, chegaram, game)

        nextLevel(chegaram, enemies, platforms, frog, game)

        text_info1 = info_font.render(f'Level: {game.level}               Points: {game.points}', 1, (255, 255, 255))
        text_info2 = info_font.render(f'Time: {game.time}           Lifes: {frog.lives}', 1, (255, 255, 255))
        screen.blit(background, (0, 0))
        screen.blit(text_info1, (10, 520))
        screen.blit(text_info2, (250, 520))

        Random_chance = Random.randint(0, 100)
        if Random_chance % 100 == 0:
            carChangeRoad(enemies)

        drawList(enemies)
        drawList(platforms)
        drawList(chegaram)

        frog.draw()

        destroyenemies(enemies)
        destroyPlatforms(platforms)

        pygame.display.update()
        time_passed = clock.tick(30)

    while gameInit == 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                gameInit = 0

        screen.blit(background, (0, 0))
        text = game_font.render('GAME OVER', 1, (255, 0, 0))
        text_points = game_font.render(f'Score: {game.points}', 1, (255, 0, 0))
        text_reiniciar = info_font.render('Press any key to restart!', 1, (255, 0, 0))
        screen.blit(text, (75, 120))
        screen.blit(text_points, (10, 170))
        screen.blit(text_reiniciar, (70, 250))

        pygame.display.update()

if __name__ == "__main__":
    main()