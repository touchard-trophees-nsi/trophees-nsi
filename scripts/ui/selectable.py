from scripts.cursor import cursor
from scripts.graphics.color import RGB, gradient_palette

defaultPalette = gradient_palette(RGB(63,63,63),len_=3)
class Selectable:
    def __init__(self, pos, dims, idleColor=defaultPalette[0], hoveredColor=defaultPalette[1], selectedColor=defaultPalette[2], text='', keepActivity=False):
        self.pos = pos
        self.width, self.height = dims.x, dims.y
        self.text = text
        #
        self.colorPalette = {'idle':idleColor, 'hovered':hoveredColor, 'selected':selectedColor}
        self.color = self.colorPalette['idle']
        #
        self.isFrozen = False
        self.isHovered = False
        self.isActive = False
        self.isPressed = False
        self.keepActivity = keepActivity
        #
        self.continousClick = False

    def freeze(self):
        self.isFrozen = not self.isFrozen

    def update_color(self):
        self.color = self.colorPalette['selected'] if self.isActive else self.colorPalette['hovered'] if self.isHovered else self.colorPalette['idle']

    def base_update(self):
        if cursor.pos.x>=self.pos.x and cursor.pos.x<=self.pos.x+self.width and cursor.pos.y>=self.pos.y and cursor.pos.y<=self.pos.y+self.height and not self.isFrozen:
            self.isHovered = True
            if cursor.eventType=='left' and cursor.isClicking:
                self.isPressed = True
                cursor.selectedElement = self
                self.onClick()
                self.continousClick = True
            else:
                if not self.keepActivity:
                    self.isActive = False
                    if cursor.selectedElement==self:
                        cursor.selectedElement = None
                if self.isPressed:
                    self.isPressed = False
                    self.isActive = True
            if cursor.isReleasing:
                self.continousClick = False
                self.onRelease()
        else:
            self.isHovered = False
            if cursor.isClicking and cursor.eventType=='left':
                self.isActive = False
                if cursor.selectedElement==self:
                    cursor.selectedElement = None
        self.update_color()
        if self.continousClick:
            self.onContinuousClick()

    def onClick(self):
        pass

    def onContinuousClick(self):
        pass

    def onRelease(self):
        pass

    def get_type(self):
        return 'Selectable'
