import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape

# printed circuit board
class PCB(Shape):
    def __init__(self,pos,size=Vector2(181,241),color=(0,70,30),form="square",direc=0):
        super().__init__(pos,size,color,form,direc)

    def get_type(self):
        return 'Shape.PCB'