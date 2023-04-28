from pygame.mouse import get_pos as get_mouse_pos
from scripts.math.vector2 import Vector2, vectorize

class Cursor:
    def __init__(self):
        self.pos = Vector2(0,0)
        self.isClicking = False
        self.isReleasing = False
        self.eventDic = {0:'none',1:'left',2:'middle',3:'right',4:'scroll_up',5:'scroll_down',6:'side1',7:'side2'}
        self.eventType = self.eventDic[0]
        # --- #
        self.selectedElement = None
    
    def set_eventType(self, type):
        if type<=7:
            self.eventType = self.eventDic[type]

    def update(self):
        self.pos = vectorize(get_mouse_pos())

cursor = Cursor()