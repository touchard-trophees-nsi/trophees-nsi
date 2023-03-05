import pygame
from scripts.math.vector2 import Vector2
from scripts.cursor import cursor
from scripts.ui.selectable import Selectable
from scripts.graphics.color import RGB

class MoveableElement(Selectable):
    def __init__(self,pos,size,color):
        super().__init__(pos,size,idleColor=color)
        self.pos,self.size = pos,size
        self.FirstClickPos = Vector2.ZERO()

    def update(self,shapes):
        self.base_update()
        self.update_pos(shapes)

    def update_pos(self,shapes):
        self.shapes = shapes
        if self.continousClick:
            if self.FirstClickPos == Vector2.ZERO():
                self.FirstClickPos = Vector2(self.pos.x-cursor.pos.x, self.pos.y-cursor.pos.y)
            nshape = self.nearest(shapes,60)
        else:
            self.FirstClickPos = Vector2.ZERO()
        if self.FirstClickPos != Vector2.ZERO():
            self.pos = Vector2(cursor.pos.x+self.FirstClickPos.x, cursor.pos.y+self.FirstClickPos.y)

    def onRelease(self):
        nshape = self.nearest(self.shapes,60)
        if nshape != None:
            vectdiff = nshape.pos - self.pos
            if vectdiff.x < 0 and -min(nshape.size.y,self.size.y)//2 < vectdiff.y < min(nshape.size.y,self.size.y)//2:
                self.pos = Vector2(nshape.pos.x + self.size.x , nshape.pos.y)
            elif vectdiff.x > 0 and -min(nshape.size.y,self.size.y)//2 < vectdiff.y < min(nshape.size.y,self.size.y)//2:
                self.pos = Vector2(nshape.pos.x - self.size.x, nshape.pos.y)
            elif vectdiff.y < 0:
                self.pos = Vector2(nshape.pos.x, nshape.pos.y + self.size.y)
            elif vectdiff.y > 0:
                self.pos = Vector2(nshape.pos.x, nshape.pos.y - self.size.y)
        gridspacing = 60 # Valeur actuelle de l'espacement des lignes de la grille
        self.pos.x -= self.pos.x % gridspacing
        self.pos.y -= self.pos.y % gridspacing
    
    def nearest(self,shapeslist,radius=50):
        nearestshape,distance = None,radius+1
        for shape in shapeslist:
            if shape != self:
                length = ((shape.pos.x - self.pos.x)**2+(shape.pos.y - self.pos.y)**2)**0.5
                if length < distance:
                    nearestshape,distance = shape,length
        return nearestshape


class Shape(MoveableElement):
    def __init__(self,pos,size,color=(100,0,0)) -> None:
        color = RGB(color)
        super().__init__(pos,size,color)
        self.pos,self.size,self.color = pos,size,color
        self.isLocked = False
        self.draggingPanel = False
        self.FirstClickPos = Vector2.ZERO()

    def draw(self,screen):
        pygame.draw.rect(screen, self.color.value, (self.pos.x, self.pos.y, self.size.x, self.size.y))
