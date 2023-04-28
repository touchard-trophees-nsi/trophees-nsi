import pickle

def save_device_as(path,shapes):
    try:
        with open('data/{}.pkl'.format(str(path)), 'wb') as output:
            for shape in shapes:
                shape.pickle_check()
            print('Sauvegardé avec succès!')
            pickle.dump(shapes, output, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print("Error: {}".format(str(e)))

def load_device(path):
    try:
        with open('data/{}.pkl'.format(str(path)), 'rb') as inp:
            out = pickle.load(inp)
            print('Chargé avec succès!')
            return out
    except Exception as e:
        print("Error: {}".format(str(e)))