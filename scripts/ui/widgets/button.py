import pygame
from scripts.math.vector2 import Vector2
from scripts.cursor import cursor
from scripts.ui.selectable import Selectable, defaultPalette
from scripts.ui.label import Label

class Button(Selectable):
    def __init__(self, pos, dims, text='', textSize=20, img=None, idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[2]):
        super().__init__(pos, dims, idleColor, hoveredColor, selectedColor, text)
        self.label = Label(Vector2(int(self.pos.x+self.width/2), int(self.pos.y+self.height/2)), size=textSize, text=text, centered=True)
        self.img = img

    def update(self):
        self.base_update()
        self.label.position = Vector2(int(self.pos.x+self.width/2), int(self.pos.y+self.height/2))

    def is_pressed(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height).collidepoint((cursor.pos.x, cursor.pos.y))

    def draw(self, screen):
        pygame.draw.rect(screen, tuple(self.color), (self.pos.x, self.pos.y, self.width, self.height))
        self.label.draw(screen, text=self.label.text)
        if self.img != None:
            screen.blit(self.img, (self.pos.x + (self.width/2 - self.img.get_width()/2), self.pos.y + (self.height/2 - self.img.get_height()/2)))

    def get_type(self):
        return 'Selectable.Button'
    
    def onClick(self):
        click_sound=pygame.mixer.Sound("sound/click.mp3")
        click_sound.play()
