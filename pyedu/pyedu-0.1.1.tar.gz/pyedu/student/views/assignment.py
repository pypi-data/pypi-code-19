"""
This file does the actual assignment handling. For a future release, this route should NOT be called and moreover
be shifted to a remote server. As the body content was already run, only the teacher made code from the database
will be executed here.
"""
import base64, dill
from flask import request, abort, redirect, url_for, flash
from pyedu.student import stud
from pyedu.models import User, Task, Assignment, Log, db


@stud.route('/assign/<student_id>/<int:task_id>')
def assign(student_id, task_id):
    """

    :param student_id:
    :param task_id:
    :return:
    """
    # load the user and task and abort if not valid
    user = User.query.get(student_id)
    task = Task.query.get(task_id)
    dec_locals = request.args.get('locals')
    body = base64.b64decode(request.args.get('body')).decode()

    if dec_locals is None or user is None or task is None or body is None:
        abort(500, 'Missing info: dec_locals: {0}, user: {1}, task: {2}, body: {3}'.format(dec_locals, user, task, body))

    # load the Assignment
    assignment = Assignment.query.filter_by(task_id=task_id, student_id=student_id).first()
    if assignment is None:
        assignment = Assignment(task_id=task_id, student_id=student_id, attempts=0)

    # decrypt and parse the locals_dict
    locals_holder = dill.loads(base64.b64decode(dec_locals))

    # run the code
    fenvg, fenvl = dict(), dict()
    exec(task.solution, fenvg, fenvl)
    verify = fenvl.get('verify')

    print(locals_holder, task.solution)
#    print(fenvg, fenvl)

    try:
        if not verify(**locals_holder):
            raise AssertionError
        else:
            assignment.solved = True
            flash('Correct! You solved task %s (%d attempts)' % (task.name, assignment.attempts + 1),
                  category='success')
    except AssertionError:
        flash('Sorry, your solution was not correct.', category='danger')

    # log the Assignment
    assignment.body = body
    assignment.increment()

    # create a log
    log = Log(student_id=student_id, task_id=task_id)

    # save
    db.session.add(assignment)
    db.session.add(log)
    db.session.commit()

    # return
    return redirect(url_for('stud.task_view',
                    task_id=task.next.id if assignment.solved and task.next is not None else task.id))

