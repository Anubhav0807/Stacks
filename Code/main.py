# STACK

# Importing
import os
import pickle
import pygame
from pygame.locals import *
from random import randint

# Inisialization
pygame.init()
pygame.mixer.init()

# Creating window
screen_width = 500
screen_height = 600
gameWindow = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('STACKS GAME')

# Game specific variables
font1 = pygame.font.SysFont(None, 128)
font2 = pygame.font.SysFont(None, 32)
clock = pygame.time.Clock()
Color_init = ([255,0,0], [255,255,0], [0,255,0], [0,255,255], [0,0,255], [255,0,255])
ColorCode = ((0,1,0), (-1,0,0), (0,0,1), (0,-1,0), (1,0,0), (0,0,-1))
fps = 60
stack_b = 10
stack_velocity_x = 5
stack_velocity_y = 2
color_diff = 30
Tower, Vanishing = [], []

# Colours
red=(255,0,0)
green=(0,255,0)
blue=(0,0,255)
black=(0, 0, 0)
white=(255,255,255)

# Path related stuff
rootdir = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]

# Images
play_image = pygame.image.load(os.path.join(rootdir, 'Assets\\Sprites\\play_image.png'))
play_image = pygame.transform.scale(play_image, (200, 200)).convert_alpha()

game_over_image = pygame.image.load(os.path.join(rootdir, 'Assets\\Sprites\\game_over_image.png'))
game_over_image = pygame.transform.scale(game_over_image, (400, 200)).convert_alpha()

# Music & Sound effects
bg_music = os.path.join(rootdir, 'Assets\\Audio\\bg_music.mp3')

intro_sound = pygame.mixer.Sound(os.path.join(rootdir, 'Assets\\Audio\\intro_sound.wav'))
drop_sound = pygame.mixer.Sound(os.path.join(rootdir, 'Assets\\Audio\\drop_sound.wav'))
place_sound = pygame.mixer.Sound(os.path.join(rootdir, 'Assets\\Audio\\place_sound.wav'))
game_over_sound = pygame.mixer.Sound(os.path.join(rootdir, 'Assets\\Audio\\game_over_sound.wav'))

# Data storage file (to store high score)
score_file_path = os.path.join(rootdir, "Data\\HighScore.dat")

def Stack(d):
    "Moves the stack in horizontal and vertical motion"
    global stack_x2, stack_y2, score, high_score
    if placing:
        if stack_y2 >= stack_y1-stack_b:
            temp_stack_l, temp_stack_x2 = PlaceStack(d)
            if stack_l <= 0:
                Vanishing[-1]['x'] = temp_stack_x2
                Vanishing[-1]['len'] = temp_stack_l
                return True
            else:
                score += 1
                if high_score<score:
                    high_score = score
        else:
            stack_y2 += stack_velocity_y
    else:
        stack_x2 += stack_velocity_x*d
    try:
        pygame.draw.rect(gameWindow, stack_color, [stack_x2, stack_y2, stack_l, stack_b])
    except ValueError:
        Validate()
        pygame.draw.rect(gameWindow, stack_color, [stack_x2, stack_y2, stack_l, stack_b])

    for stack in Tower:
        pygame.draw.rect(gameWindow, stack['color'], [stack['x'], stack['y'], stack['len'], stack_b])

def PlaceStack(d):
    "Places the stack and creates a new one"
    global placing, stack_x1, stack_x2, stack_y1, stack_y2, stack_l
    place_sound.play()
    placing = False
    cutoff = abs(stack_x1-stack_x2)
    temp_stack_l = stack_l
    temp_stack_x2 = stack_x2
    stack_l -= cutoff
    if stack_x2<stack_x1:
        stack_x3 = stack_x2
        stack_x2 = stack_x1
    else:
        stack_x3 = stack_x1+stack_l+cutoff
        stack_x1 = stack_x2
    Tower.append({'x':stack_x2, 'y':stack_y2, 'color':stack_color.copy(), 'len':stack_l})
    if cutoff:
        Vanishing.append({'x':stack_x3, 'y':stack_y2, 'color':stack_color.copy(), 'len':cutoff})
    if d==1:
        stack_x2 = screen_width
    else:
        stack_x2 = -stack_l
    UpdateColor()
    if stack_y2 < 200:
        PushDown()
    else:
        stack_y1 = stack_y2
    stack_y2 -= stack_b+20
    return temp_stack_l, temp_stack_x2

def Validate():
    "Validates the stack color and bring all the rgb code in 0, 255 range"
    global rgb
    for i in (0,1,2):
        if stack_color[i]<0:
            stack_color[i]=0
        elif stack_color[i]>255:
            stack_color[i]=255
    rgb += 1
    if rgb==6: rgb = 0

def UpdateColor(n = color_diff):
    "Changes the color of the stack"
    global stack_color
    for i in (0,1,2):
        stack_color[i] += n*ColorCode[rgb][i]

def ReverseColor(color):
    "Returns the reverse color code"
    return [255-i for i in color]

def Vanish():
    "Vanishes the cutoff parts of stacks"
    for stack in Vanishing:
        pygame.draw.rect(gameWindow, stack['color'], [stack['x'], stack['y'], stack['len'], stack_b])
        for j in (0,1,2):
            stack['color'][j] -= 5
            if stack['color'][j]<0: stack['color'][j] = 0
        if stack['color']==[0,0,0]:
            Vanishing.remove(stack)

