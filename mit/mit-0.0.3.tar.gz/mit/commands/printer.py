from colorama import Style, Fore


class Printer(object):

    @staticmethod
    def get_prefix(repo_name):
        return Fore.LIGHTCYAN_EX + repo_name + Style.RESET_ALL + "\n\t"

    @staticmethod
    def p(msg, back="", fore=""):
        print back + fore + msg + Style.RESET_ALL
