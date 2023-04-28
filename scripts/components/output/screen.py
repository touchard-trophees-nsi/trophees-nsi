import pygame
from scripts.math.vector2 import Vector2
from scripts.components.shapes import Shape
from scripts.parser.pseudocode import get_game_state

# printed circuit board
class Screen(Shape):
    def __init__(self,pos,size=Vector2(231,121),color=(15,15,15),form="square",direc=0):
        super().__init__(pos,size,color,form,direc,showWhenRunning=True)
        self.draw_surface = pygame.Surface((self.width, self.height))
        self.id = 'Screen'
        self.videoChipID = 'VideoChip'

    def blit_rectangle(self, rect):
        pygame.draw.rect(self.draw_surface, (255,255,255),pygame.Rect(rect[0], rect[1], rect[2], rect[3]))
    
    def draw(self,screen):
        Shape.draw(self,screen)
        if get_game_state() and self.draw_surface != None:
            screen.blit(self.draw_surface, (self.start_pos.x+self.pos.x, self.start_pos.y+self.pos.y))
        else:
            self.draw_surface = pygame.Surface((self.width, self.height))

    def pickle_check(self):
        self.draw_surface = None

    def set_videoChipID(self, ID):
        self.videoChipID = ID
    
    def get_videoChipID(self):
        return self.videoChipID
        
    def get_showWhenRunning(self):
        return True
        
    def get_type(self):
        return 'Shape.Screen'