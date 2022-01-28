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

#start game
def main():
    screen = pygame.display.set_mode([screenWidth, screenHeight])
    # Fill the background with black
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()
    COLOR_INACTIVE = pygame.Color('lightskyblue3')
    COLOR_ACTIVE = pygame.Color('dodgerblue2')
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
    for x in np.arange(100, 600, 100):
        for y in np.arange(100, 700, 100):
            pygame.draw.rect(screen, (64, 64, 64), (x, y, 75, 75))

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
                                    pygame.draw.rect(screen, (255,255,0), (100*(i+1), 100*(n+1), 75, 75))
                                if user_guess[i] == random_word[i]:
                                    pygame.draw.rect(screen, (0,255,0), (100*(i+1), 100*(n+1), 75, 75))
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


for n in range(6):
    while(True):
        message = "Guess word #" + str(n+1) + ":"
        user_guess = input(message)
        print("Your guess is: " + user_guess)
        if user_guess not in words:
            print("Please guess a valid 5-letter word")
        else:
            break
    if user_guess == random_word:
        print("correct")
        break
    else:
        for i in range(len(user_guess)):
            if user_guess[i] in random_word:
                print("The correct word contains " + user_guess[i])
            if user_guess[i] == random_word[i]:
                print(user_guess[i] + " is in the correct position")
