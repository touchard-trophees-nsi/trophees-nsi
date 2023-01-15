# MODULES
import pygame
pygame.init()
from scripts.math.vector2 import Vector2
from scripts.ui.label import Label
from scripts.ui.labelHighlighting.keywords import coloredKeywords, coloredCharacters, specialChars
from scripts.ui.labelHighlighting.utils import char2indexes, word2indexes

HORIZONTAL_SPACE = Label(Vector2(0,0), size=15, text='_').get_width()

loaded_fonts = {}
class ColoredLabel(Label):
    def __init__(self, position, size=13, color=(255,255,255), text='', centered=False, font='RobotoMono-Regular'):
        super().__init__(position, size, color, text, centered, font)
    def draw(self, surface, text=''):
        white_text = list(text)

        # --- HIGHLIGHT ON MULTIPLE CHARS --- #
        isStrHighlighting = False
        isCommentHighlighting = False
        highlight_str = list(text)
        highlight_comment = list(text)
        # STRINGS
        for i in range(len(text)):
            if text[i] in coloredCharacters[(255,217,52)] and not isCommentHighlighting:
                isStrHighlighting = not isStrHighlighting
                white_text[i]=' '
                highlight_comment[i]=' '
            elif isStrHighlighting and not isCommentHighlighting:
                white_text[i]=' '
                highlight_comment[i]=' '
            else:
        # COMMENTS
                if text[i] in coloredCharacters[(92,99,112)]:
                    isCommentHighlighting = True
                    white_text[i]=' '
                elif isCommentHighlighting:
                    white_text[i]=' '
                else:
                    highlight_comment[i] = ' '
                highlight_str[i] = ' '
        self.draw_text(surface, ''.join(highlight_str), color=(255,217,52))
        self.draw_text(surface, ''.join(highlight_comment), color=(92,99,112))

        # ---------- KEYWORDS AND CHARS ---------- #
        for color_, keywords in coloredKeywords.items():
            for word in keywords:
                indexes = word2indexes(white_text, word)
                new_text = ''
                for i in range(len(text)):
                    if i in indexes:
                        new_text += text[i]
                        white_text[i] = ' '
                    else:
                        new_text += ' '
                self.draw_text(surface, new_text, color=color_)
        for color_, chars in coloredCharacters.items():
            for char in chars:
                indexes = char2indexes(white_text, char)
                new_text = ''
                for i in range(len(text)):
                    if i in indexes:
                        new_text += text[i]
                        white_text[i] = ' '
                    else:
                        new_text += ' '
                self.draw_text(surface, new_text, color=color_)
        
        # --- FUNCTION AND CLASS HIGHLIGHTING --- #
        wordIndexes = []
        for i in range(len(white_text)):
            if white_text[i]=='(' and len(wordIndexes)>0:
                new_text = ''
                for i in range(len(text)):
                    if i in wordIndexes:
                        new_text += text[i]
                        white_text[i] = ' '
                    else:
                        new_text += ' '
                self.draw_text(surface, new_text, color=(129,249,0))
            elif white_text[i] in specialChars:
                wordIndexes = []
            else:
                word += white_text[i]
                wordIndexes += [i]
            
        
        # --- CLASSIC TEXT --- #
        self.draw_text(surface, ''.join(white_text), color=self.color)
        
        '''
        # -------------- #
        labelWords = text.split(' ')
        for color_, keywords in coloredKeywords.items():#for word in labelWords:
            # --- #
            counter = 0
            for word in keywords:
                new_text = text.split(' ')
                for i in range(len(new_text)):
                    if new_text[i] != word:
                        length = len(new_text[i])
                        new_text[i] = ' '*length
                new_text = ' '.join(new_text)
                self.draw_text(surface, text=new_text, color=color_)
            if counter >= len(coloredKeywords):
                self.draw_text(surface, text=new_text, color=self.color)
        
        labelChars = list(text)
        for char in labelChars:
            new_text = list(text)
            for i in range(len(new_text)):
                if new_text[i]!= char:
                    new_text[i] = ' '
            new_text = ''.join(new_text)
            # --- #
            for color_, characters in coloredCharacters.items():
                if char in characters:
                    self.draw_text(surface, text=new_text, color=color_)
        '''
    def draw_text(self, surface, text='', color=(255,255,255)):
        if text != '':
            font = self.load_font()
            text = font.render(text, 1, color)
            self.surface = text
            if self.centered:
                surface.blit(text, (self.position.x-text.get_width()/2, self.position.y-text.get_height()/2))
            else:
                surface.blit(text, (self.position.x, self.position.y))
