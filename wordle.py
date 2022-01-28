import os
import random
import pandas as pd
import numpy as np
import pygame
import pygame.font

pygame.init()
# Set up the drawing window
screenWidth = 700
screenHeight = 1000
screen = pygame.display.set_mode([screenWidth, screenHeight])

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(500, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)




wordfile = open("wordle-answers-alphabetical.txt", "r")
words = wordfile.read()
words = words.split('\n')

random_word = words[random.randint(0, len(words))]
print(random_word)



# Run until the user asks to quit

def main():
    clock = pygame.time.Clock()
    input_box = InputBox(100, 800, 600, 75)
    # Fill the background with black
    screen.fill((0, 0, 0))

    titleFont = pygame.font.Font(None, 100)
    guessFont = pygame.font.Font(None, 75)
    wordletxt = titleFont.render("Wordle", True, (255,255,255))
    screen.blit(wordletxt, (100,20))
    for x in np.arange(100, 600, 100):
        for y in np.arange(100, 600, 100):
            pygame.draw.rect(screen, (64, 64, 64), (x, y, 75, 75))

    pygame.display.flip()
    running = True
    while running:

        # Did the user click the window close button?

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            input_box.handle_event(event)

        input_box.update()

        input_box.draw(screen)

        pygame.display.flip()
        clock.tick(30)


        # Flip the display
        #pygame.display.flip()

# Done! Time to quit.
if __name__ == '__main__':
    main()
    pygame.quit()


for n in range(6):
    while(True):
        message = "Guess word " + str(n+1) + ":"
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
