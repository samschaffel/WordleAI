import os
import random
import pandas as pd
import numpy as np
import pygame
import pygame.font
import torch

#initialize random word
# wordfile = open("WordList.txt", "r")
# words = wordfile.read()
# words = words.split(',')
# for n in range(len(words)):
#     words[n] = words[n].replace('"','')
# wordfile.close()

wordfile = open("wordle-answers-alphabetical.txt", "r")
words = wordfile.read()
words = words.split('\n')
random_word = words[random.randint(0, len(words))]
random_word = "green"
print(random_word)


#initialize game
pygame.init()
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

SCREEN_WIDTH = 700
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
qwerty = "qwertyuiopasdfghjklzxcvbnm"

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

#start game
def main():
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    screen.fill(BACKGROUND)
    clock = pygame.time.Clock()
    input_box = pygame.Rect(GAME_X, INPUTBOX_Y, GAME_WIDTH, INPUTBOX_WIDTH)
    COLOR = COLOR_INACTIVE
    active = False
    text = ''
    n = 0
    winflag = 0
    loseflag = 0

    wintxt = smallFont.render("Congrats, you got it.", True, WHITE)
    losetxt = smallFont.render("Wow, you suck.", True, WHITE)
    wordletxt = titleFont.render("Wordle", True, WHITE)
    wordError = smallFont.render("Please guess a valid 5-letter word", True, WHITE)
    screen.blit(wordletxt, (GAME_X, WORDLE_Y))
    x_pos = np.linspace(GAME_X, GAME_X + 4 * (BOX_SIZE + BOX_MARGIN), 5)
    y_pos = np.linspace(GRID_Y, GRID_Y + 5 * (BOX_SIZE + BOX_MARGIN), 6)
    boxes = np.empty((6, 5), dtype=object)
    for x in range(5):
        for y in range(6):
            boxes[y][x] = letter_box(screen, x_pos[x], y_pos[y], x, y)


    x_key_pos0 = np.linspace(GAME_X, GAME_X + 9 * (KEY_SIZE + KEY_MARGIN), 10)
    x_key_pos1 = np.linspace(GAME_X + KEY_SIZE // 4, GAME_X + KEY_SIZE // 4 + 8 * (KEY_SIZE + KEY_MARGIN), 9)
    x_key_pos2 = np.linspace(GAME_X + KEY_SIZE // 2, GAME_X + KEY_SIZE // 2 + 6 * (KEY_SIZE + KEY_MARGIN), 7)
    y_key_pos = np.linspace(KEY_Y, KEY_Y + 2 * (KEY_SIZE + KEY_MARGIN), 3)

    # keys = np.empty((26,1), dtype=object)
    # for x in range(len(x_key_pos0)):
    #     keys[x] = keyboard_letter(screen, x_key_pos0[x], y_key_pos[0], x, 0)
    # for x in range(len(x_key_pos1)):
    #     keys[x + len(x_key_pos0)] = keyboard_letter(screen, x_key_pos1[x], y_key_pos[1], x, 1)
    # for x in range(len(x_key_pos2)):
    #     keys[x + len(x_key_pos0) + len(x_key_pos1)] = keyboard_letter(screen, x_key_pos2[x], y_key_pos[2], x, 2)
    #
    # for x in range(26):
    #     keys[x].draw(GREEN)
    keys = []
    for x in range(len(x_key_pos0)):
        keys.append(keyboard_letter(screen, x_key_pos0[x], y_key_pos[0], x, 0))
    for x in range(len(x_key_pos1)):
        keys.append(keyboard_letter(screen, x_key_pos1[x], y_key_pos[1], x, 1))
    for x in range(len(x_key_pos2)):
        keys.append(keyboard_letter(screen, x_key_pos2[x], y_key_pos[2], x, 2))

    for x in range(26):
        keys[x].write(qwerty[x])
    pygame.display.flip()
    running = True
    # Run until the user asks to quit
    while running:
        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current COLOR of the input box.
                COLOR = COLOR_ACTIVE if active else COLOR_INACTIVE
            if event.type == pygame.KEYDOWN and winflag == 0 and loseflag == 0:
                if active:
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
                                if guess == correct:
                                    box.draw(GREEN)
                                    keys[qwerty.index(guess)].draw(GREEN)
                                    keys[qwerty.index(guess)].write(guess)
                                box.write(guess)
                            n += 1
                            if user_guess == random_word:
                                screen.blit(wintxt, (ERROR_X, ERROR_Y))
                                winflag = 1                            
                            elif n > 5:
                                screen.blit(losetxt, (ERROR_X, ERROR_Y))
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

# Done! Time to quit.
if __name__ == '__main__':
    main()
    pygame.quit()
