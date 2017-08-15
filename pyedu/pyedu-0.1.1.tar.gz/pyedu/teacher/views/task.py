from flask import render_template, request, flash, redirect, url_for
from pyedu.teacher import teach
from pyedu.forms import EditTaskForm
from pyedu.models import db, Lesson, Task


@teach.route('/task/edit', defaults={'task_id':None}, methods=['GET', 'POST'])
@teach.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
def task_edit(task_id):
    lesson_id = request.args.get('lesson_id')
    if lesson_id is None and task_id is None:
        flash('No lesson_id provided!', category='danger')
        return redirect(url_for('stud.lesson_view_all'))

    # load the form and the lesson
    form = EditTaskForm()

    # form was validated and submitted
    if form.validate_on_submit():
        # edit existing or add a new task
        if form.id.data is not None and form.id.data != '':
            task = Task.query.get_or_404(task_id)
            msg = 'Edited Task %s of Lesson %s.' % (task.name, task.lesson.name)

        # add new one
        else:
            task = Task()
            # load the lesson or throw a 404
            lesson = Lesson.query.get_or_404(lesson_id)
            msg = 'Added Task %s to Lesson %s.' % (task.name, lesson.name)

        # fill task and save to db
        task.lesson_id = form.lesson_id.data
        task.name = form.name.data
        task.description = form.description.data
        task.body = form.body.data
        task.solution = form.solution.data
        task.required = form.required.data
        task.seq = form.seq.data

        db.session.add(task)
        db.session.commit()
        flash(msg,category='success')
        return redirect(url_for('stud.task_view', task_id=task.id))


    # prefill the form
    else:
        if task_id is not None:
            # it's an edit form
            task = Task.query.get_or_404(task_id)
            form.id.data = task.id
            form.lesson_id.data = task.lesson_id
            form.name.data = task.name
            form.description.data = task.description
            form.body.data = task.body
            form.solution.data = task.solution
            form.required.data = task.required
            form.seq.data = task.seq
        else:
            form.lesson_id.data = lesson_id
        return render_template('teacher/edit_task.html', form=form)