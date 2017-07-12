import logging.config
import click
import logging
import numbers
import os.path
import cPickle as pickle
import time
import configparser

import workflow
import cube

def setup_logging(tg_chat, tg_token):
    if tg_chat is not None:
        tg_chat = int(tg_chat)

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
            'formatter': 'telegram',
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
            },
            'telegram': {
                'format': '%(message)s',
            }
        }
    })

class Main():
    def __init__(self, argument, full_result):
        config_file = '.cuber'
        self.config = configparser.ConfigParser()
        self.config.read(config_file)


        setup_logging(
            self.config.get('telegram', 'chat_id', fallback = None),
            self.config.get('telegram', 'token', fallback = None),
        )

        if argument.endswith('.wf'):
            self.run_graph(argument, full_result)
        elif argument.endswith('.pkl'):
            self.print_pickle(argument)
        else:
            raise ValueError('Unknown file type (.wf and .pkl are supported')

    def run_graph(self, workflow_file, full_result):
        start_time = time.time()
        try:
            cube.Cube.checkpoints_dir = self.config.get('cuber', 'checkpoints_dir', fallback = './checkpoints/')
            logging.info('Checkpoints dir: {}'.format(cube.Cube.checkpoints_dir))
            wf = workflow.Workflow(workflow_file)
            data = wf.run()
            res = '{}:\n'.format(workflow_file)
            for key, value in data.iteritems():
                if full_result or isinstance(value, str) or isinstance(value, numbers.Number):
                    res += '{}: {}\n'.format(key, value)
                else:
                    res += '{}: ...'.format(key)

            if time.time() - start_time >= 60 * float(self.config.get('cuber', 'message_delay', fallback = 3)):
                logging.critical('Calculation is done: {}\n{}'.format(workflow_file, res))
            else:
                logging.info('Calculation is done: {}\n{}'.format(workflow_file, res))
        except:
            import traceback
            traceback.print_exc()
            if time.time() - start_time >= 60 * float(self.config.get('cuber', 'message_delay', fallback = 3)):
                logging.critical('Calculation is failed: {}'.format(workflow_file))
            else:
                logging.error('Calculation is failed: {}'.format(workflow_file))

    def print_pickle(self, pickle_file):
        with open(workflow_file, 'rb') as f:
            data = pickle.load(f)
        print data

@click.command()
@click.argument('workflow_file')
@click.option('--full_result', default = False, is_flag=True)
def main(workflow_file, full_result):
    Main(workflow_file, full_result)

if __name__ == '__main__':
    main()
