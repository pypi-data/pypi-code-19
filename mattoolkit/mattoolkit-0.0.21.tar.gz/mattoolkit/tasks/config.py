import json

config_file = json.load(open('config/dev.json'))

class CeleryConfig:
    broker = config_file['broker']
    results_backend = config_file['results_backend']

    # Default in 4.0
    result_serializer = 'json'

    imports=(
        'mattoolkit.tasks.calculation',
        'mattoolkit.tasks.structure'
    )

    task_routes = {
        'tasks.calculation.*': 'foobar-queue'
    }
