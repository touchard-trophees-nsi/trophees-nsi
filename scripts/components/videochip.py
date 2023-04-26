import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape

# printed circuit board
class VideoChip(Shape):
    def __init__(self,pos,size=Vector2(80,40),color=(15,15,15),form="square",direc=0):
        super().__init__(pos,size,color,form,direc)

    def draw(self,screen):
        Shape.draw(self,screen)
        Shape.draw_connections(self,screen,extra=(1,0))

    def get_type(self):
        return 'Shape.VideoChip'