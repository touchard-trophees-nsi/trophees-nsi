# MODULES
import pygame
pygame.init()
from math import sqrt
from random import randint

loaded_fonts = {}
class Label:
    def __init__(self, position, size=13, color=(255,255,255), text='', centered=False, font='RobotoMono-Regular', isComponent=False):
        self.position = position
        self.size = size
        self.color = color
        self.text = text
        self.centered = centered
        self.font = font
        # --- #
        self.surface = None

    def load_font(self):
        if self.font not in loaded_fonts.keys():
                loaded_fonts[self.font] = {}
        if self.size not in loaded_fonts[self.font].keys():
            loaded_fonts[self.font][self.size] = pygame.font.Font(f'fonts/{self.font}.ttf', self.size)
        return loaded_fonts[self.font][self.size]

    def draw(self, surface, text='_'):
        if text == '_': text = self.text
        if text != '':
            font = self.load_font()
            text = font.render(text, 1, self.color)
            self.surface = text
            if self.centered:
                surface.blit(text, (self.position.x-text.get_width()/2, self.position.y-text.get_height()/2))
            else:
                surface.blit(text, (self.position.x, self.position.y))

    def get_width(self):
        self.surface = self.load_font()
        self.surface = self.surface.render(self.text, 1, self.color)
        if self.surface != None:
            return self.surface.get_width()
    
    def get_height(self):
        self.surface = self.load_font().render(self.text, 1, self.color)
        if self.surface != None:
            return self.surface.get_height()
    
    def update(self):
        pass

    def get_type(self):
        return 'Label'