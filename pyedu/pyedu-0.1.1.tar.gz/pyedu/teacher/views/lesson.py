from flask import flash, redirect, url_for, render_template, request
from pyedu.teacher import teach
from pyedu.forms import EditLessonForm
from pyedu.models import db, Lecture, Lesson


@teach.route('/lesson/edit', defaults={'lesson_id':None}, methods=['GET', 'POST'])
@teach.route('/lesson/edit/<int:lesson_id>', methods=['GET', 'POST'])
def lesson_edit(lesson_id):
    lecture_id = request.args.get('lecture_id')
    if lecture_id is None and lesson_id is None:
        flash('No lecture_id provided!', category='danger')
        return redirect(url_for('stud.lesson_view_all'))

    # get the form and the lecture
    form = EditLessonForm()

    # validate form and insert
    if form.validate_on_submit():
        #  edit existing
        if form.id.data is not None and form.id.data != '':
            lesson = Lesson.query.get_or_404(form.id.data)
            msg = 'Edited Lesson %s of Lecture %s.' %(lesson.name, lesson.lecture.name)

        # add new
        else:
            lesson = Lesson()
            lecture = Lecture.query.get_or_404(lecture_id)
            msg = 'Added Lesson %s to Lecture %s.' % (lesson.name, lecture.name)

        # fill the lesson
        lesson.name = form.name.data
        lesson.lecture_id = form.lecture_id.data

        db.session.add(lesson)
        db.session.commit()
        flash(msg, category='success')
        return redirect(url_for('stud.lesson_view', lesson_id=lesson.id))

    # prefil the form
    else:
        if lesson_id is not None:
            # Form is actually a EditForm not an AddFrom
            lesson = Lesson.query.get_or_404(lesson_id)
            form.id.data = lesson.id
            form.lecture_id.data = lesson.lecture_id
            form.name.data = lesson.name
        else:
            form.lecture_id.data = lecture_id
        return render_template('teacher/edit_lesson.html', form=form)
