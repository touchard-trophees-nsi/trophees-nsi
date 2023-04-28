import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape
from scripts.dev import dprint
from scripts.cursor import cursor
from scripts.parser.pseudocode import get_game_state
from scripts.graphics.color import RGB

# printed circuit board
class PCB(Shape):
    def __init__(self,pos,size=Vector2(301,481),color=RGB(0,70,30),form="square",direc=0):
        super().__init__(pos,size,color,form,direc,showWhenRunning=True)
        self.attached_comps = []
        self.id = 'PCB'
        self.base_color = color
        self.displayColor = (150,150,150)

    def update(self,shapes):
        Shape.update(self, shapes)
        
        self.attached_comps = []
        for shape in shapes:
            if shape != self and shape.parent == self:
                self.attached_comps.append(shape)
                if not shape.dragging:
                    shape.pos = self.pos+shape.parent_offset
         
    def draw(self,screen):
        self.color = RGB(*self.displayColor) if get_game_state() else self.base_color
        Shape.draw(self, screen)

    def get_showWhenRunning(self):
        return True

    def get_type(self):
        return 'Shape.PCB'