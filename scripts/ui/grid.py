# Créé par tkmer, le 28/01/2023 en Python 3.77
import pygame, sys
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

def grid(size,color):
    screenWidth=screen.get_size()[0]
    screenHeight=screen.get_size()[1]
    for x in range(0,screenWidth,size-1):
        for y in range(0,screenHeight,size-1):
            pygame.draw.rect(screen,color,((x,y),(size,size)),1)
