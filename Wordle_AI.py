import os
import random
import pandas as pd
import numpy as np
import pygame
import pygame.font
import torch
import torch.optim as optim
import torch.nn as nn
import seaborn as sns
import matplotlib.pyplot as plt
from DQN import DQNAgent
import statistics
from GPyOpt.methods import BayesianOptimization
#from bayesOpt import *
import datetime
import distutils.util
DEVICE = 'cpu'

#INITIALIZE VALUES
wordfile = open("wordle-answers-alphabetical.txt", "r")
words = wordfile.read()
words = words.split('\n')

pygame.font.init()
titleFont = pygame.font.Font(None, 100)
guessFont = pygame.font.Font(None, 75)
smallFont = pygame.font.Font(None, 32)
keyboardFont = pygame.font.Font(None, 25)

YELLOW = (181, 159, 59)
GREEN = (83, 141, 78)
DARK_GRAY = (58, 58, 60)
LIGHT_GRAY = (129, 131, 132)
WHITE = (255,255,255)
BLACK = (0,0,0)
BACKGROUND = (18, 18, 19)
COLOR_INACTIVE = DARK_GRAY
COLOR_ACTIVE = LIGHT_GRAY

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
GAME_WIDTH = 400 # was 500
GAME_X = (SCREEN_WIDTH - GAME_WIDTH) // 2

BOX_SIZE = 70 # was 85
BOX_MARGIN = (GAME_WIDTH - 5 * BOX_SIZE) // 4

WORDLE_Y = 30
GRID_Y = WORDLE_Y + 90
MSG_X = GAME_X
MSG_Y = GRID_Y + 6 * (BOX_SIZE + BOX_MARGIN) + 25
INPUTBOX_X = GAME_X
INPUTBOX_Y = MSG_Y + 50
INPUTBOX_WIDTH = 70
ERROR_X = GAME_X
ERROR_Y = INPUTBOX_Y + INPUTBOX_WIDTH + 25

KEY_SIZE = GAME_WIDTH // (10 + 9/4)
KEY_MARGIN =  KEY_SIZE // 4
KEY_Y = ERROR_Y + 50

