from ghlint import config
from ghlint import lint


def main():
    settings = config.settings()
    lint.run(settings)

if __name__ == "__main__":
    main()
