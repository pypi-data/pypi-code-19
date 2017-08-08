import celery
import inspect
import os


ENV = {
    'MYR_ANNOUNCE_TASK': 'myr.discovery.announce',
    'MYR_ANNOUNCE_QUEUE': '_myr_discovery_',
    'MYR_ANNOUNCE_INTERVAL': 5.0
}
ENV.update(os.environ)


def get_function_spec(callable):
    """Returns function (callable) argspec"""
    return inspect.getargspec(callable)


def get_task_routing(celery_app, task_name):
    router = celery_app.amqp.Router()
    route = router.route({}, task_name)
    route = {
        'queue': route['queue'].name,
        'exchange': route.get('exchange', route['queue'].exchange.name),
        'routing_key': route.get('routing_key', route['queue'].routing_key)
    }
    if route['exchange'] == route['queue']:
        del route['exchange']
    return route


def announce(self):
    """Celery task for announcing user tasks to discovery service"""
    all_tasks = self.app.tasks.regular()
    user_tasks = {}
    for task in all_tasks:
        if task.startswith('celery.'):
            continue
        if task == 'myr.base.app.announce':
            continue
        user_tasks[task] = {
            'signature': get_function_spec(all_tasks[task].run)._asdict(),
            'routing': get_task_routing(self.app, task)
        }
    self.app.send_task(ENV.get('MYR_ANNOUNCE_TASK'),
                       args=[user_tasks],
                       queue=ENV.get('MYR_ANNOUNCE_QUEUE'))


class MyrApp(celery.Celery):
    def on_init(self):
        queue_name = '{name}.tasks'.format(name=(
            self.main or __package__.split('.', 1)[0]))
        self.amqp.queues.select_add(queue_name)
        self.conf.task_default_queue = queue_name

        self._tasks.register(self.task(announce,
            name='myr.base.app.announce', bind=True, ignore_result=True))
        self.conf.beat_schedule = {
            'announce': {
                'task': 'myr.base.app.announce',
                'schedule': ENV.get('MYR_ANNOUNCE_INTERVAL'),
                'options': {
                    'queue': queue_name
                }
            }
        }

    def gen_task_name(self, name, module):
        return '{}.{}'.format(self.main or __package__.split('.', 1)[0], name)
