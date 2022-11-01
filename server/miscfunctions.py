from os import path

def current_path(file=None):
    try:
        dir_path = path.dirname(path.realpath(__file__), )
        if file != None:
            config_path = path.join(dir_path, file)
            return config_path
        else:
            return dir_path
    except Exception as e:
        return e