import logging.config
import click
import logging
import numbers
import os.path
import cPickle as pickle

import workflow

@click.command()
@click.argument('workflow_file')
@click.option('--tg_chat', default = None, help = 'Telegram chat_id for logging')
@click.option('--tg_token', default = None, help = 'Telegram token for logging')
def main(workflow_file, tg_chat, tg_token):
    if tg_chat is None:
        config_file = '{}/.cuber'.format(os.path.expanduser("~"))
        if os.path.isfile(config_file):
            tg_token, tg_chat = open(config_file).read().split('\n')[0:2]
            tg_chat = int(tg_chat)
            print 'tg'

    logging_handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
    }

    if tg_chat is not None:
        logging_handlers['telegram'] = {
            'class': 'telegram_handler.TelegramHandler',
            'token': tg_token,
            'chat_id': tg_chat,
            'level': 'CRITICAL',
        }

    logging.config.dictConfig({
        'version': 1,
        'handlers': logging_handlers,
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ['console'] + (['telegram'] if tg_chat is not None else []),
                "propagate": "no"
            }
        },
        'formatters': {
            'console': {
                'format': '%(levelname)s: %(asctime)s ::: %(name)-10s: %(message)s (%(filename)s:%(lineno)d)',
            }
        }
    })
    if workflow_file.endswith('.wf'):
        try:
            wf = workflow.Workflow(workflow_file)
            data = wf.run()
            res = '{}:\n'.format(workflow_file)
            for key, value in data.iteritems():
                if isinstance(value, str) or isinstance(value, numbers.Number):
                    print '{}: {}'.format(key, value)
                    res += '{}: {}\n'.format(key, value)
                else:
                    print '{}: ...'.format(key)
            logging.critical(res)
        except:
            import traceback
            traceback.print_exc()
            logging.critical('Calculation is failed')
    elif workflow_file.endswith('.pkl'):
        with open(workflow_file, 'rb') as f:
            data = pickle.load(f)
        print data
    else:
        raise ValueError('Unknown file type (.wf and .pkl are supported')

if __name__ == '__main__':
    main()
