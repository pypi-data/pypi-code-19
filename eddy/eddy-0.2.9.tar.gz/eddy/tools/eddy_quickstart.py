import os
import argparse
import requests
import tarfile

def ask(question, default_answer=True):
    option = "[Y/n]" if default_answer else "[y/N]"
    question = question + " " + option
    print(question)
    
    print(len(question)*'-')
    answer = input("==> ")
    if default_answer:
        return answer != 'n'
    else:
        return answer == 'y'
        
def parse() -> argparse.Namespace:
    """Command line flags logic"""
    parser = argparse.ArgumentParser(description="Quickstart your eddy instance.")

    parser.add_argument('path', type=str, help="Path to new eddy instance")
    return parser.parse_args()


url = "https://api.github.com/repos/joajfreitas/eddy_starter/tarball/master"

def main():
    args = parse()

    print(f"Starting a new Eddy instance in {args.path}")
    if os.path.exists(args.path):
        print(f"Error: {args.path} already exists")
        exit()

    print("Downloading", url)
    r = requests.get(url)

#save tarfile to disk
    with open(args.path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=32):
            f.write(chunk)

#untar file
    t = tarfile.open(args.path, 'r')
    os.remove(args.path)
    t.extractall(os.path.split(args.path)[0])
    os.rename(t.getmembers()[0].name, args.path)
