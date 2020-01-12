import random, pygame, sys
from pygame.locals import *
import numpy as np
import time
import utils
import os


FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
HIGHSCORE = 0
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

'''     COLOR SCHEME    '''
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
BLUE      = (0,     0, 255)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HEAD = 0    # index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def logHighSCore(score):
    print '\033[1m****\033[31m<-{ NEW HIGH SCORE }->\033[0m\033[1m****\033[0m'
    user = raw_input('Enter Name: ')
    open('snek_score.txt', 'wb').write('%d\t%s' % (score, user))


def runGame():

    # Keep Track of HighScore
    if os.path.isfile('snek_score.txt'):
        high_score = int(utils.swap('snek_score.txt', False).pop().split('\t')[0])
    else:
        open('high_score.txt', 'wb').write('0\tNo One')
        high_score = 0

    tic = time.time()

    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True: # main game loop
        score = len(wormCoords) - 3
        for event in pygame.event.get():    # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            if score > high_score:
                showHighScoreScreen()
                logHighSCore(score)
                DISPLAYSURF.fill(BGCOLOR)
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                if score > high_score:
                    showHighScoreScreen()
                    logHighSCore(score)
                    DISPLAYSURF.fill(BGCOLOR)
                return # game over

        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation() # set a new apple somewhere
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        # MOVE APPLE!
        x = apple['x']
        y = apple['y']
        moves = {1: [x-1, y-1], 2: [x, y-1], 3: [x+1, y-1],
                 4: [x-1,   y], 5: [x, y],   6: [x+1,   y],
                 7: [x-1, y+1], 8: [x, y+1], 9: [x+1, y+1]}
        moved = False
        while not moved:
            new_pos = moves[np.random.randint(1,9,1)[0]]
            if 0<new_pos[0] < CELLWIDTH and 0<new_pos[1] < CELLHEIGHT:
                apple['y'] = new_pos[1]
                apple['x'] = new_pos[0]
                moved = True
            else:
                # Start the apple in a random place.
                apple = getRandomLocation()
        drawApple(apple)

        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def drawScore(score):
    # Keep Track of HighScore
    if os.path.isfile('snek_score.txt'):
        highest = int(utils.swap('snek_score.txt', False).pop().split('\t')[0])
    else:
        open('snek_score.txt', 'wb').write('0\tNo One')
        highest = 0
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    bestSurf = BASICFONT.render('High Score: %d' % (highest), True, BLUE)
    bestRect = bestSurf.get_rect()
    bestRect.topleft = (WINDOWWIDTH - 420, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)
    DISPLAYSURF.blit(bestSurf, bestRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    fonts = [pygame.font.Font('freesansbold.ttf',  90),
             pygame.font.Font('freesansbold.ttf', 100),
             pygame.font.Font('freesansbold.ttf', 110),
             pygame.font.Font('freesansbold.ttf', 120),
             pygame.font.Font('freesansbold.ttf', 130),
             pygame.font.Font('freesansbold.ttf', 140),
             pygame.font.Font('freesansbold.ttf', 150),
             pygame.font.Font('freesansbold.ttf', 160)]

    size_loop = 0
    while True:
        try:
            DISPLAYSURF.fill(BGCOLOR)
            if size_loop % 2 == 0:
                titleSurface = fonts[size_loop].render('sn3k', True, GREEN)
            else:
                titleSurface = fonts[size_loop].render('SN3K', True, WHITE)
            surf = pygame.transform.rotate(titleSurface, 0)
            titleRect = titleSurface.get_rect()
            titleRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
            DISPLAYSURF.blit(surf, titleRect)
            drawPressKeyMsg()
            if checkForKeyPress():
                pygame.event.get()  # clear event queue
                return

            pygame.display.update()
            FPSCLOCK.tick(FPS)
            size_loop += 1
        except IndexError:
            size_loop = 0


def showHighScoreScreen():
    highScoreFont = pygame.font.Font('freesansbold.ttf', 100)
    topSurf = highScoreFont.render('NEW HIGH', True, RED)
    lowSurf = highScoreFont.render(' SCORE', True, RED)
    topRect = topSurf.get_rect()
    lowRect = lowSurf.get_rect()
    topRect.midtop = (WINDOWWIDTH/2, 50)
    lowRect.midtop = (WINDOWWIDTH/2, topRect.height + 35)
    DISPLAYSURF.blit(topSurf, topRect)
    DISPLAYSURF.blit(lowSurf, lowRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def terminate():
    pygame.quit()
    sys.exit()


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


if __name__ == '__main__':
    main()
