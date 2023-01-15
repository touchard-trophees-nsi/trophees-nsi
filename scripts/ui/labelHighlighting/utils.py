from scripts.ui.labelHighlighting.keywords import specialChars

def char2indexes(text, word):
    index = 0 
    temp_list = []
    out = []
    for i in range(len(text)):
        if text[i]==word[index]:
            index+=1
            temp_list.append(i)
        else:
            index = 0
            temp_list = []
        if index == len(word):
            index = 0
            out += temp_list
            temp_list = []
    return out

def word2indexes(text, word):
    index = 0
    start_index = 0
    temp_list = []
    out = []
    for i in range(len(text)):
        if index==0 and text[i]==word[index] and ((text[i-1] in specialChars) if i>0 else True):
            start_index = i
            index+=1
            temp_list.append(i)
        elif index>0 and text[i]==word[index]:
            index+=1
            temp_list.append(i)
        else:
            index = 0
            temp_list = []
        if index == len(word) and ((text[start_index+index] in specialChars) if start_index+index<len(text) else True):
            index = 0
            out += temp_list
            temp_list = []
        elif index == len(word):
            index = 0
            temp_list = []

    return out