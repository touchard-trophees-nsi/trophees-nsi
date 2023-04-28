import pygame, copy, sys
from os import listdir
from os.path import isfile, join
from scripts.parser.parse import parse
from scripts.parser.pseudocode import set_code, get_code, get_game_state, set_game_state, stop_game
from scripts.parser.user_print import user_print
from scripts.parser.exception_handler import handle_exception
from scripts.ui.label import Label
from scripts.ui.labelHighlighting.coloredLabel import ColoredLabel
from scripts.ui.widgets.button import Button
from scripts.ui.widgets.textEntry import TextEntry, HorizontalTextEntry
from scripts.math.vector2 import Vector2
from scripts.math.camera import camera
from scripts.graphics.color import RGB, gradient_palette
from scripts.graphics.spriteManager import load_sprite
from scripts.cursor import cursor
from scripts.file_handler import load_device, save_device_as
from scripts.dev import dprint
from lang.lang import getText
# -------- #
# ---------#
from scripts.components.PCB import PCB
from scripts.components.processing.CPU import CPU
from scripts.components.processing.videochip import VideoChip
from scripts.components.output.screen import Screen
from scripts.components.input.pressButton import PressButton
from scripts.components.input.directionalButton import DirectionalButton

class CommonLang:
    def __init__(self,lang):
        self.lang=lang

    def changeLang(self,language):
        self.lang=language

    def getLang(self):
        return self.lang

lang=CommonLang("fr")

defaultShapes = {
    'PCB':PCB(Vector2(61,61),Vector2(300,300)),
    'CPU':CPU(Vector2(61,61),Vector2(80,80)),
    'Video Chip':VideoChip(Vector2(61,61),Vector2(80,40)),
    'Screen':Screen(Vector2(61,61),Vector2(170,170)),
   'Simple Button':PressButton(Vector2(61,61),Vector2(50,50)),
    'Directional Button':DirectionalButton(Vector2(61,61),Vector2(120,120))
}
    
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
        self.components = {'saveMenuButton':Button(Vector2(self.pos.x, self.pos.y), Vector2(40,40), idleColor=colors[1], hoveredColor=colors[2], selectedColor=colors[2], img=load_sprite('ui/NEWsaveIcon')),
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
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x')}

        names = list(defaultShapes.keys())
        for i in range(len(defaultShapes)):
            self.components['shape_ '+names[i]] = Button(Vector2(self.pos.x+10, self.pos.y+self.barHeight+32*i+10), Vector2(250, 27), text=getText('button.add',lang.getLang())+names[i], textSize=13)

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)
    
    def update(self, panels, shapes):
        Panel.update(self, panels, shapes)
        if get_game_state():
            panels.remove(self)

    def get_type(self):
        return 'Panel.AddComponentPanel'

class SavePanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name=getText('button.save',lang.getLang()), font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        self.name = getText('button.save',lang.getLang())
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x'),
                           'saveTextEntry':HorizontalTextEntry(Vector2(self.pos.x+150, self.pos.y+self.barHeight+15), Vector2(240,20), text='Appareil_1'),
                           'saveButton':Button(Vector2(self.pos.x+int(self.width/2)-100, self.pos.y+self.barHeight+45), Vector2(200,20), textSize=15, text=getText('button.save',lang.getLang()),)}
        self.labels.append(Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+15),size=15,text=getText('text.file_name',lang.getLang())))
        self.labelPosOffsets.append(Vector2(7,self.barHeight+15))

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

# --------------------- #
# ----- MAIN MENU ----- #
# --------------------- #

class MenuPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Logo': Button(Vector2(camera.w_2,camera.h_2-370), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],img = load_sprite('logo')),
                           'LoadDeviceButton':Button(Vector2(camera.w_2-140,camera.h_2-250), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.load_device',lang.getLang()), textSize=23),
                           'NewDeviceButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.new_device',lang.getLang()), textSize=28),
                           'SettingsButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.settings',lang.getLang()), textSize=35),
                           'CreditsButton':Button(Vector2(camera.w_2-140,camera.h_2+50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.credits',lang.getLang()), textSize=35),
                           'QuitButton':Button(Vector2(camera.w_2-140,camera.h_2+150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.quit',lang.getLang()), textSize=35)}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.MenuPanel'

class SettingsPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text=getText('button.settings',lang.getLang()), textSize=55),
                           'LangButton':Button(Vector2(camera.w_2-140,camera.h_2-150), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.language',lang.getLang()), textSize=35),
                           'KeyboardButton':Button(Vector2(camera.w_2-140,camera.h_2-50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.keyboard',lang.getLang()), textSize=35),
                           'BackButton':Button(Vector2(camera.w_2-140,camera.h_2+50), Vector2(280,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=getText('button.back',lang.getLang()), textSize=35)}

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

    def get_type(self):
        return 'Panel.MenuPanel'

class LangPanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text=getText('button.language',lang.getLang()), textSize=55),
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

class LoadDevicePanel(Panel):
    def __init__(self, pos, dims, bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        colors = gradient_palette(self.barColor, step=-15)
        self.components = {'Title': Button(Vector2(camera.w_2,camera.h_2-250), Vector2(0,0), idleColor=colors[1], hoveredColor=colors[1], selectedColor=colors[1],text=getText('button.load_device',lang.getLang()), textSize=55)}
        files = [str(file) for file in listdir('data/') if isfile(join('data/',file))]
        text_size = 35
        for i in range(len(files)):
            display_text = files[i].replace('.pkl','')
            self.components['device'+str(i)] = Button(Vector2(camera.w_2-300,camera.h_2-150+i*100), Vector2(600,75), idleColor=colors[0], hoveredColor=colors[1], selectedColor=colors[2],text=display_text, textSize=text_size)

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)
    
    def get_type(self):
        return 'Panel.LoadDevicePanel'
    

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


# ----- RIGHT CLICK PANELS ----- #
# ------------------------------ #

class DefaultRightClickPanel(Panel):
    def __init__(self, pos, parent, dims=Vector2(200,92), bgColor=defaultPalette[0], barColor=defaultPalette[1], name='', font='RobotoMono-Regular', hasBar=False):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        self.components = {'deleteButton': Button(Vector2.ZERO(), Vector2(200,30), idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[1],text=getText('button.delete',lang.getLang()), textSize=18),
                           'rotateButton': Button(Vector2(0,31), Vector2(200,30), idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[1],text=getText('button.rotate',lang.getLang()), textSize=18),
                           'propertiesButton': Button(Vector2(0,62), Vector2(200,30), idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[1],text=getText('button.characteristics',lang.getLang()), textSize=18)}
        self.parent = parent
        self.componentPosOffsets = [Vector2.ZERO(), Vector2(0,31), Vector2(0,62)]

        cursor.selectedElement = self
    
    def update(self, panels, shapes):
        Panel.update(self, panels, shapes)
        if (cursor.eventType=='left' and not self.get_rect().collidepoint(cursor.pos.x, cursor.pos.y)) or get_game_state():
            panels.remove(self)

    def get_type(self):
        return 'Panel.DefaultRightClickPanel'

class DefaultPropertiesPanel(Panel):
    def __init__(self, pos, parent, dims=Vector2(400,110), bgColor=defaultPalette[0], barColor=defaultPalette[1], name=getText('button.characteristics',lang.getLang()), font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        self.name = getText('button.characteristics',lang.getLang())
        self.parent = parent
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x'),
                           'idTextEntry':HorizontalTextEntry(Vector2(self.pos.x+150, self.pos.y+self.barHeight+15), Vector2(240,20), text=parent.get_ID()),
                           'saveDefaultPropertiesButton':Button(Vector2(self.pos.x+int(self.width/2)-100, self.pos.y+self.barHeight+45), Vector2(200,20), textSize=15, text=getText('button.save',lang.getLang()))}
        self.labels.append(Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+15),size=15,text=getText('button.id_internal',lang.getLang())))
        self.labelPosOffsets.append(Vector2(7,self.barHeight+15))

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

class ScreenPropertiesPanel(Panel):
    def __init__(self, pos, parent, dims=Vector2(400,170), bgColor=defaultPalette[0], barColor=defaultPalette[1], name=getText('button.characteristics',lang.getLang()), font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        self.name = getText('button.characteristics',lang.getLang())
        self.parent = parent
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x'),
                           'idTextEntry':HorizontalTextEntry(Vector2(self.pos.x+150, self.pos.y+self.barHeight+15), Vector2(240,20), text=parent.get_ID()),
                           'dimensionsTextEntry':HorizontalTextEntry(Vector2(self.pos.x+150, self.pos.y+self.barHeight+45), Vector2(240,20), text=str(self.parent.size.x)+'x'+str(self.parent.size.y)),
                           'videochipTextEntry':HorizontalTextEntry(Vector2(self.pos.x+150, self.pos.y+self.barHeight+75), Vector2(240,20), text=self.parent.get_videoChipID()),
                           'saveScreenPropertiesButton':Button(Vector2(self.pos.x+int(self.width/2)-100, self.pos.y+self.barHeight+110), Vector2(200,20), textSize=15, text=getText('button.save',lang.getLang()))}
        labels_ = [Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+15),size=15,text=getText('button.id_internal',lang.getLang())),
                  Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+45),size=15,text=getText('button.size',lang.getLang())),
                  Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+75),size=15,text=getText('button.id_video',lang.getLang()))]
        labelOffsets_ = [Vector2(7,self.barHeight+15),Vector2(7,self.barHeight+45),Vector2(7,self.barHeight+75)]
        for l in labels_: self.labels.append(l)
        for lo in labelOffsets_: self.labelPosOffsets.append(lo)

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

