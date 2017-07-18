from celery import task

@task()
def create_pmg_structure():
    print('Create PMG Structure Call')
    return 'Create PMG Structure Call <SUCCESS>'
