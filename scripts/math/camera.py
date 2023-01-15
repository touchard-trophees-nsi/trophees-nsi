import ctypes
from scripts.math.vector2 import Vector2
user32 = ctypes.windll.user32

class Camera:
    def __init__(self):
        self.pos = Vector2(0,0)
        self.vel = Vector2(0,0)
        self.w, self.h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.w_2 = int(self.w/2)
        self.h_2 = int(self.h/2)
        self.cen = (self.w_2, self.h_2)
        
    def update(self, player, ts):
        self.pos += self.vel
camera = Camera()