# MODULES
import pygame
from scripts.ui.label import Label
from scripts.math.vector2 import Vector2
pygame.init()

class DynamicLabel(Label):
    def __init__(self, position, velocity, size=13, color=(255,255,255), text='', centered=False, fade_speed=1, font='RobotoMono-Regular'):
        super().__init__(position, size, color, text, centered, font)
        self.velocity = velocity
        self.fade_speed = fade_speed
    
    def draw(self, surface, text=''): 
        Label.draw(self, surface, text)
        self.position = self.position+self.velocity
        self.color = (self.color[0]-10*self.fade_speed, self.color[1]-10*self.fade_speed, self.color[2]-10*self.fade_speed)
        if self.color[0]<0: self.color = (0, self.color[1], self.color[2])
        if self.color[1]<0: self.color = (self.color[0], 0, self.color[2])
        if self.color[2]<0: self.color = (self.color[0], self.color[1], 0)
