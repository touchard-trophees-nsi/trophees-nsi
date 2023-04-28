import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape

# printed circuit board
class Microcontroller(Shape):
    def __init__(self,pos,size=Vector2(80,40),color=(80,80,80),form="square",direc=0):
        super().__init__(pos,size,color,form,direc,showWhenRunning=False)
        self.id = 'MicroController'

    def draw(self,screen):
        Shape.draw(self,screen)
        Shape.draw_connections(self,screen,extra=(1,0))

    def get_showWhenRunning(self):
        return False

    def get_type(self):
        return 'Shape.Microcontroller'