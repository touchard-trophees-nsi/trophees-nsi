# TO-DO

# LATER: add suport for syntax highlighting when horizontally scrolling (strings & comments)
# LATER: selection highlight can't be drawn further than the panel boundaries
# LATER: add numbers highlight, string highlight should be ended with couples ('' or "" and not '" or "')

# MODULES
import pygame, sys
from scripts.cursor import cursor
from scripts.events import update_event, keys, key_update
from scripts.math.vector2 import Vector2, vectorize
from scripts.math.camera import camera
from scripts.ui.panel import AddComponentPanel, TextPanel, TopNavPanel, update_panel_buttons
from scripts.ui.grid import grid
from scripts.components.shapes import update_shape_dragging
from scripts.dev import dev_update_and_draw, dev_update, dprint
from scripts.parser.pseudocode import get_game_state, get_code, set_game_state, stop_game
from scripts.parser.user_print import user_print,dynamic_labels
from scripts.parser.exception_handler import handle_exception

IS_DEV = False
MAX_FPS = 60

# pygame setup
pygame.init()
pygame.display.init()
pygame.mixer.init()
pygame.display.set_caption('Micro Gadgets')
_SCREEN = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
#pygame.mouse.set_visible(0)

# variables & functions
panels = [MenuPanel(Vector2(0,0), Vector2(pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[0],pygame.display.set_mode((0,0), pygame.FULLSCREEN).get_size()[1])),AddComponentPanel(Vector2(120,120), Vector2(280,240)), TopNavPanel(Vector2(camera.w_2-80, 0), Vector2(160, 40))]
shapes = []
lastPressed = None
oldGameState = False
oldTimer = 0

def get_component_from_ID(ID):
    global shapes
    for shape in shapes:
        if shape.id == ID:
            if 'Screen' in shape.get_type():
                for shape_ in shapes:
                    if 'VideoChip' in shape_.get_type() and shape_.id == shape.get_videoChipID():
                        break
                else:
                    user_print('ID de la puce vidéo de {} inexistante'.format(shape.id))
                    set_game_state(False)
            return shape

# MAIN LOGIC
while True:
    # --- frame init --- #
    _SCREEN.fill((0,0,0))
    cursor.pos = vectorize(pygame.mouse.get_pos())
    currentFps = round(clock.get_fps(),1)
    dev_update(currentFps, MAX_FPS)

    # ----- instance updates ----- #
    cursor.update()

    try:
        if get_game_state() and oldGameState==False: # >>update loop
            # >>start execution
            exec(get_code()[0])
            oldTimer = 0
        elif get_game_state() and oldGameState==True:                                         
            exec(get_code()[1])
        elif not get_game_state() and oldTimer<2:
            exec(get_code()[2])
    except Exception as e:
        user_print(handle_exception(e))
        stop_game()
    oldGameState = get_game_state()
    if oldGameState == False and oldTimer<2:
        oldTimer += 1

    # ------- event handler ------- #
    for event in pygame.event.get():
        # KEY INPUTS
        update_event(event)

        # MOUSE INPUTS
        cursor.isClicking -= 1 if cursor.isClicking > 0 else 0
        cursor.isReleasing -= 1 if cursor.isReleasing > 0 else 0
        if event.type == pygame.MOUSEBUTTONUP:
            cursor.isReleasing = 1
            cursor.set_eventType(0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            cursor.isClicking = 1
            cursor.set_eventType(event.button)

            # SCROLLING
            if event.button==4: # scroll up
                if cursor.selectedElement != None and 'Selectable.TextEntry' in cursor.selectedElement.get_type() and cursor.selectedElement.displayedLines[0]>0:
                    cursor.selectedElement.displayedLines[0]-=1
                    cursor.selectedElement.displayedLines[1]-=1
                    cursor.selectedElement.update_labels()
            elif event.button==5: # scroll down
                if cursor.selectedElement != None and 'Selectable.TextEntry' in cursor.selectedElement.get_type() and cursor.selectedElement.displayedLines[0]<len(cursor.selectedElement.content)-1:
                    cursor.selectedElement.displayedLines[0]+=1
                    cursor.selectedElement.displayedLines[1]+=1
                    cursor.selectedElement.update_labels()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                IS_DEV = not IS_DEV #False if IS_DEV==False else True
            lastPressed = event.unicode
        elif event.type == pygame.KEYUP:
            lastPressed = None

    # ------- maintained key presses ------- #
    for key, values in keys.items():
        if values[0]>0:
            key_update(key, values[1], values[2])
            keys[key][0] += 1

    # ----- shape updates ----- #
    for shape in shapes:
        shape.update(shapes)
    update_shape_dragging(shapes, panels)
    #updateDrawer(shapes)

    # ----- panel updates ----- #
    update_panel_buttons(panels, shapes)
    for panel in panels:
        panel.update(panels, shapes)

    # ----- drawing ----- #
    grid(61,(20,20,20))
    grid(181,(80,80,80))

    for shape in shapes:
        if (shape.get_showWhenRunning() and get_game_state()) or not get_game_state():
            shape.draw(_SCREEN)
    for panel in panels:
        panel.draw(_SCREEN)
    for label in dynamic_labels:
        label.draw(_SCREEN, label.text)
        if label.color == (0,0,0): dynamic_labels.remove(label)

    if IS_DEV==True:
        dev_update_and_draw(_SCREEN, currentFps, MAX_FPS, lastPressed)

    # --- screen refreshing ---#
    pygame.display.update()
    clock.tick(MAX_FPS)
