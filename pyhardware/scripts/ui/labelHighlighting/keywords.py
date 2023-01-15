import keyword

coloredKeywords = {
    (255,63,79):['if', 'elif', 'else', 'for', 'while', 'break', 'continue', 'with', 'import', 'as', 'using', 'and', 'or', 'not', 'in', 'is', 'return', 'yield', 'pass', 'del', 'global', 'nonlocal', 'await', 'try', 'except', 'finally', 'assert', 'raise'], # red
    (25,209,229):['def', 'class', '__init__', 'int', 'float', 'bool', 'str', 'async'], # blue
    (227,115,206):['True','False','None'], # pink
    (248,142,10):['self'], # orange
}

coloredCharacters = {
    (255,63,79):['=', '+', '-', '*', '/', '%', '>', '<', '!', '&', '|', '^', '~', '@'],
    (92,99,112):['#'], # gray
    (255,217,52):['"', '\'']
}

specialChars = ' ()[]{}:;,.?!$£'+''.join(coloredCharacters[(255,63,79)])+''.join(coloredCharacters[(92,99,112)])+''.join(coloredCharacters[(255,217,52)])