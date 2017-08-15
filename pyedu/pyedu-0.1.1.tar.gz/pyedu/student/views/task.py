"""

"""
import sys, base64, dill
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from pyedu.student import stud
from pyedu.models import Task
from pyedu.forms import ViewTaskForm


@stud.route('/tasks/view', defaults={'lesson_id':None})
@stud.route('/taks/view/<int:lesson_id>')
def task_view_all(lesson_id):
    if lesson_id is None:
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(lesson_id=lesson_id).all()
    return render_template('student/tasks.html', tasks=tasks)


@stud.route('/task/view/<int:task_id>', methods=['GET', 'POST'])
def task_view(task_id):
    form = ViewTaskForm()
    task = Task.query.get_or_404(task_id)

    if form.validate_on_submit():
        # A solution was submitted, try to run the chunk
        locals_dict = dict()
        try:
            exec(form.body.data, dict(), locals_dict)
        except:
            e_type, e, tb = sys.exc_info()
            flash("""<strong>Oops!</strong><br>
            Your code is not yet correct.
            <br><br>[%d]: %s: %s""" % (tb.tb_lineno, e_type.__name__, str(e)),
                  category='danger')
            return render_template('student/view_task.html', task=task, form=form)

        # TODO handle correctly (by POST?? necessary?)
        # in locals dict are still maybe callables
        #locals_dict_callables = {key:str(value) for key, value in locals_dict.items() if callable(value)}
        #locals_dict.update(locals_dict_callables)

        # encode locs and body for sending
        locs = base64.b64encode(dill.dumps(locals_dict)).decode()  # TODO: try so send a pickle
        body = base64.b64encode(form.body.data.encode('utf-8')).decode()
        return redirect(url_for('stud.assign', student_id=current_user.id, task_id=task.id, body=body, locals=locs))


    else:
        # prefill
        form.id.data = task_id
        form.body.data = task.get_user_body(current_user)
    return render_template('student/view_task.html', task=task, form=form)