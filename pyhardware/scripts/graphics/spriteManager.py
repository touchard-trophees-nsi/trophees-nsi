from pygame import image

def load_sprite(path):
    path_ = '././sprites/'+path+('' if '.png' in path else '.png')
    return image.load(path)