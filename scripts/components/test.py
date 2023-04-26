import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape

# printed circuit board
class TestShape(Shape):
    def __init__(self,pos,size=Vector2(80,80),color=(255,0,0),form="square",direc=0):
        super().__init__(pos,size,color,form,direc)

    def draw(self,screen):
        Shape.draw(self,screen)
        Shape.draw_connections(self,screen)

    def get_type(self):
        return 'Shape.PCB'