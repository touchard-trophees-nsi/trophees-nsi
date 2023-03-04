lang = 'fr'

with open(lang+'.txt') as file:
    trads = {'title': (file.readline()).strip(),
            'subtitle': (file.readline()).strip()}

def getText(txt):
    return trads[txt] if txt in trads.keys() else None

