import pygame
from scripts.math.vector2 import Vector2
from scripts.cursor import cursor

class Moveable_element:
    def __init__(self,pos):
        self.pos = pos

    def update(self):
        if cursor.pos.x>self.pos.x and cursor.pos.x<self.pos.x+self.size.x and cursor.pos.y>self.pos.y and cursor.pos.y<self.pos.y+self.size.y and not self.isLocked and cursor.selectedElement==None or cursor.selectedElement==self:
            if cursor.eventType=='left':
                cursor.selectedElement = self
                self.draggingPanel = True
                if self.barFirstClickPos == Vector2.ZERO():
                        self.barFirstClickPos = Vector2(self.pos.x-cursor.pos.x, self.pos.y-cursor.pos.y)
            else:
                cursor.selectedElement = None
                self.barFirstClickPos = Vector2.ZERO()

        if self.barFirstClickPos != Vector2.ZERO():
            self.pos = Vector2(cursor.pos.x+self.barFirstClickPos.x, cursor.pos.y+self.barFirstClickPos.y)
    """
    def nearest(self,radius):
        nearestshape,distance = None,radius+1
        for shape in shapes:
            if (shape.pos - self.pos).normalize() < distance:
                nearestshape,distance = shape,(shape.pos - self.pos).normalize()
        return nearestshape"""


class Shape(Moveable_element):
    def __init__(self,pos,size,color=(100,0,0)) -> None:
        super().__init__(pos)
        self.pos,self.size,self.color = pos,size,color
        self.isLocked = False
        self.draggingPanel = False
        self.barFirstClickPos = Vector2.ZERO()

    def draw(self,screen):
        pygame.draw.rect(screen, self.color, (self.pos.x, self.pos.y, self.size.x, self.size.y))
    
class Group:
    pass

