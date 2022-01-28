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
print(random_word)

#initialize game
pygame.init()
# Set up the drawing window
screenWidth = 700
screenHeight = 1000
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
YELLOW = (255, 255, 0)
GREEN = (0,255,0)
BOX_SIZE = 75

class letter_box:
    def __init__(self,
                screen,
                x,
                y,
                col,
                row,
                letter=None,
                color=COLOR_INACTIVE):
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


#start game
def main():
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    # Fill the background with black
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()
    titleFont = pygame.font.Font(None, 100)
    guessFont = pygame.font.Font(None, 75)
    smallFont = pygame.font.Font(None, 32)
    input_box = pygame.Rect(100, 800, 600, 75)
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
                        user_guess = text
                        if user_guess not in words:
                            #draw error text
                            screen.blit(wordError, (100,900))
                        else:
                            #draw over error text
                            pygame.draw.rect(screen, (0,0,0), (100, 900, 500, 40))


                            for i in range(len(user_guess)):
                                if user_guess[i] in random_word:
                                    correctlettercount = 0
                                    for k in range(i,5):
                                        if user_guess[i] == user_guess[k] and user_guess[k] == random_word[k]:
                                            correctlettercount += 1
                                            boxes[n][k].draw(GREEN)
                                    if user_guess[0:i+1].count(user_guess[i]) + correctlettercount <= random_word.count(user_guess[i]):
                                        print("ROW", n)
                                        boxes[n][i].draw(YELLOW)
                                        print(n, i, boxes[n][i].x, boxes[n][i].y)


                                lettertxt = guessFont.render(user_guess[i], True, (255,255,255))
                                screen.blit(lettertxt,(20 + 100*(i+1), 15 + 100*(n+1)))
                            n = n + 1
                        text = ''

                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                    # Re-render the text.

        # Render the current text.
        pygame.draw.rect(screen, (128, 128, 128), (100, 800, 500, 75))
        txt_surface = guessFont.render(text, True, COLOR)
        # Resize the box if the text is too long.
        width = max(500, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        #pygame.draw.rect(screen, COLOR, input_box, 2)
        #text above guessbox
        guesstxt = smallFont.render("Guess word #" + str(n+1) + ":", True, (255,255,255))
        pygame.draw.rect(screen, (0,0,0), (100, 750, 500, 40))
        screen.blit(guesstxt, (100,750))

        pygame.display.flip()
        clock.tick(30)


# Done! Time to quit.
if __name__ == '__main__':
    main()
    pygame.quit()
