from cgitb import text
import pygame, sys
from scripts.cursor import cursor
from scripts.ui.widgets.textEntry import TextEntry
from lang.lang import isKeyboardAzerty

def shutdown():
    pygame.quit()
    sys.exit()

keys = {'right':[0,0,0,0],'up':[0,0,0,0],'left':[0,0,0,0],'down':[0,0,0,0]} # [0]:pressed time, [1]:isPressingShift, [2]:isPressingCtrl, [3]:move cooldown
def directional_key_update(key, isPressingShift, isPressingCtrl):
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
                else:
                    print('Invalid direcitonal key')
                keys[key][3]+=1
            else:
                keys[key][3]=0

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
            elif event.key == pygame.K_BACKSPACE: cursor.selectedElement.backspace(ctrl=isPressingCtrl)
            elif event.key == pygame.K_RETURN: cursor.selectedElement.add_return()
            # --- Text input
            elif event.key == pygame.K_TAB:
                cursor.selectedElement.add_char('TAB', isManual=True)
            else:
                if event.unicode != '':
                    cursor.selectedElement.add_char(event.unicode, isManual=True)
    elif event.type == pygame.KEYUP:
        # --- Directional Keys
        if event.key == pygame.K_LEFT: keys['left']=[0,0,0,0]
        elif event.key == pygame.K_RIGHT: keys['right']=[0,0,0,0]
        elif event.key == pygame.K_UP: keys['up']=[0,0,0,0]
        elif event.key == pygame.K_DOWN: keys['down']=[0,0,0,0]
        # --- Shortcuts


    # --------------------------- #
    elif event.type == pygame.KEYUP:
        pass
    return ''