class PCBPropertiesPanel(Panel):
    def __init__(self, pos, parent, dims=Vector2(440,170), bgColor=defaultPalette[0], barColor=defaultPalette[1], name=getText('button.characteristics',lang.getLang()), font='RobotoMono-Regular', hasBar=True):
        super().__init__(pos, dims, bgColor, barColor, name, font, hasBar)
        self.name = getText('button.characteristics',lang.getLang())
        self.parent = parent
        self.components = {'closeButton':Button(Vector2(self.pos.x+self.width-50, self.pos.y), Vector2(50,self.barHeight), idleColor=self.barColor, hoveredColor=RGB(255,50,50), selectedColor=RGB(255,50,50), text='x'),
                           'idTextEntry':HorizontalTextEntry(Vector2(self.pos.x+190, self.pos.y+self.barHeight+15), Vector2(240,20), text=parent.get_ID()),
                           'dimensionsTextEntry':HorizontalTextEntry(Vector2(self.pos.x+190, self.pos.y+self.barHeight+45), Vector2(240,20), text=str(self.parent.size.x)+'x'+str(self.parent.size.y)),
                           'colorTextEntry':HorizontalTextEntry(Vector2(self.pos.x+190, self.pos.y+self.barHeight+75), Vector2(240,20), text=str(self.parent.displayColor)),
                           'savePCBPropertiesButton':Button(Vector2(self.pos.x+int(self.width/2)-100, self.pos.y+self.barHeight+110), Vector2(200,20), textSize=15, text=getText('button.save',lang.getLang()))}
        
        labels_ = [Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+15),size=15,text=getText('button.id_internal',lang.getLang())),
                  Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+45),size=15,text=getText('button.size',lang.getLang())),
                  Label(Vector2(self.pos.x+7, self.pos.y+self.barHeight+75),size=15,text=getText('button.color',lang.getLang()))]
        labelOffsets_ = [Vector2(7,self.barHeight+15),Vector2(7,self.barHeight+45),Vector2(7,self.barHeight+75)]
        for l in labels_: self.labels.append(l)
        for lo in labelOffsets_: self.labelPosOffsets.append(lo)

        self.componentPosOffsets = []
        for comp in self.components.values():
            self.componentPosOffsets.append(comp.pos-self.pos)

