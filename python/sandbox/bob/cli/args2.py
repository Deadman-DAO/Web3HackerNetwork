import argparse

# See: https://docs.python.org/3/library/argparse.html#module-argparse

parser = argparse.ArgumentParser(
    prog='argparse Module Example Code',
    description='Shows how argparse can be used to parse args.',
    epilog = f'eg: python3 {__file__} -c 7 /path/to/file'
)

parser.add_argument('filename') # positional argument
parser.add_argument('-c', '--count', # option that takes a value
                    help='explain what count does', type=int)
parser.add_argument('-v', '--verbose',
                    action='store_true', # on/off flag
                    help='this is a switch that explains things using far too many words')

args = parser.parse_args()
print(args.filename, args.count, args.verbose)
