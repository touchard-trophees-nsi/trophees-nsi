
from scripts.ui.dynamic_label import DynamicLabel
from scripts.math.camera import camera
from scripts.math.vector2 import Vector2

dynamic_labels = []
def user_print(text_):
    global dynamic_labels
    size_ = 16
    dynamic_labels.append(DynamicLabel(position=Vector2(2,camera.h-size_*1.5), velocity=Vector2.ZERO(), size=size_, text=str(text_), fade_speed=0.25))