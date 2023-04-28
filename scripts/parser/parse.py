
from scripts.parser.pseudocode import set_code, stop_game
from scripts.parser.user_print import user_print
from scripts.dev import dprint

changes = {'print': 'user_print',
           'terminate': 'stop_game'}

def parse_keywords(text, shapes):
    '''
    Remplace les mots-clés du pseudo-code par de vraies instructions python
    '''
    out = text

    for key, value in changes.items():
        out = out.replace(key, value)
    return out

def parse_indentation(text):
    '''
    Décompose le code en 3 parties exécutables: démarrage, boucle, fin
    '''
    text_ = text.split('\n')
    text_.remove('>>start')
    temp = []
    out = []
    for i in range(len(text_)):
        line = text_[i]
        temp.append(line)
        if line == '>>update' or line == '>>end' or i==len(text_)-1:
            out.append(temp)
            temp = []
    out[0].remove('>>update') 
    out[1].remove('>>end')
    for i in range(len(out)):
        out[i] = 'if True:\n'+'\n'.join(out[i])
    return out         

def parse(text, shapes):
    '''
    Fonction wrapper pour les fonctions parse_keywords et parse_indentation
    Analyse et décompose un pseudo-code fourni par l'utilisateur en un code python exécutable
    '''
    for shape in shapes:
        if 'CPU' in shape.get_type() and shape.parent != None and 'PCB' in shape.parent.get_type():
            out = parse_keywords(text, shapes)
            out = parse_indentation(out)
            set_code(out[0],out[1],out[2])
            return out
    else: 
        return None
    