import pygame
from scripts.cursor import cursor
from scripts.math.vector2 import Vector2
from scripts.ui.selectable import Selectable, defaultPalette
from scripts.ui.label import Label
from scripts.ui.labelHighlighting.coloredLabel import ColoredLabel
from scripts.ui.labelHighlighting.keywords import specialChars
from modules.pyperclip.src.pyperclip.__init__ import *

table = 'abcdefghijklmnopqrstuvwxyz\
        ABCDEFGHIJKLMNOPQRSTUVWXYZ\
        0123456789\
        ,;.:+-*/=|\\?!@$£%&"\'_()[]{}<>\
        éÉèÈêÊëËôÔçÇù¤µ°§²#^¨'

autoplacableChars = '\'"[{('
autoplacedChars = '\'"]})'

VERTICAL_SPACE = 15+5 # space between lines
HORIZONTAL_SPACE = Label(Vector2(0,0), size=15, text='_').get_width()
HIGHLIGHT_COLOR = (78, 177, 252)

class OptimizedTextEntry(Selectable):
    def __init__(self, pos, dims, idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[2], text=''):
        super().__init__(pos, dims, idleColor, hoveredColor, selectedColor, text, keepActivity=True)
        self.content = ''
        self.editIndex = 0
        self.labels = [Label(self.pos, size=15)]

    # -------------------------- #
    # ------- NAVIGATION ------- #
    # -------------------------- #

    def get_line_length(self, index):
        return len(self.labels[index].text)
    
    def get_line_content_index(self, index):
        lines = self.content.split('■')
        count = 0
        for i in range(index):
            count += lines[i]+1

    # ---------------------------- #
    # ------- TEXT EDITING ------- #
    # ---------------------------- #

    def backspace(self,ctrl=False):
        print('test')
        if self.editIndex>0:
            self.content = self.content[:self.editIndex-1]+self.content[self.editIndex:]
            print('backspaced :',self.content)
        self.parse_content()

    def add_return(self,ctrl=False):
        self.content += '■' # alt+254 character to indicate return (do not use \n since it can be used in code)
        self.parse_content()

    def add_char(self, unicode, isManual=False):
        if unicode in table:
            self.content += unicode
        elif unicode == 'TAB':
            self.content += '   '
        self.parse_content()

    def parse_content(self):
        lines = self.content.split('■')
        self.labels=[]
        for i in range(len(lines)):
            self.labels.append(Label(self.pos, size=15,text=lines[i]))
        print(self.labels[0].text)

    # ----------------------------- #
    # ------- FRAME REFRESH ------- #
    # ----------------------------- #

    def update(self):
        self.base_update()
        self.editIndex = len(self.content)

        # LABELS
        for i in range(len(self.labels)):
            self.labels[i].position = Vector2(self.pos.x, self.pos.y+i*VERTICAL_SPACE)

    def draw(self, screen):
        # drawing textEntry
        pygame.draw.rect(screen, tuple(self.color), (self.pos.x, self.pos.y, self.width, self.height))
        # drawing labels
        for label in self.labels:
            print(label.text)
            label.draw(screen, text=label.text)
    
    def get_type(self):
        return 'Selectable.TextEntry'