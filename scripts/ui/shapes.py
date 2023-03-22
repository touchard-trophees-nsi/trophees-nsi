import pygame
from scripts.math.vector2 import Vector2
from scripts.cursor import cursor
from scripts.ui.selectable import Selectable
from scripts.graphics.color import RGB

class MoveableElement(Selectable):
    def __init__(self,pos,size,color):
        super().__init__(pos,size,idleColor=color)
        self.pos,self.lastpos,self.size = pos,pos,size
        self.FirstClickPos = Vector2.ZERO()

    def update(self,shapes):
        self.base_update()
        self.update_pos(shapes)

    def update_pos(self,shapes):
        self.shapes = shapes
        if self.continousClick:
            if self.FirstClickPos == Vector2.ZERO():
                self.FirstClickPos = Vector2(self.pos.x-cursor.pos.x, self.pos.y-cursor.pos.y)
            #nshape = self.nearest(shapes,60)
        else:
            self.FirstClickPos = Vector2.ZERO()
        if self.FirstClickPos != Vector2.ZERO():
            self.pos = Vector2(cursor.pos.x+self.FirstClickPos.x, cursor.pos.y+self.FirstClickPos.y)
    """
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
    def onRelease(self):
        gp = 60 # Valeur actuelle de l'espacement des lignes de la grille
        if True: #[c'est possible de lacher la pièce]:
            diffx = self.pos.x % gp
            self.pos.x -= diffx if diffx<gp//2 else diffx-60
            diffy = self.pos.y % gp
            self.pos.y -= diffy if diffy<gp//2 else diffy-60
        else:
            self.pos = self.lastpos
        
        """
        
    def onRelease(self):
        if self.placeavail(): #[c'est possible de lacher la pièce]:
            self.pos.x,self.pos.y = self.posgrid()
        else:
            self.pos = self.lastpos
    def posgrid(self):
        gp = 60 # Valeur actuelle de l'espacement des lignes de la grille
        diffx = self.pos.x % gp
        posx = self.pos.x - (diffx if diffx<gp//2 else diffx-60)
        diffy = self.pos.y % gp
        posy = self.pos.y - (diffy if diffy<gp//2 else diffy-60)
        return posx,posy

    def placeavail(self):
        posalign = self.posgrid()
        for i in range(len(self.shapes)):
            if (self.shapes[i].pos.x,self.shapes[i].pos.y) == posalign and self.shapes[i] != self:
                return False
        return True

    def onClick(self):
        self.lastpos = self.pos
    
    """def nearest(self,shapeslist,radius=50):
        nearestshape,distance = None,radius+1
        for shape in shapeslist:
            if shape != self:
                length = ((shape.pos.x - self.pos.x)**2+(shape.pos.y - self.pos.y)**2)**0.5
                if length < distance:
                    nearestshape,distance = shape,length
        return nearestshape"""

class Shape(MoveableElement):
    def __init__(self,pos,size=Vector2(60,60),color=(100,0,0),form="square",direc=0) -> None:
        if type(color) == tuple: color = RGB(color)
        super().__init__(pos,size,color)
        self.pos,self.size,self.color = pos,size,color
        self.isLocked = False
        self.draggingPanel = False
        self.FirstClickPos = Vector2.ZERO()
        self.form = form
        self.direction = direc

    def draw(self,screen):
        if self.continousClick and self.placeavail():
            pygame.draw.rect(screen, (180,180,180), (self.posgrid()[0]+2, self.posgrid()[1]+2, self.size.x-4, self.size.y-4), 2,10)
        if self.form == "square":
            pygame.draw.rect(screen, self.color.value, (self.pos.x, self.pos.y, self.size.x, self.size.y))
        elif self.form == "triangle":
            pygame.draw.polygon(screen, self.color.value, [(self.pos.x, self.pos.y), (self.pos.x + self.size.x, self.pos.y), (self.pos.x, self.size.y + self.pos.y),(self.pos.x + self.size.x, self.size.y + self.pos.y),(self.pos.x, self.pos.y), (self.pos.x + self.size.x, self.pos.y)][self.direction:self.direction+3], 0)
        elif self.form == "circle":
            pygame.draw.circle(screen, self.color.value, ((self.pos.x+self.size.x,self.pos.x)[self.direction%2], (self.pos.y+self.size.y,self.pos.y)[self.direction//2]), self.size.x, 0, draw_top_left=(True,False,False,False)[self.direction],draw_top_right=(False,True,False,False)[self.direction],draw_bottom_left=(False,False,True,False)[self.direction],draw_bottom_right=(False,False,False,True)[self.direction])
        
    def copy(self):
        return Shape(self.pos,self.size,self.color,self.form,self.direction)

    def __eq__(self,object):
        if isinstance(object, Shape):
            return self.pos.x == object.pos.x and self.pos.y == object.pos.y and self.size == object.size


        """
        1 | pos.x, pos.y                    | pos.x + size.x, pos.y          | pos.x, pos.y + size.y          |
        2 | pos.x, pos.y                    | pos.x + size.x, pos.y          | pos.x + size.x, pos.y + size.y |
        3 | pos.x, pos.y                    | pos.x + size.x, pos.y + size.y | pos.x, pos.y + size.y          |
        0 | pos.x + size.x, pos.y + size.y  | pos.x + size.x, pos.y          | pos.x, pos.y + size.y          |

        1 | pos.x + size.x, pos.y + size.y |  draw_top_left=True  | draw_top_right=False | draw_bottom_right=False | draw_bottom_left=False |
        2 | pos.x         , pos.y + size.y |  draw_top_left=False | draw_top_right=True  | draw_bottom_right=False | draw_bottom_left=False |
        3 | pos.x + size.x, pos.y          |  draw_top_left=False | draw_top_right=False | draw_bottom_right=True  | draw_bottom_left=False |
        0 | pos.x         , pos.y          |  draw_top_left=False | draw_top_right=False | draw_bottom_right=False | draw_bottom_left=True  |
        """

"""
µ to do : 
- supp double item st incorrc place
- bin
µ done:
- better approximation when release
- circular shapes
- when release to an impossible place => return to the initial position
- shapes drawer adding forms
- ghost shape
    """