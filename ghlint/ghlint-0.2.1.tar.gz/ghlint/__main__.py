from ghlint import run
import config


def main():
    run(config.settings())

if __name__ == "__main__":
    main()