def update_panel_buttons(panels, shapes):
    toRemove = []
    for k in range(len(panels)):
        panel = panels[k]
        for j in range(k+1, len(panels)):
            if panels[j].get_rect().collidepoint((cursor.pos.x, cursor.pos.y)):
                break
        else:
            for i in range(len(panel.components.values())):
                comp = list(panel.components.values())[i]
                if 'Button' in comp.get_type() and comp.is_pressed and comp.isActive:
                    if ('closeButton' in panel.components.keys() and comp==panel.components['closeButton']):
                        if panel.get_type() == 'Panel.TextPanel':
                            for shape in shapes:
                                if 'CPU' in shape.get_type():
                                    shape.set_code(panel.components['textEntry'].content)
                        toRemove.append(panel)
                    elif 'runButton' in panel.components.keys() and comp==panel.components['runButton']:
                        if panel.get_type()=='Panel.TextPanel':
                            # executing code of entry text widgets
                            try:
                                if not get_game_state():
                                    for i in range(len(panel.components.values())):
                                            comp = list(panel.components.values())[i]
                                            if comp.get_type() == 'Selectable.TextEntry':
                                                code = r'{}'.format(comp.get_text())
                                                check = parse(code, shapes)
                                                if check!=None:
                                                    set_game_state(True)
                                                else:
                                                    user_print(getText('text.attach_cpu',lang.getLang()))       
                                else: # >>end execution
                                    stop_game()
                            except Exception as e:
                                user_print(handle_exception(e))
                    elif 'componentsButton' in panel.components.keys() and comp==panel.components['componentsButton']:
                        for panel_ in panels:
                            if 'AddComponentPanel' in panel_.get_type():
                                toRemove.append(panel_)
                                break
                        else:
                            panels.append(AddComponentPanel(Vector2(120,120), Vector2(280,240)))     
                    elif 'IDEButton' in panel.components.keys() and comp==panel.components['IDEButton']:
                        for panel_ in panels:
                            if 'TextPanel' in panel_.get_type():
                                toRemove.append(panel_)
                                break
                        else:
                            panels.append(TextPanel(Vector2(120,120), Vector2(500,500)))
                            for shape in shapes:
                                if 'CPU' in shape.get_type():                              
                                    panels[-1].components['textEntry'].content = shape.get_code()
                                    for i in range(len(panels[-1].components['textEntry'].content)):
                                            panels[-1].components['textEntry'].labels.append(ColoredLabel(Vector2(0,0), size=15, text='', centered=False))
                                    panels[-1].components['textEntry'].update_labels()
                    elif 'saveMenuButton' in panel.components.keys() and comp==panel.components['saveMenuButton']:
                        for panel_ in panels:
                            if 'SavePanel' in panel_.get_type():
                                toRemove.append(panel_)
                                break
                        else:
                            panels.append(SavePanel(Vector2(0,0), Vector2(400,110)))
                    elif 'saveButton' in panel.components.keys() and comp==panel.components['saveButton']:
                        save_device_as(panel.components['saveTextEntry'].content[0], shapes)
                        toRemove.append(panel)
                    elif 'deleteButton' in panel.components.keys() and comp==panel.components['deleteButton']:
                        toRemove.append(panel)
                        shapes.remove(panel.parent)
                    elif 'rotateButton' in panel.components.keys() and comp==panel.components['rotateButton']:
                        toRemove.append(panel)
                        
                        for s in range(len(shapes)):
                            if shapes[s] == panel.parent:
                                shapes[s].rotate()
                                break
                    elif 'propertiesButton' in panel.components.keys() and comp==panel.components['propertiesButton']:
                        if 'Screen' in panel.parent.get_type():
                            panels.append(ScreenPropertiesPanel((cursor.pos), panel.parent))
                        elif 'PCB' in panel.parent.get_type():
                            panels.append(PCBPropertiesPanel((cursor.pos), panel.parent))
                        else:
                            panels.append(DefaultPropertiesPanel((cursor.pos), panel.parent))
                    elif 'saveDefaultPropertiesButton' in panel.components.keys() and comp==panel.components['saveDefaultPropertiesButton']:
                        try:
                            panel.parent.set_ID(panel.components['idTextEntry'].content[0])
                            user_print(getText('text.save_success',lang.getLang()))
                            toRemove.append(panel)
                        except:
                            user_print(getText('text.invalid_field',lang.getLang()))
                    elif 'saveScreenPropertiesButton' in panel.components.keys() and comp==panel.components['saveScreenPropertiesButton']:
                        try:
                            #
                            panel.parent.set_ID(panel.components['idTextEntry'].content[0])
                            #
                            dimensions = panel.components['dimensionsTextEntry'].content[0].split('x')
                            panel.parent.set_dimensions(int(dimensions[0]), int(dimensions[1]))
                            #
                            panel.parent.set_videoChipID(panel.components['videochipTextEntry'].content[0])
                            user_print(getText('text.save_success',lang.getLang()))
                            toRemove.append(panel)
                        except:
                            user_print(getText('text.invalid_field',lang.getLang()))
                    elif 'savePCBPropertiesButton' in panel.components.keys() and comp==panel.components['savePCBPropertiesButton']:
                        try:
                            panel.parent.set_ID(panel.components['idTextEntry'].content[0])
                            dimensions = panel.components['dimensionsTextEntry'].content[0].split('x')
                            panel.parent.set_dimensions(int(dimensions[0]), int(dimensions[1]))
                            color_str = panel.components['colorTextEntry'].content[0]
                            color = tuple(int(x) for x in color_str[1:-1].split(','))
                            _ = pygame.Color(*color)
                            panel.parent.displayColor = color
                            user_print(getText('text.save_success',lang.getLang()))
                            toRemove.append(panel)
                        except:
                            user_print(getText('text.invalid_field',lang.getLang()))

                    # ------------------------- #
                    # ------- main menu ------- #
                    # ------------------------- #

                    elif 'NewDeviceButton' in panel.components.keys() and comp==panel.components['NewDeviceButton']:
                        # clearing shapes
                        while len(shapes)>0:
                            shapes.pop()
                        # clearing panels:
                        for panel in panels:
                            if 'TopNavPanel' not in panel.get_type():
                                toRemove.append(panel) 
                        # going back to editing
                        for panel in panels:
                            if 'MenuPanel' in panel.get_type():
                                toRemove.append(panel)
                    elif 'LoadDeviceButton' in panel.components.keys() and comp==panel.components['LoadDeviceButton']:
                        panels.append(LoadDevicePanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'HomeButton' in panel.components.keys() and comp==panel.components['HomeButton']:
                        set_game_state(False)
                        panels.append(MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'SettingsButton' in panel.components.keys() and comp==panel.components['SettingsButton']:
                        toRemove.append(panel)
                        panels.append(SettingsPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'CreditsButton' in panel.components.keys() and comp==panel.components['CreditsButton']:
                        panels.append(CreditsPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'QuitButton' in panel.components.keys() and comp==panel.components['QuitButton']:
                        pygame.quit()
                        sys.exit()

                    # -- options menu --
                    elif 'LangButton' in panel.components.keys() and comp==panel.components['LangButton']:
                        toRemove.append(panel)
                        panels.append(LangPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'KeyboardButton' in panel.components.keys() and comp==panel.components['KeyboardButton']:
                        toRemove.append(panel)
                        panels.append(KeyboardPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))
                    elif 'BackButton' in panel.components.keys() and comp==panel.components['BackButton']:
                        toRemove.append(panel)
                        panels.append(MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])))

                    # -- lang menu --
                    elif 'frButton' in panel.components.keys() and comp==panel.components['frButton']:
                        toRemove.append(panel)
                        lang.changeLang('fr')
                    elif 'enButton' in panel.components.keys() and comp==panel.components['enButton']:
                        toRemove.append(panel)
                        lang.changeLang('en')

                    # -- keyboard menu --
                    elif 'azertyButton' in panel.components.keys() and comp==panel.components['azertyButton']:
                        toRemove.append(panel)
                        isKeyboardAzerty = True
                    elif 'qwertyButton' in panel.components.keys() and comp==panel.components['qwertyButton']:
                        toRemove.append(panel)
                        isKeyboardAzerty = False

                    else:
                        for c in panel.components.keys():
                            if 'shape_' in c and comp == panel.components[c]:
                                c = c[7:]
                                defaultShapes[c].pickle_check()
                                shapes.append(copy.deepcopy(defaultShapes[c]))
                            elif 'device' in c and comp == panel.components[c]:
                                # loading device
                                files = [str(file) for file in listdir('data/') if isfile(join('data/',file))]
                                shapes_ = load_device(files[int(c.replace('device',''))].replace('.pkl',''))
                                while len(shapes)>0:
                                    shapes.pop()
                                for shape in shapes_: shapes.append(shape)

                                # clearing panels:
                                for panel in panels:
                                    if 'TopNavPanel' not in panel.get_type():
                                        toRemove.append(panel) 
            break
    for panel in toRemove:
        try:
            panels.remove(panel)
        except: pass
