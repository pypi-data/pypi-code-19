from myr.base.app import (
    MyrApp,
    announce,
    get_function_spec,
    ENV
)


class TestApp:

    def test_basic(self):
        app = MyrApp()
        assert 'myr.base.app.announce' in app.tasks.regular()
        assert 'announce' in app.conf.beat_schedule

    def test_announcing_no_tasks(self, mocker):
        class Task:
            app = MyrApp()

        mocker.patch.object(Task.app, 'send_task')

        announce(Task)
        Task.app.send_task.assert_called_with(
            ENV.get('MYR_ANNOUNCE_TASK'),
            args=[{}],
            queue=ENV.get('MYR_ANNOUNCE_QUEUE'))

    def test_announcing_user_tasks(self, mocker):
        app = MyrApp()

        @app.task
        def test_task(a1, a2='2'):
            pass

        mocker.patch.object(app, 'send_task')

        announce(test_task)
        tasks_spec = {
            test_task.name: {
                'signature': get_function_spec(test_task.run)._asdict(),
                'routing': {
                    'queue': 'myr.tasks',
                    'routing_key': 'myr.tasks',
                    'exchange': ''
                }
            }
        }
        app.send_task.assert_called_with(
            ENV.get('MYR_ANNOUNCE_TASK'),
            args=[tasks_spec],
            queue=ENV.get('MYR_ANNOUNCE_QUEUE'))

    def test_custom_task_routing(self, mocker):
        app = MyrApp()

        @app.task
        def test_task():
            pass
        app.conf.task_routes = {
            test_task.name: {
                'queue': 'test_queue',
                'exchange': 'test_exchange',
                'routing_key': 'test_key'
            }
        }

        mocker.patch.object(app, 'send_task')
        announce(test_task)
        tasks_spec = {
            test_task.name: {
                'signature': get_function_spec(test_task.run)._asdict(),
                'routing': {
                    'queue': 'test_queue',
                    'exchange': 'test_exchange',
                    'routing_key': 'test_key'
                }
            }
        }
        app.send_task.assert_called_with(
            ENV.get('MYR_ANNOUNCE_TASK'),
            args=[tasks_spec],
            queue=ENV.get('MYR_ANNOUNCE_QUEUE'))
