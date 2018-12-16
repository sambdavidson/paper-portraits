import time
import argparse

parser = argparse.ArgumentParser(description='Paper Portraits')
parser.add_argument('-d', '--debug', type=bool, action='store_true', help='enable debug printing')
args = parser.parse_args()


def info(v):
    if not args.debug:
        print('INFO[{}]: {}'.format(time.strftime("%H:%M:%S", time.gmtime()), v))


def error(v):
    if not args.debug:
        print('ERROR[{}]: {}'.format(time.strftime("%H:%M:%S", time.gmtime()), v))
