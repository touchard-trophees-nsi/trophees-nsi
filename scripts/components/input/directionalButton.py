import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape
from scripts.parser.user_print import user_print
from scripts.parser.pseudocode import get_game_state
from scripts.graphics.spriteManager import load_sprite
from scripts.dev import dprint
from scripts.cursor import cursor

states = {
    'None':load_sprite('components/directionalButton/directionalButtonNone'),
    'Right':load_sprite('components/directionalButton/directionalButtonRight'),
    'Left':load_sprite('components/directionalButton/directionalButtonLeft'),
    'Up':load_sprite('components/directionalButton/directionalButtonUp'),
    'Down':load_sprite('components/directionalButton/directionalButtonDown')
}

hitboxes = {
    'Right':[(74,45),(107, 74)],
    'Left':[(13,45),(46, 74)],
    'Up':[(46,12),(75, 45)],
    'Down':[(46,74),(75, 107)],
}

class DirectionalButton(Shape):
    def __init__(self,pos,size=Vector2(120,120),color=(200,200,200),form="custom",direc=0):
        super().__init__(pos,size,color,form,direc,showWhenRunning=True)
        self.pressState = 'None'
        self.id = 'DirectionalButton'

    def get_pressed(self):
        return self.pressState

    def update(self, shapes):
        Shape.update(self, shapes)
        if get_game_state():
            for state, values in hitboxes.items():
                if cursor.pos.x>=self.pos.x+values[0][0] and cursor.pos.x<=self.pos.x+values[1][0] and cursor.pos.y>=self.pos.y+values[0][1] and cursor.pos.y<=self.pos.y+values[1][1] and not self.isFrozen and cursor.eventType=='left' and cursor.isClicking:
                    self.pressState = state
                    break
            else:
                self.pressState = 'None'
        else:
            self.pressState = 'None'
    
    def draw(self,screen):
        Shape.draw(self,screen)
        screen.blit(states[self.pressState], self.pos.toTuple()) 

    def get_showWhenRunning(self):
        return True

    def get_type(self):
        return 'Shape.PressButton'