import pygame, copy, sys
from scripts.parser.parse import parse
from scripts.parser.pseudocode import get_code, get_game_state, set_game_state, set_code
from scripts.parser.user_print import user_print
from scripts.parser.exception_handler import handle_exception
from scripts.ui.label import Label
from scripts.ui.widgets.button import Button
from scripts.ui.widgets.textEntry import TextEntry
from scripts.components.shapes import defaultShapes
from scripts.math.vector2 import Vector2
from scripts.math.camera import camera
from scripts.graphics.color import RGB, gradient_palette
from scripts.graphics.spriteManager import load_sprite
from scripts.cursor import cursor
from lang.lang import getText

defaultPalette = gradient_palette(RGB(48,48,48),step=15,len_=2)

class CommonLang:
    def __init__(self,lang):
        self.lang=lang

    def changeLang(self,language):
        self.lang=language

    def getLang(self):
        return self.lang

lang=CommonLang("fr")

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
    
    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)

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
                count = 0
                for i in range(panels.index(self)+1, len(panels)):
                    if pygame.Rect(panels[i].pos.x,panels[i].pos.y,panels[i].width,panels[i].height).collidepoint((cursor.pos.x,cursor.pos.y)):
                        count += 1
                if count ==0:
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
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name=getText('text.console',lang.getLang()), font='RobotoMono-Regular', hasBar=True):
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
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name=getText('text.add_a_component',lang.getLang()), font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        self.name = getText('text.add_a_component',lang.getLang())
        self.labels = [Label(Vector2(self.pos.x+7, self.pos.y+2), size=17, text=self.name, font=font)]
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
        self.components = {'Logo': Button(Vector2(camera.w_2,camera.h_2-370), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],img = load_sprite('logo')),
                           'ResumeButton':Button(Vector2(camera.w_2-140,camera.h_2-250), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.resume',lang.getLang()), textSize=35),
                           'LoadDeviceButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.load_device',lang.getLang()), textSize=23),
                           'NewDeviceButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.new_device',lang.getLang()), textSize=28),
                           'SettingsButton':Button(Vector2(camera.w_2-140,camera.h_2+50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.settings',lang.getLang()), textSize=35),
                           'CreditsButton':Button(Vector2(camera.w_2-140,camera.h_2+150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.credits',lang.getLang()), textSize=35),
                           'QuitButton':Button(Vector2(camera.w_2-140,camera.h_2+250), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.quit',lang.getLang()), textSize=35)}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.MenuPanel'


class SettingsPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text= getText('button.settings',lang.getLang()), textSize=55),
                           'LangButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.language',lang.getLang()), textSize=35),
                           'KeyboardButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.keyboard',lang.getLang()), textSize=35),
                           'BackButton':Button(Vector2(camera.w_2-140,camera.h_2+50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.back',lang.getLang()), textSize=35)}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.MenuPanel'

class LangPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text= getText('button.language',lang.getLang()), textSize=55),
                           'frButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'Français', textSize=35),
                           'enButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'English', textSize=35),}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.LangPanel'

class KeyboardPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text=getText('button.keyboard',lang.getLang()), textSize=55),
                           'azertyButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'AZERTY', textSize=35),
                           'qwertyButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= 'QWERTY', textSize=35),}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.KeyboardPanel'

class CreditsPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Credits': Button(Vector2(camera.w_2,camera.h_2), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],img = load_sprite('credits/'+lang.getLang())),
                           'Logo': Button(Vector2(camera.w_2,camera.h_2-370), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],img = load_sprite('logo')),
                           'BackButton':Button(Vector2(camera.w_2-140,camera.h_2+250), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text= getText('button.back',lang.getLang()), textSize=35),}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    

    def get_type(self):
        return 'Panel.CreditsPanel'
    
def update_panel_buttons(panels, shapes):
    doBreak = False

    for k in range(len(panels)):
        panel = panels[k]
        for j in range(k+1, len(panels)):
            if panels[j].get_rect().collidepoint((cursor.pos.x, cursor.pos.y)):
                break
        else:
            for i in range(len(panel.components.values())):
                comp = list(panel.components.values())[i]
                if 'Button' in comp.get_type() and comp.is_pressed and comp.isActive:
                    if ('closeButton' in panel.components.keys() and comp==panel.components['closeButton']) or ('ResumeButton' in panel.components.keys() and comp==panel.components['ResumeButton']):
                        panels.remove(panel)
                    elif 'runButton' in panel.components.keys() and comp==panel.components['runButton']:
                        for panel in panels:
                            if panel.get_type()=='Panel.TextPanel':
                                # executing code of entry text widgets
                                try:
                                    if not get_game_state():
                                        for i in range(len(panel.components.values())):
                                                comp = list(panel.components.values())[i]
                                                if comp.get_type() == 'Selectable.TextEntry':
                                                    code = r'{}'.format(comp.get_text())
                                                    parse(code, shapes)
                                                    set_game_state(True)
                                    else: # >>end execution
                                        set_code('','','')
                                        set_game_state(False)
                                except Exception as e:
                                    user_print(handle_exception(e))
                    elif 'componentsButton' in panel.components.keys() and comp==panel.components['componentsButton']:
                        panels.append(AddComponentPanel(Vector2(0,0), Vector2(400,365)))
                    elif 'IDEButton' in panel.components.keys() and comp==panel.components['IDEButton']:
                        panels.append(TextPanel(Vector2(0,0), Vector2(500,500)))

                    # -- main menu --
                    elif 'HomeButton' in panel.components.keys() and comp==panel.components['HomeButton']:
                        panels.append(MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'SettingsButton' in panel.components.keys() and comp==panel.components['SettingsButton']:
                        panels.remove(panel)
                        panels.append(SettingsPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'CreditsButton' in panel.components.keys() and comp==panel.components['CreditsButton']:
                        panels.remove(panel)
                        panels.append(CreditsPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'QuitButton' in panel.components.keys() and comp==panel.components['QuitButton']:
                        pygame.quit()
                        sys.exit()

                    # -- options menu --
                    elif 'LangButton' in panel.components.keys() and comp==panel.components['LangButton']:
                        panels.remove(panel)
                        panels.append(LangPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'KeyboardButton' in panel.components.keys() and comp==panel.components['KeyboardButton']:
                        panels.remove(panel)
                        panels.append(KeyboardPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'BackButton' in panel.components.keys() and comp==panel.components['BackButton']:
                        panels.remove(panel)
                        panels.append(MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))

                    # -- lang menu --
                    elif 'frButton' in panel.components.keys() and comp==panel.components['frButton']:
                        panels.remove(panel)
                        lang.changeLang('fr')
                    elif 'enButton' in panel.components.keys() and comp==panel.components['enButton']:
                        panels.remove(panel)
                        lang.changeLang('en')

                    # -- keyboard menu --
                    elif 'azertyButton' in panel.components.keys() and comp==panel.components['azertyButton']:
                        panels.remove(panel)
                        isKeyboardAzerty = True
                    elif 'qwertyButton' in panel.components.keys() and comp==panel.components['qwertyButton']:
                        panels.remove(panel)
                        isKeyboardAzerty = False

                    else:
                        for c in panel.components.keys():
                            if 'shape' in c and comp == panel.components[c]:
                                shapes.append(copy.copy(defaultShapes[int(c.replace('shape',''))]))
            break