x_pos = np.linspace(GAME_X, GAME_X + 4 * (BOX_SIZE + BOX_MARGIN), 5)
y_pos = np.linspace(GRID_Y, GRID_Y + 5 * (BOX_SIZE + BOX_MARGIN), 6)
boxes = np.empty((6, 5), dtype=object)
x_key_pos0 = np.linspace(GAME_X, GAME_X + 9 * (KEY_SIZE + KEY_MARGIN), 10)
x_key_pos1 = np.linspace(GAME_X + KEY_SIZE // 4, GAME_X + KEY_SIZE // 4 + 8 * (KEY_SIZE + KEY_MARGIN), 9)
x_key_pos2 = np.linspace(GAME_X + KEY_SIZE // 2, GAME_X + KEY_SIZE // 2 + 6 * (KEY_SIZE + KEY_MARGIN), 7)
y_key_pos = np.linspace(KEY_Y, KEY_Y + 2 * (KEY_SIZE + KEY_MARGIN), 3)

keys = []

qwerty = "qwertyuiopasdfghjklzxcvbnm"

wintxt = smallFont.render("Congrats, you got it.", True, WHITE)
losetxt = smallFont.render("Wow, you suck.", True, WHITE)
wordletxt = titleFont.render("Wordle", True, WHITE)
wordError = smallFont.render("Please guess a valid 5-letter word", True, WHITE)


def define_parameters():
    params = dict()
    # Neural Network
    params['epsilon_decay_linear'] = 1/100
    params['learning_rate'] = 0.00013629
    params['first_layer_size'] = 200    # neurons in the first layer
    params['second_layer_size'] = 20   # neurons in the second layer
    params['third_layer_size'] = 50    # neurons in the third layer
    params['episodes'] = 250
    params['memory_size'] = 2500
    params['batch_size'] = 1000
    # Settings
    params['weights_path'] = 'weights/weights.h5'
    params['train'] = False
    params["test"] = True
    params['plot_score'] = True
    params['log_path'] = 'logs/scores_' + str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) +'.txt'
    return params

#initialize game
class Game:
    """ Initialize PyGAME """

    def __init__(self, game_width, game_height):
        pygame.display.set_caption('Wordle')
        self.game_width = game_width
        self.game_height = game_height
        self.gameDisplay = pygame.display.set_mode([game_width, game_height])
        self.won = False
        self.lost = False



class letter_box:
    def __init__(self,
                screen,
                x,
                y,
                col,
                row,
                letter=None,
                color=DARK_GRAY):

        self.screen = screen
        self.x = x
        self.y = y
        self.col = col
        self.row = row
        self.letter = letter
        self.rect = self.draw(color)

    def draw(self, color):
        return pygame.draw.rect(self.screen,
                                color,
                                (self.x, self.y, BOX_SIZE, BOX_SIZE))

    def write(self, letter):
        self.letter = letter.upper()
        lettertxt = guessFont.render(self.letter, True, WHITE)
        text_rect = lettertxt.get_rect()
        self.screen.blit(lettertxt,
                        (self.x + (BOX_SIZE - text_rect.width) // 2, 15 + self.y))


class keyboard_letter:
    def __init__(self,
                screen,
                x,
                y,
                col,
                row,
                letter=None,
                color=DARK_GRAY):

        self.screen = screen
        self.x = x
        self.y = y
        self.col = col
        self.row = row
        self.letter = letter
        self.color = color
        self.rect = self.draw(color)

    def draw(self, color):
        if color == GREEN:
            self.color = GREEN
            return pygame.draw.rect(self.screen,
                                        color,
                                        (self.x, self.y, KEY_SIZE, KEY_SIZE))
        elif self.color != GREEN:
            return pygame.draw.rect(self.screen,
                                        color,
                                        (self.x, self.y, KEY_SIZE, KEY_SIZE))
    def write(self, letter):
        self.letter = letter.upper()
        lettertxt = keyboardFont.render(self.letter, True, WHITE)
        text_rect = lettertxt.get_rect()
        self.screen.blit(lettertxt,
                        (self.x + (KEY_SIZE - text_rect.width) // 2, 8 + self.y))

def update_screen():
    pygame.display.update()


#def initialize_game(wordlist, game, agent, batch_size):

def reset_display(screen, counter, streak, longeststreak, scores):
    screen.fill(BACKGROUND)
    screen.blit(wordletxt, (GAME_X, WORDLE_Y))
    gamecounter = smallFont.render("Game #: " + str(counter + 1), True, WHITE)
    streakcounter = smallFont.render("Streak: " + str(streak), True, WHITE)
    longstreakcounter = smallFont.render("Longest Streak: " + str(longeststreak), True, WHITE)
    guesscounter = smallFont.render("Guess history", True, WHITE)
    screen.blit(gamecounter, (SCREEN_WIDTH - GAME_X + BOX_MARGIN, WORDLE_Y))
    screen.blit(streakcounter, (SCREEN_WIDTH - GAME_X + BOX_MARGIN, WORDLE_Y+25))
    screen.blit(longstreakcounter, (SCREEN_WIDTH - GAME_X + BOX_MARGIN, WORDLE_Y+50))
    screen.blit(guesscounter, (SCREEN_WIDTH - GAME_X + BOX_MARGIN, WORDLE_Y+75))
    for n in range(len(scores)):
        if n < 6:
            scorecounter = smallFont.render(str(n+1) + ": " + str(scores[n]), True, WHITE)
        else:
            scorecounter = smallFont.render("Failures: " + str(scores[n]), True, WHITE)
        screen.blit(scorecounter, (SCREEN_WIDTH - GAME_X + BOX_MARGIN, WORDLE_Y+25*(n+4)))
    for x in range(5):
        for y in range(6):
            boxes[y][x] = letter_box(screen, x_pos[x], y_pos[y], x, y)

    for x in range(len(x_key_pos0)):
        keys.append(keyboard_letter(screen, x_key_pos0[x], y_key_pos[0], x, 0))
    for x in range(len(x_key_pos1)):
        keys.append(keyboard_letter(screen, x_key_pos1[x], y_key_pos[1], x, 1))
    for x in range(len(x_key_pos2)):
        keys.append(keyboard_letter(screen, x_key_pos2[x], y_key_pos[2], x, 2))

    for x in range(26):
        keys[x].write(qwerty[x])
    pygame.display.flip()

#start game

def run(params):
    """
    Run DQN algoritm
    """
    pygame.init()
    agent = DQNAgent(params)
    agent = agent.to(DEVICE)
    agent.optimizer = optim.Adam(agent.parameters(), weight_decay=0, lr=params['learning_rate'])
    counter_games = 0
    streak = 0
    longeststreak = 0
    scores = [0, 0, 0, 0, 0, 0, 0]
    while counter_games < params['episodes']:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        clock = pygame.time.Clock()
        input_box = pygame.Rect(GAME_X, INPUTBOX_Y, GAME_WIDTH, INPUTBOX_WIDTH)
        COLOR = COLOR_ACTIVE
        active = False
        text = ''
        n = 0
        winflag = 0
        loseflag = 0
        state = DQNAgent.initialize_state()
        random_word = words[random.randint(0, len(words))]
        print(random_word)
        reset_display(screen, counter_games, streak, longeststreak, scores)

        while winflag == 0 and loseflag == 0:
            while len(text) < 5:
                if not params['train']:
                    agent.epsilon = 0.01
                else:
                    # agent.epsilon is set to give randomness to actions
                    agent.epsilon = 1 - (counter_games * params['epsilon_decay_linear'])


                # perform random actions based on agent.epsilon, or choose the action
                if random.uniform(0, 1) < agent.epsilon:
                    move = text += qwerty[random.randint(0,len(qwerty))]
                else:
                    # predict action based on the old state
                    with torch.no_grad():
                        state_old_tensor = torch.tensor(state_old.reshape((1, 11)), dtype=torch.float32).to(DEVICE)
                        prediction = agent(state_old_tensor)
                        final_move = np.eye(3)[np.argmax(prediction.detach().cpu().numpy()[0])]

                # perform new move and get new state
                player1.do_move(final_move, player1.x, player1.y, game, food1, agent)
                state_new = agent.get_state(game, player1, food1)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN :
                    if event.key == pygame.K_RETURN:
                        user_guess = text.lower()
                        if user_guess not in words:
                            #draw error text
                            screen.blit(wordError, (ERROR_X, ERROR_Y))
                        else:
                            #draw over error text
                            pygame.draw.rect(screen, BACKGROUND, (ERROR_X, ERROR_Y, GAME_WIDTH, 40))
                            for i in range(len(user_guess)):
                                guess = user_guess[i]
                                correct = random_word[i]
                                box = boxes[n][i]
                                if guess not in random_word:
                                    box.draw(BLACK)
                                    keys[qwerty.index(guess)].draw(BLACK)
                                    keys[qwerty.index(guess)].write(guess)
                                else:
                                    correctlettercount = 0
                                    for k in range(i,5):
                                        if guess == user_guess[k] and user_guess[k] == random_word[k]:
                                            correctlettercount += 1
                                    if user_guess[0:i+1].count(guess) + correctlettercount <= random_word.count(user_guess[i]):
                                        box.draw(YELLOW)
                                        keys[qwerty.index(guess)].draw(YELLOW)
                                        keys[qwerty.index(guess)].write(guess)
                                    else:
                                        box.draw(BLACK)
                                if guess == correct:
                                    box.draw(GREEN)
                                    keys[qwerty.index(guess)].draw(GREEN)
                                    keys[qwerty.index(guess)].write(guess)
                                box.write(guess)
                            n += 1
                            if user_guess == random_word:
                                screen.blit(wintxt, (ERROR_X, ERROR_Y))
                                streak += 1
                                if streak > longeststreak:
                                    longeststreak = streak
                                scores[n-1] +=1
                                winflag = 1
                            elif n > 5:
                                screen.blit(losetxt, (ERROR_X, ERROR_Y))
                                streak = 0
                                scores[6] += 1
                                loseflag = 1
                        text = ''

                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif len(text) < 5:
                            text += event.unicode
                    # Re-render the text.

            # Render the current text
            pygame.draw.rect(screen,
                            COLOR,
                            input_box)
            txt_surface = guessFont.render(text.upper(), True, WHITE)
            text_rect = txt_surface.get_rect()
            # Blit the text
            screen.blit(txt_surface,
                        (input_box.x + (input_box.w - text_rect.width) // 2,
                        input_box.y + (input_box.h - text_rect.height) // 2 + 3))
            #text above guessbox
            msg = smallFont.render("Guess word #" + str(n+1) + ":", True, WHITE)
            pygame.draw.rect(screen, BACKGROUND, (MSG_X, MSG_Y, GAME_WIDTH, 40))
            screen.blit(msg, (MSG_X, MSG_Y))
            pygame.display.flip()
            clock.tick(30)

        counter_games += 1
def main():
    pygame.font.init()
    params = define_parameters()
    params['load_weights'] = False
    run(params)

# Done! Time to quit.
if __name__ == '__main__':
    main()
    pygame.quit()
