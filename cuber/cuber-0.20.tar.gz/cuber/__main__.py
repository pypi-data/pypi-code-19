import logging.config
import click
import logging
import numbers
import os.path
import cPickle as pickle
import time
import configparser
import sqlite3
import datetime

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
    def __init__(self, argument, full_result, no_db, comment = ''):
        self.no_db = no_db
        self.comment = comment

        config_file = '.cuber'
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.checkpoints_dir = self.config.get('cuber', 'checkpoints_dir', fallback = './checkpoints/')

        setup_logging(
            self.config.get('telegram', 'chat_id', fallback = None),
            self.config.get('telegram', 'token', fallback = None),
        )

        if argument.endswith('.wf'):
            self.run_graph(argument, full_result)
        elif argument.endswith('.pkl'):
            self.print_pickle(argument)
        elif argument == 'show':
            self.setup_db()
            self.db_show()
        elif argument.startswith('detailed'):
            self.setup_db()
            self.db_show_detailed(argument[len('detailed'):])
        else:
            raise ValueError('Unknown file type (.wf and .pkl are supported')

    def setup_db(self):
        if self.no_db:
            self.db_connect = None
            return

        path = os.path.abspath(self.checkpoints_dir)
        if not os.path.isdir(path):
            os.makedirs(path)

        db_file = os.path.join(self.checkpoints_dir, 'graphs.db')

        logging.info('DB: file: {}'.format(db_file))
        self.db_connect = sqlite3.connect(db_file)
        c = self.db_connect.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS graphs
                             (id INTEGER PRIMARY KEY, date text, file text, graph text, result text, comment text, start_time text, end_time text, status text)''')
        self.db_connect.commit()
        logging.info('DB: prepared')

    def db_register(self):
        if self.no_db:
            return
        c = self.db_connect.cursor()
        c.execute(
        '''
            INSERT INTO graphs (date, file, start_time, status, graph, comment) VALUES (?, ?, ?, ?, ?, ?)
        ''',
            (datetime.datetime.now().date().isoformat(), self.workflow_file, datetime.datetime.now().isoformat(), 'register', self.graph, self.comment)
        )
        self.db_id = c.lastrowid
        logging.info('Graph ID: {}'.format(self.db_id))
        self.db_connect.commit()
        logging.info('DB: registered')

    def db_update_status(self, status):
        if self.no_db:
            return
        c = self.db_connect.cursor()
        c.execute(
        '''
            UPDATE graphs SET status = ? WHERE id = ?
        ''',
            (status, self.db_id)
        )
        self.db_connect.commit()
        logging.info('DB: status updated')

    def db_save_result(self, result):
        if self.no_db:
            return
        c = self.db_connect.cursor()
        c.execute(
        '''
            UPDATE graphs SET result = ?, end_time = ? WHERE id = ?
        ''',
            (result, datetime.datetime.now().isoformat(), self.db_id)
        )
        self.db_connect.commit()
        logging.info('DB: result saved')

    def db_show(self):
        if self.no_db:
            raise ValueError('You want to show db results, without db...')

        c = self.db_connect.cursor()
        res = c.execute(
        '''
            SELECT id, file, start_time, status, comment FROM graphs
        ''',
        )
        for row in res:
            print '\t'.join(map(str, row))

    def db_show_detailed(self, db_id):
        if self.no_db:
            raise ValueError('You want to show db results, without db...')

        c = self.db_connect.cursor()
        res = c.execute(
        '''
            SELECT id, graph, file, start_time, end_time, status, comment, result FROM graphs WHERE id = ?
        ''',
            db_id
        )
        for row in res:
            print '\n'.join(map(str, row))

    def run_graph(self, workflow_file, full_result):
        self.workflow_file = workflow_file
        start_time = time.time()

        self.setup_db()
        with open(workflow_file) as f:
            self.graph = f.read()

        self.db_register()

        message_delay = 60 * float(self.config.get('cuber', 'message_delay', fallback = 3))

        job_descritpion = '{}; {}'.format(workflow_file, self.comment)

        try:
            cube.Cube.checkpoints_dir = self.checkpoints_dir
            logging.info('Checkpoints dir: {}'.format(cube.Cube.checkpoints_dir))
            wf = workflow.Workflow(workflow_file)

            self.db_update_status('running')
            data = wf.run()

            res = '{}:\n'.format(workflow_file)
            for key, value in data.iteritems():
                if full_result or isinstance(value, str) or isinstance(value, numbers.Number):
                    res += '{}: {}\n'.format(key, value)
                else:
                    res += '{}: ...\n'.format(key)

            if time.time() - start_time >= message_delay:
                logging.critical('Calculation is done: {}\n{}'.format(job_descritpion, res))
            else:
                logging.info('Calculation is done: {}\n{}'.format(job_descritpion, res))
            self.db_save_result(res)
            self.db_update_status('done')
        except KeyboardInterrupt:
            if time.time() - start_time >= message_delay:
                logging.critical('Calculation is cancelled: {}'.format(job_descritpion))
            else:
                logging.error('Calculation is cancelled: {}'.format(job_descritpion))
            self.db_update_status('cancelled')
        except:
            import traceback
            traceback.print_exc()
            if time.time() - start_time >= message_delay:
                logging.critical('Calculation is failed: {}'.format(job_descritpion))
            else:
                logging.error('Calculation is failed: {}'.format(job_descritpion))
            self.db_update_status('failed')

    def print_pickle(self, pickle_file):
        with open(workflow_file, 'rb') as f:
            data = pickle.load(f)
        print data

@click.command()
@click.argument('workflow_file')
@click.option('--full_result', default = False, is_flag=True)
@click.option('--no_db', default = False, is_flag=True)
@click.option('--comment', default = '')
def main(workflow_file, full_result, no_db, comment):
    Main(workflow_file, full_result, no_db, comment)

if __name__ == '__main__':
    main()
