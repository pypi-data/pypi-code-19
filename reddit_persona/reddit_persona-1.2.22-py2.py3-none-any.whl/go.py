from reddit_persona import insights
from reddit_persona import reddit_get
from reddit_persona import io_helper


def show(USERNAME, target):
    fpath = io_helper.out_path(USERNAME, target)
    with open(fpath, 'r') as f:
        response = ' '.join([line + ' ' for line in f])
    print(str(response))


import os


def check_dirs():
    if os.path.exists('cache/user/'):
        return
    elif not os.path.exists('cache/'):
        os.mkdir('cache')
    os.mkdir('cache/user')
    os.chmod('cache/user', 0o757)


def go(target, refresh=60 * 60 * 24):
    check_dirs()
    parse = target.split('/')
    USERNAME = parse[2]
    if not io_helper.check_time(USERNAME, target, refresh):
        show(USERNAME, target)
        return
    if parse[1] == 'u':
        target = 'user'
        reddit_get.user_text(user=USERNAME, refresh=refresh)
    elif parse[1] == 'r':
        target = 'sub'
        reddit_get.user_text(sub=USERNAME, refresh=refresh)

    try:
        indicoio.config.api_key = indicoKey.key
        indicoio.sentiment("I love writing code!")

    except Exception as e:
        io_helper.read_raw(USERNAME, target)

    insights.execute(USERNAME, target, refresh)

    show(USERNAME, target)


# TODO Add subreddits or descriptions
