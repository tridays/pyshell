import os


def env(args):
    if len(args) == 0:
        pass
    elif len(args) == 1:
        print(os.getenv(args[0]))
    elif len(args) == 2:
        os.putenv(args[0], args[1])
    else:
        pass
    return True
