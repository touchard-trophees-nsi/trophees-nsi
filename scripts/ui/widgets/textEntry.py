import pygame
from scripts.cursor import cursor
from scripts.math.vector2 import Vector2
from scripts.ui.selectable import Selectable, defaultPalette
from scripts.ui.label import Label
from scripts.ui.labelHighlighting.coloredLabel import ColoredLabel

table = 'abcdefghijklmnopqrstuvwxyz\
        ABCDEFGHIJKLMNOPQRSTUVWXYZ\
        0123456789\
        ,;.:+-*/=|\\?!@$£%&"\'_()[]{}<>\
        éÉèÈêÊëËôÔçÇù¤µ°§²#'

autoplacableChars = '\'"[{('
autoplacedChars = '\'"]})'

VERTICAL_SPACE = 15+5 # space between lines
HORIZONTAL_SPACE = Label(Vector2(0,0), size=15, text='_').get_width()
HIGHLIGHT_COLOR = (78, 177, 252)

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
        #
        self.cursor_pos = Vector2(0,0)
        self.onClickPos = Vector2(-1,-1)
        self.onReleasePos = Vector2(-1,-1)

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

    def move_line(self, step):
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
        # ----- #
        self.focus_on_cursor()

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

    def move_cursor(self, step):
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

    def backspace(self):
        n_of_loops = 1
        if self.selection != '':
            if self.onReleasePos.x<=self.onClickPos.x and self.onReleasePos.y<=self.onClickPos.y:
                self.cursor_pos = self.onClickPos
            n_of_loops = len(self.selection)+abs(self.onClickPos.y-self.onReleasePos.y)
            self.clear_selection()
        for i in range(n_of_loops):
            if self.cursor_pos.y>0 and self.cursor_pos.x==0:
                # REMOVE RETURN
                self.move_cursor(-1)
                saved_x = self.cursor_pos.x
                line = self.content.pop(self.cursor_pos.y+1)
                self.labels.pop(self.cursor_pos.y+1)
                for char in line:
                    self.add_char(char)
                self.cursor_pos.x = saved_x
                self.update_labels()
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

    def add_char(self, unicode):
        self.content[self.cursor_pos.y] = list(self.content[self.cursor_pos.y])
        if unicode in table:
            # DELETE EVERYTHING IN SELECTION
            if self.selection != '':
                if self.onReleasePos.x<=self.onClickPos.x and self.onReleasePos.y<=self.onClickPos.y:
                    self.cursor_pos = self.onClickPos
                self.backspace() # backspace only once since text is selected
            # PLACE CHAR
            self.content[self.cursor_pos.y].insert(self.cursor_pos.x, unicode)
            # PLACE 2ND CHAR IF IN AUTOPLACABLE_CHARS
            for i in range(len(autoplacableChars)):
                if autoplacableChars[i]==unicode:
                    self.content[self.cursor_pos.y].insert(self.cursor_pos.x+1, autoplacedChars[i])
        elif unicode == 'TAB':
            self.content[self.cursor_pos.y].insert(self.cursor_pos.x, '   ')
            self.move_cursor(2)
        self.content[self.cursor_pos.y] = ''.join(self.content[self.cursor_pos.y])
        self.move_cursor(1)
        self.clear_selection()
        self.update_labels()
        self.focus_on_cursor()

    def base_add_return(self):
        if self.selection != '':
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

    def add_return(self):
        self.base_add_return()

    def update_labels(self):
        for i in range(self.displayedLines[0], self.displayedLines[1]):
            if i < len(self.content):
                coefficient = abs(self.displayedLines[0]-i)
                self.labels[i].position = Vector2(int(self.pos.x+self.labelOffset.x), int(self.pos.y+self.labelOffset.y+VERTICAL_SPACE*coefficient))
                self.labels[i].text = self.content[i]
                self.text += '\n'+self.labels[i].text

    def clear_selection(self):
        self.onClickPos = Vector2(-1,-1)
        self.onReleasePos = Vector2(-1,-1)
        self.selection = ''

    def update_selection(self):
        try:
            if self.onReleasePos.isPositive() and self.onClickPos!=self.onReleasePos:
                self.selection = ''
                if self.onClickPos.y>self.onReleasePos.y:
                    # SELECTION UP
                    for i in range(self.onReleasePos.y, self.onClickPos.y+1):
                        if i == self.onReleasePos.y:
                            self.selection += self.content[i][self.onReleasePos.x:]
                        elif i == self.onClickPos.y:
                            self.selection += self.content[i][:self.onClickPos.x]
                        else:
                            self.selection += self.content[i]
                elif self.onClickPos.y<self.onReleasePos.y:
                    # SELECTION DOWN
                    for i in range(self.onClickPos.y, self.onReleasePos.y+1):
                        if i == self.onReleasePos.y:
                            self.selection += self.content[i][:self.onReleasePos.x]
                        elif i == self.onClickPos.y:
                            self.selection += self.content[i][self.onClickPos.x:]
                        else:
                            self.selection += self.content[i]
                elif self.onClickPos.x>self.onReleasePos.x:
                    self.selection = self.content[self.onClickPos.y][self.onReleasePos.x:self.onClickPos.x]
                else:
                    self.selection = self.content[self.onClickPos.y][self.onClickPos.x:self.onReleasePos.x]
        except:pass

    def update(self):
        self.base_update()
        self.update_scrolling()
        self.update_labels()
        self.update_selection()

        if self.cursor_pos.x < 0: self.cursor_pos.x=0
        if self.cursor_pos.y < 0: self.cursor_pos.y=0
        if self.displayedLines[0] < 0:
            self.displayedLines = [0, (self.height-self.labelOffset.y)//VERTICAL_SPACE]
        if self.selection != '':
            cursor.selectedElement = self
        
    def cursor2text_pos(self):
        if self.isHovered:
            mouse_pos = Vector2(int(cursor.pos.x), int(cursor.pos.y)) # Mouse pointer's pos, not the text cursor's
            relative_pos = mouse_pos-(self.pos+self.labelOffset)
            relative_pos.x = relative_pos.x//HORIZONTAL_SPACE + self.displayedChars[0]
            relative_pos.y = relative_pos.y//VERTICAL_SPACE + self.displayedLines[0]
            self.cursor_pos = Vector2(relative_pos.x, relative_pos.y)
            if self.cursor_pos.y>=len(self.content):
                self.cursor_pos.y = len(self.content)-1
                self.cursor_goto_x0() ; self.cursor_goto_lastx()
            if self.cursor_pos.x>=len(self.content[self.cursor_pos.y]):
                self.cursor_goto_x0() ; self.cursor_goto_lastx()
            return self.cursor_pos

    def onClick(self):
        self.onClickPos = self.cursor2text_pos()

    def onContinuousClick(self):
        
        self.onReleasePos = self.cursor2text_pos()

    def update_scrolling(self):
        if cursor.eventType=='scroll_down':
            self.move_line(1)

    def draw(self, screen):
        # drawing textEntry
        pygame.draw.rect(screen, tuple(self.color), (self.pos.x, self.pos.y, self.width, self.height))
        # drawing selection highlight
        try:
            if self.onReleasePos.isPositive() and self.onClickPos!=self.onReleasePos:
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
        except:pass
        # drawing text
        for i in range(self.displayedLines[0], self.displayedLines[1]):
            if i < len(self.labels):
                text = self.labels[i].text[self.displayedChars[0]:self.displayedChars[1]]
                self.labels[i].draw(screen, text=text)
        # drawing text cursor
        if self.isActive and self.cursor_pos.y>=self.displayedLines[0] and self.cursor_pos.y<self.displayedLines[1]:
            pygame.draw.rect(screen, (255,255,255), (self.pos.x+self.labelOffset.x+HORIZONTAL_SPACE*(self.cursor_pos.x-self.displayedChars[0]), self.pos.y+self.labelOffset.y+VERTICAL_SPACE*(self.cursor_pos.y-self.displayedLines[0]), 1, VERTICAL_SPACE))

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
