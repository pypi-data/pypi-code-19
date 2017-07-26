from celery import task

@task()
def vasp_calculation_run():
    print('Vasp Calculation Run Command')
    return 'Vasp Calculation <SUCCESS>'
