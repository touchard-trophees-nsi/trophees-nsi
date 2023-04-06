import pygame
from scripts.cursor import cursor
from scripts.math.vector2 import Vector2
from scripts.ui.selectable import Selectable, defaultPalette
from scripts.ui.label import Label
from scripts.ui.labelHighlighting.coloredLabel import ColoredLabel
from scripts.ui.labelHighlighting.keywords import specialChars
from lang.char_table import table, autoplacableChars, autoplacedChars
from modules.pyperclip.src.pyperclip.__init__ import *

VERTICAL_SPACE = 15+5 # space between lines
HORIZONTAL_SPACE = Label(Vector2(0,0), size=15, text='_').get_width()
HIGHLIGHT_COLOR = (39, 85, 126) #(78, 177, 252)

class TextEntry(Selectable):
    def __init__(self, pos, dims, idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[2], text=''):
        super().__init__(pos, dims, idleColor, hoveredColor, selectedColor, text, keepActivity=True)
        self.labelOffset = Vector2(3, 0) # offset from window
        self.labels = [ColoredLabel(Vector2(0,0), size=15, text=text, centered=False)]
        self.displayedChars = [0, (self.width-self.labelOffset.x)//HORIZONTAL_SPACE]
        self.displayedLines = [0, (self.height-self.labelOffset.y)//VERTICAL_SPACE]
        #
        self.content = [self.text]
        self.selection = ''
        self.isSelecting = False
        #
        self.cursor_pos = Vector2(0,0)
        self.onClickPos = Vector2(-1,-1)
        self.onReleasePos = Vector2(-1,-1)

    def clipboard_copy(self):
        copy(self.selection)

    def clipboard_paste(self):
        sliced = list(paste())
        row = []
        for i in range(len(sliced)):
            if sliced[i]=='\r':
                self.add_chars(''.join(row))
                row = []
                self.add_return()
            else:
                if sliced[i] not in '\r\n':
                    row.append(sliced[i])
                if i==len(sliced)-1:
                    self.add_chars(''.join(row))
                    row = []
        self.update_labels()

    def select_all(self):
        self.isSelecting = True
        self.onClickPos.x, self.onClickPos.y = 0,0
        self.onReleasePos.x, self.onReleasePos.y = len(self.content[-1]), len(self.content)-1
        self.cursor_pos = self.onReleasePos
        self.focus_on_cursor()
        self.update_selection()

    def cursor_goto_x0(self):
        self.cursor_pos.x = 0
        self.displayedChars = [0, (self.width-self.labelOffset.x)//HORIZONTAL_SPACE]

    def cursor_goto_lastx(self):
        while self.cursor_pos.x < len(self.content[self.cursor_pos.y]):
            self.move_cursor(1)

    def focus_on_cursor(self):
        while self.cursor_pos.y >= self.displayedLines[1]:
            self.displayedLines[0] += 1
            self.displayedLines[1] += 1
        while self.cursor_pos.y < self.displayedLines[0]:
            self.displayedLines[0] -= 1
            self.displayedLines[1] -= 1

    def move_line(self, step, shift=False):
        if shift:
            if self.isSelecting==False:
                self.isSelecting = True
                self.onClickPos.x, self.onClickPos.y = self.cursor_pos.x, self.cursor_pos.y
        else:
            cursor.selectedElement.clear_selection()

        if step >= 0:
            if self.cursor_pos.y+step<len(self.content):
                if self.cursor_pos.x>len(self.content[self.cursor_pos.y+step]) and len(self.content[self.cursor_pos.y])>len(self.content[self.cursor_pos.y+step]):
                    self.cursor_pos.y += step
                    self.cursor_goto_x0() ; self.cursor_goto_lastx()
                else:
                    self.cursor_pos.y += step
            else:
                self.cursor_pos.y = len(self.content)-1
        else:
            if self.cursor_pos.y+step>=0:
                if self.cursor_pos.x>len(self.content[self.cursor_pos.y+step]) and len(self.content[self.cursor_pos.y])>len(self.content[self.cursor_pos.y+step]):
                    self.cursor_pos.y+=step
                    self.cursor_goto_x0() ; self.cursor_goto_lastx()
                else:
                    self.cursor_pos.y += step
            else:
                self.cursor_pos.y=0
        self.update_labels()
        # ----- #
        self.focus_on_cursor()

        if shift:
            self.onReleasePos.x, self.onReleasePos.y = self.cursor_pos.x, self.cursor_pos.y
            self.update_selection()

        self.update_labels()
        '''
        if self.cursor_pos.y+step>=0 and self.cursor_pos.y+step<len(self.content):
            if len(self.content[self.cursor_pos.y])>len(self.content[self.cursor_pos.y+step]):
                # IF CURSOR LINE IS LONGER THAN DESTINATION LINE
                self.cursor_pos.y += step
                self.cursor_goto_x0() ; self.cursor_goto_lastx()
            else:
                # IF CURSOR LINE IS AS LONG OR SHORTER THAN THE DESTINATION LINE
                self.cursor_pos.y += step
        '''

    def move_cursor(self, step, shift=False, ctrl=False):
        if shift:
            if self.isSelecting==False:
                self.isSelecting = True
                self.onClickPos.x, self.onClickPos.y = self.cursor_pos.x, self.cursor_pos.y
        else:
            cursor.selectedElement.clear_selection()

        def _move():
            # MOVING CURSOR ALONG CHARACTERS
            self.cursor_pos.x += step
            if self.cursor_pos.x<0 and self.cursor_pos.y>0:
                self.cursor_pos.y -= 1
                self.cursor_goto_x0() ; self.cursor_goto_lastx()
            elif self.cursor_pos.x<0 and self.cursor_pos.y==0:
                self.cursor_pos.x = 0
            elif self.cursor_pos.x>len(self.content[self.cursor_pos.y]):
                if self.cursor_pos.y<len(self.content)-1:
                    self.cursor_pos.y += 1
                    self.cursor_goto_x0()
                else:
                    self.cursor_pos.x=len(self.content[self.cursor_pos.y])

            # HORIZONTAL SCROLLING
            if self.cursor_pos.x<self.displayedChars[0]:
                self.displayedChars[0]-=1
                self.displayedChars[1]-=1
            elif self.cursor_pos.x>self.displayedChars[1]:
                self.displayedChars[0]+=1
                self.displayedChars[1]+=1
            self.focus_on_cursor()

        if ctrl: # if control mode enabled, move cursor as long as no special character is encountered
            breakpoint=0
            if self.cursor_pos.x>0 and (self.cursor_pos.y>0 or self.cursor_pos.x>0) and self.content[self.cursor_pos.y][self.cursor_pos.x-1] not in specialChars:
                while self.content[self.cursor_pos.y][self.cursor_pos.x-1] not in specialChars:
                    breakpoint += 1
                    _move()
                    if self.cursor_pos.x<=0 or breakpoint>1000: break
            else:
                _move()
        else:
            _move()

        if shift:
            self.onReleasePos.x, self.onReleasePos.y = self.cursor_pos.x, self.cursor_pos.y
            self.update_selection()
        self.update_labels()

    def backspace(self, ctrl=False):
        if ctrl:
            self.move_cursor(-1, shift=True, ctrl=True)
        n_of_loops = 1
        if not self.isSelecting and len(self.content[self.cursor_pos.y])>=3 and self.content[self.cursor_pos.y][self.cursor_pos.x-1]==' ' and self.content[self.cursor_pos.y][self.cursor_pos.x-2]==' ' and self.content[self.cursor_pos.y][self.cursor_pos.x-3]==' ':
            n_of_loops = 3
        if self.isSelecting and self.selection != '':
            if self.onReleasePos.y<self.onClickPos.y or (self.onReleasePos.y==self.onClickPos.y and self.onReleasePos.x<=self.onClickPos.x):
                self.cursor_pos = self.onClickPos
            n_of_loops = len(self.selection)+abs(self.onClickPos.y-self.onReleasePos.y)-1
            self.clear_selection()
        for i in range(n_of_loops):
            if self.cursor_pos.y>0 and self.cursor_pos.x==0:
                # REMOVE RETURN
                self.move_cursor(-1)
                saved_x = self.cursor_pos.x
                line = self.content.pop(self.cursor_pos.y+1)
                self.labels.pop(self.cursor_pos.y+1)
                self.add_chars(line)
                self.cursor_pos.x = saved_x
            elif len(self.content[self.cursor_pos.y])>0:
                # REMOVE CHAR AT CURSOR POS
                index = self.cursor_pos.x-1
                self.move_cursor(-1)
                if index >= 0:
                    self.content[self.cursor_pos.y] = list(self.content[self.cursor_pos.y])
                    self.content[self.cursor_pos.y].pop(index)
        self.content[self.cursor_pos.y] = ''.join(self.content[self.cursor_pos.y])
        self.update_labels()
        self.focus_on_cursor()

    def add_char(self, unicode, isManual=False):
        # DELETE EVERYTHING IN SELECTION
        if self.isSelecting and self.selection != '':
            if self.onReleasePos.x<=self.onClickPos.x and self.onReleasePos.y<=self.onClickPos.y:
                self.cursor_pos = self.onClickPos
            self.backspace() # backspace only once since text is selected
        if unicode in table:
            # PLACE CHAR
            self.content[self.cursor_pos.y] = list(self.content[self.cursor_pos.y])
            self.content[self.cursor_pos.y].insert(self.cursor_pos.x, unicode)
            # PLACE 2ND CHAR IF IN AUTOPLACABLE_CHARS
            if isManual:
                for i in range(len(autoplacableChars)):
                    if autoplacableChars[i]==unicode:
                        self.content[self.cursor_pos.y].insert(self.cursor_pos.x+1, autoplacedChars[i])
            self.move_cursor(1)
        elif unicode == 'TAB':
            self.content[self.cursor_pos.y] = list(self.content[self.cursor_pos.y])
            self.content[self.cursor_pos.y].insert(self.cursor_pos.x, '   ')
            self.move_cursor(3)
        self.content[self.cursor_pos.y] = ''.join(self.content[self.cursor_pos.y])
        self.clear_selection()
        self.focus_on_cursor()
        if isManual:
            self.update_labels()

    def base_add_return(self):
        if self.isSelecting and self.selection != '':
            if self.onReleasePos.x<=self.onClickPos.x and self.onReleasePos.y<=self.onClickPos.y:
                self.cursor_pos = self.onClickPos
            self.backspace() # backspace only once since text is selected
        self.content[self.cursor_pos.y] = list(self.content[self.cursor_pos.y])
        saved_text = ''.join(self.content[self.cursor_pos.y][self.cursor_pos.x:])
        self.content[self.cursor_pos.y] = ''.join(self.content[self.cursor_pos.y][:self.cursor_pos.x])
        # --- #
        self.content.insert(self.cursor_pos.y+1, '')
        self.content[self.cursor_pos.y+1]=saved_text
        self.labels.append(ColoredLabel(Vector2(0,0), size=15, text=self.content[self.cursor_pos.y+1], centered=False))
        # auto tab feature
        self.cursor_goto_x0()
        spaceCount = 0
        for i in range(len(self.content[self.cursor_pos.y])):
            if self.content[self.cursor_pos.y][i]==' ':
                spaceCount += 1
            else:
                break
        numOfTabs = (spaceCount//3)
        if len(self.content[self.cursor_pos.y])>0 and self.content[self.cursor_pos.y][-1]==':': numOfTabs += 1
        self.move_line(1)
        for i in range(numOfTabs):
            self.add_char('TAB')
        self.update_labels()
        self.focus_on_cursor()

    def add_chars(self, text):
        # DELETE EVERYTHING IN SELECTION
        if self.isSelecting and self.selection != '':
            if self.onReleasePos.x<=self.onClickPos.x and self.onReleasePos.y<=self.onClickPos.y:
                self.cursor_pos = self.onClickPos
            self.backspace() # backspace only once since text is selected
        # INSERT
        new_text = list(text)
        for char in new_text:
            if char not in table:
                new_text.remove(char)
        n_chars = len(new_text)
        self.content[self.cursor_pos.y] = list(self.content[self.cursor_pos.y])
        self.content[self.cursor_pos.y].insert(self.cursor_pos.x, ''.join(new_text))
        self.content[self.cursor_pos.y] = ''.join(self.content[self.cursor_pos.y])
        self.move_cursor(n_chars)
        self.clear_selection()
        self.focus_on_cursor()

    def add_return(self):
        self.base_add_return()

    def update_labels(self):
        for i in range(self.displayedLines[0], self.displayedLines[1]):
            if i < len(self.content):
                self.labels[i].text = self.content[i]
                self.labels[i].refresh(self.content[i][self.displayedChars[0]:self.displayedChars[1]])

    def clear_selection(self):
        self.onClickPos = Vector2(-1,-1)
        self.onReleasePos = Vector2(-1,-1)
        self.selection = ''
        self.isSelecting = False

    def update_selection(self):
        try:
            if self.onReleasePos.isPositive() and self.onClickPos!=self.onReleasePos:
                self.selection = ''
                if self.onClickPos.y>self.onReleasePos.y:
                    # SELECTION UP
                    for i in range(self.onReleasePos.y, self.onClickPos.y+1):
                        if i == self.onReleasePos.y:
                            self.selection += self.content[i][self.onReleasePos.x:]
                            self.selection += '\n'
                        elif i == self.onClickPos.y:
                            self.selection += self.content[i][:self.onClickPos.x]
                        else:
                            self.selection += self.content[i]
                            self.selection += '\n'
                elif self.onClickPos.y<self.onReleasePos.y:
                    # SELECTION DOWN
                    for i in range(self.onClickPos.y, self.onReleasePos.y+1):
                        if i == self.onReleasePos.y:
                            self.selection += self.content[i][:self.onReleasePos.x]
                        elif i == self.onClickPos.y:
                            self.selection += self.content[i][self.onClickPos.x:]
                            self.selection += '\n'
                        else:
                            self.selection += self.content[i]
                            self.selection += '\n'
                elif self.onClickPos.x>self.onReleasePos.x:
                    self.selection = self.content[self.onClickPos.y][self.onReleasePos.x:self.onClickPos.x]
                else:
                    self.selection = self.content[self.onClickPos.y][self.onClickPos.x:self.onReleasePos.x]
        except:print('Selectable.TextEntry error in update_selection(self)')

    def update(self):
        self.base_update()
        self.update_scrolling()
        #self.update_labels()
        self.update_selection()

        # LABELS
        for i in range(self.displayedLines[0], self.displayedLines[1]):
            if i < len(self.content):
                coefficient = abs(self.displayedLines[0]-i)
                self.labels[i].position = Vector2(int(self.pos.x+self.labelOffset.x), int(self.pos.y+self.labelOffset.y+VERTICAL_SPACE*coefficient))

        # CURSOR
        if self.cursor_pos.x < 0: self.cursor_pos.x=0
        if self.cursor_pos.y < 0: self.cursor_pos.y=0
        if self.displayedLines[0] < 0:
            self.displayedLines = [0, (self.height-self.labelOffset.y)//VERTICAL_SPACE]
        if self.isSelecting and self.selection != '':
            cursor.selectedElement = self

    def cursor2text_pos(self):
        if self.isHovered:
            mouse_pos = Vector2(int(cursor.pos.x), int(cursor.pos.y)) # Mouse pointer's pos, not the text cursor's
            relative_pos = mouse_pos-(self.pos+self.labelOffset)
            relative_pos.x = relative_pos.x//HORIZONTAL_SPACE + self.displayedChars[0]
            relative_pos.y = relative_pos.y//VERTICAL_SPACE + self.displayedLines[0]
            cursor_pos = Vector2(relative_pos.x, relative_pos.y)
            if cursor_pos.y>=len(self.content):
                cursor_pos.y = len(self.content)-1
                cursor_pos.x=0
                while cursor_pos.x < len(self.content[cursor_pos.y]):
                    cursor_pos.x += 1
            if cursor_pos.x>=len(self.content[cursor_pos.y]):
                cursor_pos.x=0
                while cursor_pos.x < len(self.content[cursor_pos.y]):
                    cursor_pos.x += 1
            return cursor_pos
        return Vector2(0,0)

    def onClick(self):
        self.cursor_pos = self.cursor2text_pos()
        self.onClickPos = self.cursor_pos
        self.isSelecting = True

    def onContinuousClick(self):
        self.cursor_pos = self.cursor2text_pos()
        self.onReleasePos = self.cursor2text_pos()

    def update_scrolling(self):
        if cursor.eventType=='scroll_down':
            self.move_line(1)

    def draw(self, screen):
        # drawing textEntry
        pygame.draw.rect(screen, tuple(self.color), (self.pos.x, self.pos.y, self.width, self.height))
        # drawing selection highlight
        try:
            if self.isSelecting:
                if self.onClickPos.y>self.onReleasePos.y:
                    # SELECTION UP
                    for i in range(self.onReleasePos.y, self.onClickPos.y+1):
                        if i == self.onReleasePos.y:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x+HORIZONTAL_SPACE*(self.onReleasePos.x-self.displayedChars[0]), self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(self.onReleasePos.y-self.displayedLines[0]), (len(self.content[i])-self.onReleasePos.x)*HORIZONTAL_SPACE, VERTICAL_SPACE))#self.content[i][self.onReleasePos.x:]
                        elif i == self.onClickPos.y:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x, self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(self.onClickPos.y-self.displayedLines[0]), self.onClickPos.x*HORIZONTAL_SPACE, VERTICAL_SPACE))
                        else:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x, self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(i-self.displayedLines[0]), (len(self.content[i]))*HORIZONTAL_SPACE, VERTICAL_SPACE))
                elif self.onClickPos.y<self.onReleasePos.y:
                    # SELECTON DOWN
                    for i in range(self.onClickPos.y, self.onReleasePos.y+1):
                        if i == self.onReleasePos.y:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x, self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(self.onReleasePos.y-self.displayedLines[0]), self.onReleasePos.x*HORIZONTAL_SPACE, VERTICAL_SPACE))
                        elif i == self.onClickPos.y:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x+HORIZONTAL_SPACE*(self.onClickPos.x-self.displayedChars[0]), self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(self.onClickPos.y-self.displayedLines[0]), (len(self.content[i])-self.onClickPos.x)*HORIZONTAL_SPACE, VERTICAL_SPACE))
                        else:
                            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x, self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(i-self.displayedLines[0]), (len(self.content[i]))*HORIZONTAL_SPACE, VERTICAL_SPACE))
                elif self.onClickPos.x>self.onReleasePos.x:
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x+HORIZONTAL_SPACE*(self.onReleasePos.x-self.displayedChars[0]), self.pos.y+self.labelOffset.y+VERTICAL_SPACE*self.onReleasePos.y, (self.onClickPos.x-self.onReleasePos.x)*HORIZONTAL_SPACE, VERTICAL_SPACE))
                else:
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (self.pos.x+self.labelOffset.x+HORIZONTAL_SPACE*(self.onClickPos.x-self.displayedChars[0]), self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(self.onClickPos.y), (self.onReleasePos.x-self.onClickPos.x)*HORIZONTAL_SPACE, VERTICAL_SPACE))
        except:print('Selectable.TextEntry error in draw(self, screen)')
        # drawing text
        for i in range(self.displayedLines[0], self.displayedLines[1]):
            if i < len(self.labels):
                text = self.labels[i].text[self.displayedChars[0]:self.displayedChars[1]]
                self.labels[i].draw(screen, text=text)
        # drawing text cursor
        if self.isActive and self.cursor_pos.y>=self.displayedLines[0] and self.cursor_pos.y<self.displayedLines[1]:
            x_pos = self.labelOffset.x+HORIZONTAL_SPACE*(self.cursor_pos.x-self.displayedChars[0])
            y_pos = self.labelOffset.y+VERTICAL_SPACE*(self.cursor_pos.y-self.displayedLines[0])
            if x_pos > self.width:
                x_pos = self.width
            if y_pos > self.height:
                y_pos = self.height
            pygame.draw.rect(screen, (255,255,255), (self.pos.x+x_pos, self.pos.y+y_pos, 1, VERTICAL_SPACE))

    def get_text(self):
        out = ''
        for line in self.content:
            out += line+'\n'
        self.text = out
        return out

    def __repr__(self):
        print(self.text)

    def get_type(self):
        return 'Selectable.TextEntry'

class HorizontalTextField(TextEntry):
    '''
    A TextEntry-like object which is limited vertically
    '''
    def __init__(self, pos, dims, idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[2], text=''):
        '''
        '''
        super().__init__(pos, dims, idleColor, hoveredColor, selectedColor, text)

    def add_return(self):
        if (len(self.content)+1)*VERTICAL_SPACE<self.height:
            self.base_add_return()

    def get_type(self):
        return 'Selectable.TextEntry.HorizontalTextField'
