import sys
from pic2text import pic2text
import argparse

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    converter = pic2text.Pic_2_Text() #init class
    #convert vith path, args.path is the cmd argument string. feel free to use any path, if using this class
    converter.convert(args.path, args.scale)
    print('completed script')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="str path to picture eg: --path './path/to/pic.jpg'", default="./pic.png", type=str)
    parser.add_argument("--scale", help="0-1 new scale (.2 is not 20% less)", default=.4, type=float)
    args = parser.parse_args()
    main(args)