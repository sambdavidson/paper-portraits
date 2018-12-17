import time
import argparse


def __str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


parser = argparse.ArgumentParser(description='Paper Portraits')
parser.add_argument('-d', '--debug', type=__str2bool, nargs='?', const=True, default=False, help='Enable debug printing/')
args = parser.parse_args()


def info(v):
    if args.debug:
        print('INFO[{}]: {}'.format(time.strftime("%H:%M:%S", time.gmtime()), v))


def error(v):
    if args.debug:
        print('ERROR[{}]: {}'.format(time.strftime("%H:%M:%S", time.gmtime()), v))
