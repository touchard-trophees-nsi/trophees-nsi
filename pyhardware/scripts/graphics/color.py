class RGB:
    def __init__(self, *args):
        try:
            if len(args)==1 and (type(args[0])==list or type(args[0])==tuple) and len(args[0])==3:
                self.value = list(args[0])
            else:
                self.value = [args[0], args[1], args[2]]
        except:
            raise TypeError('arguments should be a 3-elements long iterable or 3 ints/floats')
        for v in self.value:
            if v>255: v=255
            elif v<0: v=0

    def darken(self, value):
        out = RGB(self.value[0]-value, self.value[1]-value, self.value[2]-value)
        for i in range(len(out)):
            if out.value[i]>255: out.value[i]=255
            elif out.value[i]<0:
                out.value[i]=0
        return out

    def __len__(self):
        return len(self.value)
        
    def __repr__(self):
        return 'RGB'+str(self.value)

    def __iter__(self):
        for i in range(len(self.value)):
            yield self.value[i]

def gradient_palette(RGB, step=15, len_=3):
    out = []
    for i in range(len_):
        out.append(RGB.darken(step*i))
    return out