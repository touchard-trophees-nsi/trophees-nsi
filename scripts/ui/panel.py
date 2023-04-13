import pygame, copy, sys
from scripts.ui.label import Label
from scripts.ui.widgets.button import Button
from scripts.ui.widgets.textEntry import TextEntry
from scripts.components.shapesDrawer import defaultShapes
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

    def update(self, panels, shapes):
        self.update_physics(panels)
        self.update_components(panels, shapes)
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

    def update_components(self, panels, shapes):

        for i in range(len(self.components.values())):
            comp = list(self.components.values())[i]
            comp.pos = self.componentPosOffsets[i]+self.pos
            comp.update()
            if comp.isActive:
                if ('closeButton' in self.components.keys() and comp==self.components['closeButton']) or ('ResumeButton' in self.components.keys() and comp==self.components['ResumeButton']):
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
                elif 'componentsButton' in self.components.keys() and comp==self.components['componentsButton']:
                    panels.append(AddComponentPanel(Vector2(0,0), Vector2(400,365)))
                elif 'IDEButton' in self.components.keys() and comp==self.components['IDEButton']:
                    panels.append(TextPanel(Vector2(0,0), Vector2(500,500)))

                # -- main menu --
                elif 'HomeButton' in self.components.keys() and comp==self.components['HomeButton']:
                    panels.append(MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                elif 'SettingsButton' in self.components.keys() and comp==self.components['SettingsButton']:
                    panels.remove(self)
                    panels.append(SettingsPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                elif 'QuitButton' in self.components.keys() and comp==self.components['QuitButton']:
                    pygame.quit()
                    sys.exit()

                # -- options menu --
                elif 'LangButton' in self.components.keys() and comp==self.components['LangButton']:
                    panels.remove(self)
                    panels.append(LangPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                elif 'KeyboardButton' in self.components.keys() and comp==self.components['KeyboardButton']:
                    panels.remove(self)
                    panels.append(KeyboardPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                elif 'BackButton' in self.components.keys() and comp==self.components['BackButton']:
                    panels.remove(self)
                    panels.append(MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))

                # -- lang menu --
                elif 'frButton' in self.components.keys() and comp==self.components['frButton']:
                    panels.remove(self)
                    lang = 'fr'
                elif 'enButton' in self.components.keys() and comp==self.components['enButton']:
                    panels.remove(self)
                    lang = 'en'

                # -- keyboard menu --
                elif 'azertyButton' in self.components.keys() and comp==self.components['azertyButton']:
                    panels.remove(self)
                    isKeyboardAzerty = True
                elif 'qwertyButton' in self.components.keys() and comp==self.components['qwertyButton']:
                    panels.remove(self)
                    isKeyboardAzerty = False
                    
                else:
                    for c in self.components.keys():
                        if 'shape' in c and comp == self.components[c]:
                            shapes.append(copy.copy(defaultShapes[int(c.replace('shape',''))]))

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

class AddComponentPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='Ajouter un composant', font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x')}

        for i in range(len(defaultShapes)):
            self.components['shape'+str(i)] = Button(Vector2(self.pos.x+10, self.pos.y+self.barHeight+32*i+10), Vector2(185, 27), text='Ajouter composant', textSize=13)

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.AddComponentPanel'

class MenuPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-350), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text= 'Menu', textSize=55),
                           'ResumeButton':Button(Vector2(camera.w_2-140,camera.h_2-250), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Reprendre', textSize=35),
                           'LoadDeviceButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Charger un appareil', textSize=23),
                           'NewDeviceButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Nouvel appareil', textSize=28),
                           'SettingsButton':Button(Vector2(camera.w_2-140,camera.h_2+50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Options', textSize=35),
                           'CreditsButton':Button(Vector2(camera.w_2-140,camera.h_2+150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Crédits', textSize=35),
                           'QuitButton':Button(Vector2(camera.w_2-140,camera.h_2+250), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Quitter', textSize=35)}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.MenuPanel'


class SettingsPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text= 'Options', textSize=55),
                           'LangButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Langue', textSize=35),
                           'KeyboardButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Clavier', textSize=35),
                           'BackButton':Button(Vector2(camera.w_2-140,camera.h_2+50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Retour', textSize=35)}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.MenuPanel'      
        
class LangPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text= 'Langue', textSize=55),
                           'frButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Français', textSize=35),
                           'enButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Anglais', textSize=35),}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.LangPanel'   

class KeyboardPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text= 'Clavier', textSize=55),
                           'azertyButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'AZERTY', textSize=35),
                           'qwertyButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'QWERTY', textSize=35),}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.KeyboardPanel'   
