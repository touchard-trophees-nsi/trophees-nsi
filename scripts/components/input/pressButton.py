import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape
from scripts.parser.user_print import user_print
from scripts.parser.pseudocode import get_game_state
from scripts.dev import dprint

class PressButton(Shape):
    def __init__(self,pos,size=Vector2(50,50),color=(212,219,215),form="custom",direc=0):
        super().__init__(pos,size,color,form,direc,showWhenRunning=True)
        self.pressState = False
        self.id = 'PressButton'
        self.base_color = color
        self.pressed_color = (181,188,184)

    def is_pressed(self):
        return self.pressState

    def update(self, shapes):
        Shape.update(self, shapes)
        self.color = self.pressed_color if self.pressState else self.base_color
        if not get_game_state():
            self.pressState = False

    def onClick(self):
        if get_game_state():
            self.pressState = True
    
    def onRelease(self):
        self.pressState = False

    def draw(self,screen):
        Shape.draw(self,screen)
        position = self.pos+self.start_pos
        position = Vector2(position.x+int(self.width/2), position.y+int(self.width/2))
        if type(self.color)==tuple:
            pygame.draw.circle(screen, self.color, position.toTuple(), int(self.width/2))

    def get_showWhenRunning(self):
        return True
        
    def get_type(self):
        return 'Shape.PressButton'