""" Default console script """
import sys, os
import minette

def console(bot):
    while True:
        req = input("user> ")
        res = bot.execute(req)
        for message in res:
            print("minette> " + message.text)

def main(args=sys.argv):
    args = sys.argv

    if len(args) > 1:
        config_file = args[1]
        abs_path = os.path.abspath(config_file)
        home_dir = os.path.dirname(abs_path)
        sys.path.append(home_dir)


    else:
        config_file = os.path.join(os.path.dirname(args[0]), "default.ini.py")

    bot = minette.create(config_file=config_file)

    console(bot)
