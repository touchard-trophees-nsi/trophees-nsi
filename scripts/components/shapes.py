import pygame
from scripts.math.vector2 import Vector2
from scripts.cursor import cursor
from scripts.ui.selectable import Selectable
from scripts.graphics.color import RGB
from scripts.version import PYGAME_IS_MODERN_VERSION
from scripts.dev import dprint

GRID_WIDTH = 60

class MoveableElement(Selectable):
    def __init__(self,pos,size,color):
        super().__init__(pos,size,idleColor=color,hoveredColor=color,selectedColor=color)
        self.pos,self.lastpos,self.size = pos,pos,size
        self.FirstClickPos = Vector2.ZERO()
        self.dragging = False
        self.taken_space = Vector2((self.width)//(GRID_WIDTH+1) + 1, (self.height)//(GRID_WIDTH+1) + 1)
        self.start_pos = Vector2(int(((self.taken_space.x*GRID_WIDTH)-self.width)/2), int(((self.taken_space.y*GRID_WIDTH)-self.height)/2))
        #
        self.parent = None
        self.parent_offset = Vector2(0,0)

    def get_rect(self):
        return pygame.Rect(self.start_pos.x+self.pos.x, self.start_pos.y+self.pos.y, self.width, self.height)

    def set_parent(self,parent):
        self.parent = parent
        self.parent_offset = self.pos-self.parent.pos if parent else Vector2(0,0)
    
    def update(self,shapes):
        self.base_update()

    def update_pos(self,shapes):
        self.shapes = shapes
        # Gestion du déplacement des éléments
        if self.dragging:
            cursor.selectedElement = self
        if cursor.pos.x>=self.start_pos.x+self.pos.x and cursor.pos.x<=self.start_pos.x+self.pos.x+self.width and cursor.pos.y>=self.start_pos.y+self.pos.y and cursor.pos.y<=self.start_pos.y+self.pos.y+self.height and not self.isFrozen:
            self.isHovered = True
            if cursor.eventType=='left' and (cursor.selectedElement == None or cursor.selectedElement == self):
                for shape in shapes:
                    if shape != self and shape.dragging:
                        break
                else:
                    self.dragging = True

                    if self.FirstClickPos == Vector2.ZERO():
                        self.FirstClickPos = Vector2(self.pos.x-cursor.pos.x, self.pos.y-cursor.pos.y)

                    if cursor.selectedElement==None: self.lastpos = self.pos
                    cursor.selectedElement = self

                    # layer management
                    shapes.remove(self)
                    if 'PCB' in self.get_type():
                        shapes.insert(0, self)
                    else:
                        shapes.append(self)
            else:
                self.dragging = False
                self.FirstClickPos = Vector2.ZERO()
        else:
            self.isHovered = False

        if not self.dragging and cursor.selectedElement==self:
            if self.placeavail()[0]:
                self.pos.x,self.pos.y = self.posgrid()
                
                # PCB attaching
                if self.placeavail()[1]: 
                    self.set_parent(self.placeavail()[1])
                else:
                    self.set_parent(None)
            else:
                self.pos = self.lastpos

        if self.FirstClickPos != Vector2.ZERO():
            self.pos = Vector2(cursor.pos.x+self.FirstClickPos.x, cursor.pos.y+self.FirstClickPos.y)

    def posgrid(self):
        """revoie les coordonnées de la forme alignée sur la grille"""
        diffx = self.pos.x % GRID_WIDTH
        diffy = self.pos.y % GRID_WIDTH
        posx = self.pos.x - (diffx if diffx<GRID_WIDTH//2 else diffx-GRID_WIDTH)
        posy = self.pos.y - (diffy if diffy<GRID_WIDTH//2 else diffy-GRID_WIDTH)
        return posx,posy

    def placeavail(self):
        posalign = self.posgrid()
        rect = pygame.Rect(posalign[0],posalign[1],self.taken_space.x*GRID_WIDTH,self.taken_space.y*GRID_WIDTH)
        pcbAttach = None
        for i in range(len(self.shapes)):
            if self.shapes[i]!=self:
                otherShapeRect = pygame.Rect(self.shapes[i].pos.x,self.shapes[i].pos.y,self.shapes[i].taken_space.x*GRID_WIDTH,self.shapes[i].taken_space.y*GRID_WIDTH)
                if 'PCB' in self.shapes[i].get_type() and otherShapeRect.contains(rect):
                    pcbAttach = self.shapes[i]
                    continue
                if self.shapes[i].parent != self:
                    isColliding = rect.colliderect(otherShapeRect)
                    if isColliding:
                        return False,None
        return True,pcbAttach

    def get_type(self):
        return 'MoveableElement'

class Shape(MoveableElement):
    def __init__(self,pos,size=Vector2(GRID_WIDTH,GRID_WIDTH),color=(100,0,0),form="square",direc=0):
        if type(color) == tuple: color = RGB(color)
        super().__init__(pos,size,color)
        self.pos,self.size,self.color = pos,size,color
        self.isLocked = False
        self.draggingPanel = False
        self.FirstClickPos = Vector2.ZERO()
        self.form = form
        self.direction = direc

    def __eq__(self,object):
        if isinstance(object, Shape):
            return self.pos.x == object.pos.x and self.pos.y == object.pos.y and self.size == object.size

    def copy(self):
        return Shape(self.pos,self.size,self.color,self.form,self.direction)

    def draw(self,screen):
        # preview square
        if self.continousClick and self.placeavail()[0]:
            if PYGAME_IS_MODERN_VERSION: # la ligne ci-dessous renvoie une erreur si la version de pygame est inférieure à 2.0.1, donc on dessine un carré sans arrondi pour les versions antérieures
                pygame.draw.rect(screen, (180,180,180), (self.posgrid()[0]+2+self.start_pos.x, self.posgrid()[1]+2+self.start_pos.y, self.size.x-4, self.size.y-4), 2, 10)
            else:
                pygame.draw.rect(screen, (180,180,180), (self.posgrid()[0]+2+self.start_pos.x, self.posgrid()[1]+2+self.start_pos.y, self.size.x-4, self.size.y-4), 2)
        # shape
        if self.form == "square":
            pygame.draw.rect(screen, self.color.value, (self.pos.x+self.start_pos.x, self.pos.y+self.start_pos.y, self.size.x, self.size.y))
        elif self.form == "triangle":
            pygame.draw.polygon(screen, self.color.value, [(self.pos.x, self.pos.y), (self.pos.x + self.size.x, self.pos.y), (self.pos.x, self.size.y + self.pos.y),(self.pos.x + self.size.x, self.size.y + self.pos.y),(self.pos.x, self.pos.y), (self.pos.x + self.size.x, self.pos.y)][self.direction:self.direction+3], 0)
        elif self.form == "circle":
            if PYGAME_IS_MODERN_VERSION: #renvoie une erreur si la version de pygame < 2.0.1, donc on dessine un carré au lieu d'un cercle pour les versions antérieures
                pygame.draw.circle(screen, self.color.value, ((self.pos.x+self.size.x,self.pos.x)[self.direction%2], (self.pos.y+self.size.y,self.pos.y)[self.direction//2]), self.size.x, 0, draw_top_left=(True,False,False,False)[self.direction],draw_top_right=(False,True,False,False)[self.direction],draw_bottom_left=(False,False,True,False)[self.direction],draw_bottom_right=(False,False,False,True)[self.direction])
            else:
                pygame.draw.rect(screen, self.color.value, pygame.Rect(self.pos.x,self.pos.y, self.size.x, self.size.y))
        # hover effect
        if self.isHovered:
            pygame.draw.rect(screen, (255,255,255), pygame.Rect(self.start_pos.x+self.pos.x-2, self.start_pos.y+self.pos.y-2, self.width+4, self.height+4),3)

    def draw_connections(self,screen, extra=(1,1)):
        offset = int((self.width%9+extra[0])/2),int((self.height%9+extra[0])/2)
        for i in range((self.height//9)+extra[1]):
            pygame.draw.rect(screen, (200,200,200), pygame.Rect(self.start_pos.x+self.pos.x-5, offset[1]+self.start_pos.y+self.pos.y+i*9, 10, 3))
            pygame.draw.rect(screen, (200,200,200), pygame.Rect(self.start_pos.x+self.pos.x+self.width-5, offset[1]+self.start_pos.y+self.pos.y+i*9, 10, 3))
        for j in range((self.width//9)+extra[0]):
            pygame.draw.rect(screen, (200,200,200), pygame.Rect(offset[0]+self.start_pos.x+self.pos.x+j*9, self.start_pos.y+self.pos.y-5, 3, 10))
            pygame.draw.rect(screen, (200,200,200), pygame.Rect(offset[0]+self.start_pos.x+self.pos.x+j*9, self.start_pos.y+self.pos.y+self.height-5, 3, 10))

        """
    _________triangle_________
    direc | point 1                         | point 2                        | point 3                        |
        1 | pos.x, pos.y                    | pos.x + size.x, pos.y          | pos.x, pos.y + size.y          |
        2 | pos.x, pos.y                    | pos.x + size.x, pos.y          | pos.x + size.x, pos.y + size.y |
        3 | pos.x, pos.y                    | pos.x + size.x, pos.y + size.y | pos.x, pos.y + size.y          |
        0 | pos.x + size.x, pos.y + size.y  | pos.x + size.x, pos.y          | pos.x, pos.y + size.y          |

    _________cercle_________
    direc | centre                         |                        partie à dessiner (haut, bas, gauche, droite)                          |
        1 | pos.x + size.x, pos.y + size.y | draw_top_left=True  | draw_top_right=False | draw_bottom_right=False | draw_bottom_left=False |
        2 | pos.x         , pos.y + size.y | draw_top_left=False | draw_top_right=True  | draw_bottom_right=False | draw_bottom_left=False |
        3 | pos.x + size.x, pos.y          | draw_top_left=False | draw_top_right=False | draw_bottom_right=True  | draw_bottom_left=False |
        0 | pos.x         , pos.y          | draw_top_left=False | draw_top_right=False | draw_bottom_right=False | draw_bottom_left=True  |
        """

    def get_type(self):
        return 'Shape'

def update_shape_dragging(shapes):
    for k in range(len(shapes)):
        shape = shapes[k]
        for j in range(k+1, len(shapes)):
            if shapes[j].get_rect().collidepoint((cursor.pos.x, cursor.pos.y)):
                break
        else:
            shapes[k].update_pos(shapes)

defaultShapes = [Shape(Vector2(60,60),Vector2(60,60)),
                 Shape(Vector2(60,120),Vector2(60,60),color=(100,110,10), form="square"),
                 Shape(Vector2(120,60),Vector2(60,60),color=(100,110,10),form="triangle",direc=1),
                 Shape(Vector2(180,60),Vector2(60,60),color=(100,110,10),form="triangle",direc=2),
                 Shape(Vector2(120,120),Vector2(60,60),color=(100,110,10),form="triangle",direc=3),
                 Shape(Vector2(180,120),color=(100,110,10),form="triangle"),
                 Shape(Vector2(240,60),form="circle"),
                 Shape(Vector2(300,60),form="circle",direc=1),
                 Shape(Vector2(240,120),form="circle",direc=2),
                 Shape(Vector2(300,120),form="circle",direc=3)]