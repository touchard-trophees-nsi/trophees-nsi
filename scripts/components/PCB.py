import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape
from scripts.dev import dprint
# printed circuit board
class PCB(Shape):
    def __init__(self,pos,size=Vector2(301,481),color=(0,70,30),form="square",direc=0):
        super().__init__(pos,size,color,form,direc)
        self.attached_comps = []
    
    def update(self,shapes):
        Shape.update(self, shapes)
        
        self.attached_comps = []
        for shape in shapes:
            if shape != self and shape.parent == self:
                self.attached_comps.append(shape)
                if not shape.dragging:
                    shape.pos = self.pos+shape.parent_offset
        
    
    def draw(self,screen):
        Shape.draw(self, screen)

    def get_type(self):
        return 'Shape.PCB'