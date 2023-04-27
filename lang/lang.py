import yaml
lang='fr'
def getText(key,lang):
    with open("lang/trads/"+lang+".yaml", 'r',encoding='utf8') as read_file:      
        data = yaml.safe_load(read_file)
    if key in data:
        return data[key]
    else:
        return ""

isKeyboardAzerty = False
