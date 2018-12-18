import time

debug_mode = False


def set_debug_mode(val):
    global debug_mode
    debug_mode = val


def info(v):
    if debug_mode:
        print('INFO[{}]: {}'.format(time.strftime("%H:%M:%S", time.gmtime()), v))


def error(v):
    if debug_mode:
        print('ERROR[{}]: {}'.format(time.strftime("%H:%M:%S", time.gmtime()), v))
