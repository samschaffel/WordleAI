import os
import random
import pandas as pd
import numpy as np
import pygame
import pygame.font

#initialize random word
wordfile = open("wordle-answers-alphabetical.txt", "r")
words = wordfile.read()
words = words.split('\n')
random_word = words[random.randint(0, len(words))]
#print(random_word)

#initialize game
pygame.init()
# Set up the drawing window
screenWidth = 700
screenHeight = 1000
titleFont = pygame.font.Font(None, 100)
guessFont = pygame.font.Font(None, 75)
smallFont = pygame.font.Font(None, 32)
YELLOW = (181, 159, 59)
GREEN = (83, 141, 78)
DARK_GRAY = (58, 58, 60)
LIGHT_GRAY = (129, 131, 132)
WHITE = (255,255,255)
BACKGROUND = (18, 18, 19)
COLOR_INACTIVE = DARK_GRAY
COLOR_ACTIVE = LIGHT_GRAY
BOX_SIZE = 75
INPUT_WIDTH = 500

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
        


#start game
def main():
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    # Fill the background with black
    screen.fill(BACKGROUND)
    clock = pygame.time.Clock()
    input_box = pygame.Rect((screenWidth - INPUT_WIDTH) // 2, 800, INPUT_WIDTH, 75)
    COLOR = COLOR_INACTIVE
    active = False
    text = ''
    n = 0

    wordletxt = titleFont.render("Wordle", True, (255,255,255))
    wordError = smallFont.render("Please guess a valid 5-letter word", True, (255,255,255))
    screen.blit(wordletxt, (100,20))
    x_pos = np.arange(100, 600, 100)
    y_pos = np.arange(100, 700, 100)
    boxes = np.empty((6, 5), dtype=object)
    for x in range(5):
        for y in range(6):
            boxes[y][x] = letter_box(screen, x_pos[x], y_pos[y], x, y)

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
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        user_guess = text.lower()
                        if user_guess not in words:
                            #draw error text
                            screen.blit(wordError, (100,900))
                        else:
                            #draw over error text
                            pygame.draw.rect(screen, BACKGROUND, (100, 900, 500, 40))

                            for i in range(len(user_guess)):
                                guess = user_guess[i]
                                box = boxes[n][i]
                                if guess in random_word:
                                    box.draw(YELLOW)
                                if guess == random_word[i]:
                                    box.draw(GREEN)
                                box.write(guess)
                            n += 1
                        text = ''

                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        if len(text) < 5:
                            text += event.unicode
                    # Re-render the text.

        # Render the current text.
        pygame.draw.rect(screen, 
                        COLOR, 
                        input_box)
        txt_surface = guessFont.render(text.upper(), True, WHITE)
        text_rect = txt_surface.get_rect()
        # Blit the text
        screen.blit(txt_surface, 
                    (input_box.x + (input_box.w - text_rect.width) // 2, 
                    input_box.y + (input_box.h - text_rect.height) // 2 + 3))
        # Blit the input_box rect.
        #pygame.draw.rect(screen, COLOR, input_box, 2)
        #text above guessbox
        guesstxt = smallFont.render("Guess word #" + str(n+1) + ":", True, WHITE)
        pygame.draw.rect(screen, BACKGROUND, (100, 750, 500, 40))
        screen.blit(guesstxt, (100,750))

        pygame.display.flip()
        clock.tick(30)


# Done! Time to quit.
if __name__ == '__main__':
    main()
    pygame.quit()
