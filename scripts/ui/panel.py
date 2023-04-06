import pygame
from scripts.ui.label import Label
from scripts.ui.widgets.button import Button
from scripts.ui.widgets.textEntry import TextEntry
from scripts.math.vector2 import Vector2
from scripts.math.camera import camera
from scripts.graphics.color import RGB, gradient_palette
from scripts.graphics.spriteManager import load_sprite
from scripts.cursor import cursor

defaultPalette = gradient_palette(RGB(48,48,48),step=15,len_=2)
class Panel:
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='Panel', font='RobotoMono-Regular', hasBar=True):
        self.pos = pos
        self.width, self.height = dims.x, dims.y
        self.barWidth, self.barHeight = dims.x, 30
        self.name = name
        # --- #
        self.bgColor = bgColor
        self.barColor = barColor

        self.outlineColorInactive = RGB(10,10,10)
        self.outlineColorActive = RGB(150,150,150)
        self.outlineColor = self.outlineColorInactive
        # --- #
        # window
        self.isActive = False
        self.isHovered = False
        self.isLocked = False if hasBar else True
        # close button
        self.isCloseHovered = False
        # bar
        self.hasBar = hasBar
        self.barFirstClickPos = Vector2.ZERO()
        self.draggingPanel = False
        # --- #
        self.labels = [Label(Vector2(self.pos.x+7, self.pos.y+2), size=17, text=self.name, font=font)]
        self.labelPosOffsets = []
        for l in self.labels:
            self.labelPosOffsets.append(l.position-self.pos)
        # -- #
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x')}
        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def set_isActive(self, value=None):
        self.isActive = not self.isActive if value==None else value
        self.outlineColor = self.outlineColorActive if self.isActive else self.outlineColorInactive

    def update(self, panels):
        self.update_physics(panels)
        self.update_components(panels)
        self.update_labels()

    def update_physics(self, panels):
        if cursor.eventType != 'left':
            self.draggingPanel = False

        # Window dragging
        if cursor.pos.x>self.pos.x and cursor.pos.x<self.pos.x+self.barWidth and cursor.pos.y>self.pos.y and cursor.pos.y<self.pos.y+self.barHeight and not self.isLocked:
            if cursor.eventType=='left' and (cursor.selectedElement == None or cursor.selectedElement == self):
                self.draggingPanel = True
                if self.barFirstClickPos == Vector2.ZERO():
                    self.barFirstClickPos = Vector2(self.pos.x-cursor.pos.x, self.pos.y-cursor.pos.y)
            else:
                self.barFirstClickPos = Vector2.ZERO()
        else:
            self.isCloseHovered = False

        # Panel selection
        if cursor.pos.x>self.pos.x and cursor.pos.x<self.pos.x+self.width and cursor.pos.y>self.pos.y and cursor.pos.y<self.pos.y+self.height and not self.isLocked:
            self.isHovered = True
            if cursor.eventType=='left' and cursor.isClicking and (self.draggingPanel and cursor.selectedElement == None):
                self.set_isActive(True)
                cursor.selectedElement = self
                panels.remove(self)
                panels.append(self)
        else:
            self.isHovered = False
            if cursor.eventType=='left' and not(self.draggingPanel):
                self.set_isActive(False)
                if cursor.selectedElement == self:
                    cursor.selectedElement = None

        if self.barFirstClickPos != Vector2.ZERO():
            self.pos = Vector2(cursor.pos.x+self.barFirstClickPos.x, cursor.pos.y+self.barFirstClickPos.y)
            # Post-update position
            if self.pos.x<0: self.pos.x=0
            if self.pos.x+2>camera.w: self.pos.x = camera.w-2
            if self.pos.y<0: self.pos.y=0
            if self.pos.y+2>camera.h: self.pos.y = camera.h-2

    def update_components(self, panels):
        for i in range(len(self.components.values())):
            comp = list(self.components.values())[i]
            comp.pos = self.componentPosOffsets[i]+self.pos
            comp.update()
            if comp.isActive:
                if 'closeButton' in self.components.keys() and comp==self.components['closeButton']:
                    panels.remove(self)
                elif 'runButton' in self.components.keys() and comp==self.components['runButton']:
                    for panel in panels:
                        if panel.get_type()=='Panel.TextPanel':
                            # executing code of entry text widgets
                            for i in range(len(panel.components.values())):
                                comp = list(panel.components.values())[i]
                                if comp.get_type() == 'Selectable.TextEntry':
                                    code = comp.get_text()
                                    try:
                                        exec(code)
                                    except:
                                        print('Error: unable to run panel code')

    def update_labels(self):
        for i in range(len(self.labels)):
            self.labels[i].position = self.pos+self.labelPosOffsets[i]

    def draw(self, screen):
        pygame.draw.rect(screen, tuple(self.outlineColor), (self.pos.x-1, self.pos.y-1, self.width+2, self.height+2))
        pygame.draw.rect(screen, tuple(self.bgColor), (self.pos.x, self.pos.y, self.width, self.height))
        if self.hasBar:
            pygame.draw.rect(screen, tuple(self.barColor), (self.pos.x, self.pos.y, self.barWidth, self.barHeight))

        for comp in self.components.values():
            comp.draw(screen)
        for l in self.labels:
            l.draw(screen, text=l.text)

    def get_type(self):
        return 'Panel'

class TextPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='Console', font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x'),
                           'runButton':Button(Vector2(self.pos.x+self.width-90, self.pos.y), Vector2(40,self.barHeight), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2], img=load_sprite('ui/runIcon')),
                           'textEntry':TextEntry(Vector2(self.pos.x, self.pos.y+self.barHeight),Vector2(int(int(self.width)), self.height-self.barHeight))}
        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.TextPanel'

class TopNavPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'runButton':Button(Vector2(self.pos.x, self.pos.y), Vector2(40,40), idleColor=colors[1], hoveredColor=colors[2], selectedColor=colors[2], img=load_sprite('ui/runIcon')),
                           'componentsButton':Button(Vector2(self.pos.x+40, self.pos.y), Vector2(40,40), idleColor=colors[1], hoveredColor=colors[2], selectedColor=colors[2], img=load_sprite('ui/NEWcomponentsIcon')),
                           'IDEButton':Button(Vector2(self.pos.x+80, self.pos.y), Vector2(40,40), idleColor=colors[1], hoveredColor=colors[2], selectedColor=colors[2], img=load_sprite('ui/NEWIDEIcon')),
                           'HomeButton':Button(Vector2(self.pos.x+120, self.pos.y), Vector2(40,40), idleColor=colors[1], hoveredColor=colors[2], selectedColor=colors[2], img=load_sprite('ui/NEWhomeIcon'))}
        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.TopNavPanel'
