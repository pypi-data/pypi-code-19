import sys
from pic2text import pic2text
import requests
import argparse
import shutil

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    converter = pic2text.Pic_2_Text() #init class
    #convert vith path, args.path is the cmd argument string. feel free to use any path, if using this class
    if args.link:
        response = requests.get(args.link, stream=True)
        with open('/tmp/pic2text-img.png', 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
        converter.convert('/tmp/pic2text-img.png', args.scale)
    else:
        converter.convert(args.path, args.scale)
    
    print('done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="str path to picture eg: --path './path/to/pic.jpg'", default="/tmp/pic2text.png", type=str)
    parser.add_argument("--scale", help="0-1 new scale (.2 is not 20% less)", default=.3, type=float)
    parser.add_argument("--link", help="-link", default="https://unsplash.it/400/600/?random", type=str)
    args = parser.parse_args()
    main(args)