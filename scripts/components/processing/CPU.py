import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape

class CPU(Shape):
    def __init__(self,pos,size=Vector2(80,80),color=(30,30,30),form="square",direc=0):
        super().__init__(pos,size,color,form,direc,showWhenRunning=False,code_content=[''])
        self.id = 'CPU'
        self.set_code([''])

    def draw(self,screen):
        Shape.draw(self,screen)
        Shape.draw_connections(self,screen)

    def get_showWhenRunning(self):
        return False
        
    def get_type(self):
        return 'Shape.CPU'