def PushDown():
    "When the stacks are about to go off the screen, they get push down"
    for stack in Tower:
        stack['y'] += stack_b
    for stack in Vanishing:
        stack['y'] += stack_b
    Tower.pop(0)

def Start():
    "Welcome Screen with a play button"

    global rgb, stack_color, high_score
    rgb = randint(0,5)
    stack_color = Color_init[rgb]
    
    try:
        with open(score_file_path, 'rb') as f:
            high_score = pickle.load(f)
    except FileNotFoundError:
        with open(score_file_path, 'wb') as f:
            pickle.dump(high_score, f)
            high_score = 0

    intro_sound.play()
    text2 = "Created by Anubhav Jha"
    timer = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif (event.type == MOUSEBUTTONUP) or ((event.type == KEYUP) and event.key in (K_SPACE, K_RETURN)):
                if not Restart():
                    with open(score_file_path, 'wb') as f:
                        pickle.dump(high_score, f)
                    pygame.quit()
                    return False
            elif event.type == KEYUP and event.key==K_r and pygame.key.get_mods() in (64, 128):
                # Reset the high score
                if high_score > 0:
                    high_score = 0
                    with open(score_file_path, 'wb') as f:
                        pickle.dump(high_score, f)
                text2 = "High Score has been Reset"
                timer = 2*fps

        gameWindow.fill(black)
        for i, text1 in enumerate(('Welcome', '      To', '  Stacks')):
            try:
                Text = font1.render(text1, True, stack_color)
            except ValueError:
                Validate()
                Text = font1.render(text1, True, stack_color)
            gameWindow.blit(Text, (screen_width//2-200, screen_height//2-250+(i*100)))

        if timer > 0: timer -= 1
        else: text2 = "Created by Anubhav Jha"
        Text = font2.render(text2, True, ReverseColor(stack_color))
        gameWindow.blit(Text, (screen_width-300, screen_height-30))
        
        gameWindow.blit(play_image, (screen_width//2-110, screen_height//2+30))
        pygame.display.update()
        UpdateColor(5)
        clock.tick(fps)    

def Restart():
    "Drops a base"

    # Game specific variables
    global stack_x1, stack_y1, stack_l, score
    a = 1
    score = 0
    stack_l = 200
    stack_x1 = (screen_width-stack_l)//2
    stack_y1 = -stack_b
    Vanishing.clear()

    drop_sound.play()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
        gameWindow.fill(black)
        stack_y1 += 2*a
        a += 0.1
        if stack_y1>screen_height-stack_b:
            stack_y1 = screen_height-stack_b
        try:
            pygame.draw.rect(gameWindow, stack_color, [stack_x1, stack_y1, stack_l, stack_b])
        except ValueError:
            Validate()
            pygame.draw.rect(gameWindow, stack_color, [stack_x1, stack_y1, stack_l, stack_b])
        pygame.display.update()
        clock.tick(60)
        if stack_y1==screen_height-stack_b:
            break
    Tower.clear()
    Tower.append({'x':stack_x1, 'y':stack_y1, 'color':stack_color.copy(), 'len':stack_l})
    if GameLoop():
        a = 10
        y = 0
        game_over_sound.play()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return False
            gameWindow.fill(black)
            y += 1*a
            a -= 0.1
            if a<0: a = 0.1
            if y>screen_height-200:
                y = screen_height-200
                break
            gameWindow.blit(game_over_image, (screen_width//2-200, y))
            pygame.display.update()
            clock.tick(60)
        gameWindow.blit(game_over_image, (screen_width//2-200, y))
        gameWindow.blit(play_image, (screen_width//2-110, screen_height//2-150))
        gameWindow.blit(font2.render(f'High Score: {high_score}', True, white), (15,15))
        gameWindow.blit(font2.render(f'Score: {score}', True, white), (15,40))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return False
                elif (event.type == MOUSEBUTTONUP) or ((event.type == KEYUP) and event.key in (K_SPACE, K_RETURN)):
                    if not Restart(): return False

    pygame.quit()

# THE GAME LOOP
def GameLoop():

    # Game specific variables
    global stack_velocity_x, stack_velocity_y, stack_x2, stack_y2, placing, rgb, auto
    d = 1
    placing = False
    auto = False
    stack_x2, stack_y2 = screen_width-stack_l, stack_y1-stack_b-20
    game_over = False

    pygame.mixer.stop()
    pygame.mixer.music.load(bg_music)
    pygame.mixer.music.play(-1)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key in (K_RETURN, K_SPACE):
                    placing = True
                elif event.key == K_BACKSLASH:
                    auto = not(auto)
                elif event.key == K_UP:
                    stack_velocity_x = 50
                    stack_velocity_y = 20
                elif event.key == K_DOWN:
                    stack_velocity_x = 5
                    stack_velocity_y = 2
            elif event.type == MOUSEBUTTONDOWN:
                placing = True
        gameWindow.fill(black)
        if not game_over:
            if auto and abs(stack_x1-stack_x2)<=stack_velocity_x:
                stack_x2 = stack_x1
                placing = True      
            if stack_x2>screen_width-stack_l-10:
                d = -1
            elif stack_x2<10:
                d = 1
            gameWindow.fill(black)
            if Stack(d):
                game_over = True
        elif Vanishing == []:
            pygame.mixer.music.stop()
            return True
        else:
            Stack(d)

        Vanish()
        gameWindow.blit(font2.render(f'High Score: {high_score}', True, white), (15,15))
        gameWindow.blit(font2.render(f'Score: {score}', True, white), (15,40))
        pygame.display.update()
        clock.tick(fps)

Start()
