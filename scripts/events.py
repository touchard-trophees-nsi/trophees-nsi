from cgitb import text
import pygame, sys
from scripts.cursor import cursor
from scripts.ui.widgets.textEntry import TextEntry
from lang.lang import isKeyboardAzerty
from lang.char_table import table
from scripts.version import PYGAME_IS_MODERN_VERSION

def shutdown():
    pygame.quit()
    sys.exit()

event2key = {pygame.K_LEFT: 'left',
              pygame.K_RIGHT: 'right',
              pygame.K_UP: 'up',
              pygame.K_DOWN: 'down',
              pygame.K_BACKSPACE: 'backspace',
              pygame.K_RETURN: 'return',
}


keys = {'right':[0,0,0,0],'up':[0,0,0,0],'left':[0,0,0,0],'down':[0,0,0,0],
        'backspace':[0,0,0,0],'return':[0,0,0,0]} # [0]:pressed time, [1]:isPressingShift, [2]:isPressingCtrl, [3]:move cooldown

for char in table:
    if char not in keys.items():
        keys[char] = [0,0,0,0]

def key_update(key, isPressingShift, isPressingCtrl):
        if (keys[key][0]==1 or keys[key][0]>20):
            if keys[key][3]==0:
                if key=='left':
                        cursor.selectedElement.move_cursor(-1, shift=isPressingShift, ctrl=isPressingCtrl)
                elif key=='right':
                    cursor.selectedElement.move_cursor(1, shift=isPressingShift, ctrl=isPressingCtrl)
                elif key=='up':
                    cursor.selectedElement.move_line(-1, shift=isPressingShift)
                elif key=='down':
                    cursor.selectedElement.move_line(1, shift=isPressingShift)
                elif key=='backspace':
                    cursor.selectedElement.backspace(ctrl=keys[key][2])
                elif key=='return':
                    cursor.selectedElement.add_return()
                elif key in keys.keys():
                    cursor.selectedElement.add_char(key, isManual=True)
                    print('Invalid direcitonal key')
                keys[key][3]+=1
            else:
                keys[key][3]=0

def key_press(key, isPressingShift, isPressingCtrl):
    keys[key][0]+=1 ; keys[key][1]=isPressingShift ; keys[key][2]=isPressingCtrl

def update_event(event):
    if event.type == pygame.KEYDOWN:
        # ----- APP SHUTDOWN ----- #
        if event.key == pygame.K_ESCAPE:
            shutdown()
        elif event.key == pygame.K_F3:
            return 'IS_DEV = not IS_DEV'

        # ----- EVENT MODS ----- #
        isPressingShift = True if event.mod & pygame.KMOD_SHIFT>0 else False
        isPressingCtrl = True if event.mod & pygame.KMOD_CTRL>0 else False
        isPressingAlt = True if event.mod & pygame.KMOD_ALT>0 else False

        # ----- ENTRY WRITING SYSTEM ----- #
        if cursor.selectedElement!=None and 'Selectable.TextEntry' in cursor.selectedElement.get_type():
            # --- Directional Keys
            if event.key == pygame.K_LEFT: keys['left'][0]+=1 ; keys['left'][1]=isPressingShift ; keys['left'][2]=isPressingCtrl
            elif event.key == pygame.K_RIGHT: keys['right'][0]+=1 ; keys['right'][1]=isPressingShift ; keys['right'][2]=isPressingCtrl
            elif event.key == pygame.K_UP: keys['up'][0]+=1 ; keys['up'][1]=isPressingShift ; keys['up'][2]=isPressingCtrl
            elif event.key == pygame.K_DOWN: keys['down'][0]+=1 ; keys['down'][1]=isPressingShift ; keys['down'][2]=isPressingCtrl
            # --- Shortcuts
                # copy
            if isPressingCtrl and event.key==pygame.K_c: cursor.selectedElement.clipboard_copy() ;
                # select all
            elif isPressingCtrl and not isKeyboardAzerty and event.key==pygame.K_a: cursor.selectedElement.select_all() ;
            elif isPressingCtrl and isKeyboardAzerty and event.key==pygame.K_q: cursor.selectedElement.select_all() ;
                # paste, cut
            elif isPressingCtrl and event.key==pygame.K_v: cursor.selectedElement.clipboard_paste()
            elif isPressingCtrl and event.key==pygame.K_x: cursor.selectedElement.clipboard_copy() ; cursor.selectedElement.backspace() ; print('cut')
            # --- Special Input
            elif event.key == pygame.K_BACKSPACE: key_press('backspace', isPressingShift, isPressingCtrl) #cursor.selectedElement.backspace(ctrl=isPressingCtrl)
            elif event.key == pygame.K_RETURN: key_press('return', isPressingShift, isPressingCtrl) #cursor.selectedElement.add_return()
            # --- Text input
            elif event.key == pygame.K_TAB:
                cursor.selectedElement.add_char('TAB', isManual=True)
            else:
                if event.unicode != '':
                    if PYGAME_IS_MODERN_VERSION:
                        key_press(event.unicode, isPressingShift, isPressingCtrl)
                    else:
                        cursor.selectedElement.add_char(event.unicode, isManual=True)

    elif event.type == pygame.KEYUP:
        # --- Directional Keys
        for event_, value in event2key.items():
            if event.key == event_: keys[value]=[0,0,0,0]

        if PYGAME_IS_MODERN_VERSION:
            if event.unicode in table:
                keys[event.unicode] = [0,0,0,0]

        '''
        if event.key == pygame.K_LEFT: keys['left']=[0,0,0,0]
        elif event.key == pygame.K_RIGHT: keys['right']=[0,0,0,0]
        elif event.key == pygame.K_UP: keys['up']=[0,0,0,0]
        elif event.key == pygame.K_DOWN: keys['down']=[0,0,0,0]
        elif event.key == pygame.K_BACKSPACE:
        '''
        # --- Shortcuts


    # --------------------------- #
