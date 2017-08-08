from celery import task

@task()
def espresso_calculation_run():
    print('Quantum Espresso Calculation Run Command')
    return 'Quantum Espresso Calculation <SUCCESS>'
