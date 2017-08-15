from flask import flash, redirect, url_for, render_template
from pyedu.teacher import teach
from pyedu.forms import EditLectureForm
from pyedu.models import db, Lecture


@teach.route('/lecture/edit', defaults={'lecture_id': None}, methods=['GET', 'POST'])
@teach.route('/lecture/edit/<int:lecture_id>', methods=['GET', 'POST'])
def lecture_edit(lecture_id):
    # create edit form and check for new name
    form = EditLectureForm()
    if form.validate_on_submit():
        if form.id.data is not None and form.id.data != '':
            lecture = Lecture.query.get_or_404(form.id.data)
            lecture.name = form.name.data
            lecture.description = form.description.data
            # lecture = Lecture(id=form.id.data, name=form.name.data, description=form.description.data)
            msg = 'Edited Lecture %s' % form.name.data
        else:
            lecture = Lecture(name=form.name.data, description=form.description.data)
            msg = 'Added Lecture %s' % form.name.data

        # add the lecture and sent a notice
        db.session.add(lecture)
        db.session.commit()
        flash(msg, category='success')
        return redirect(url_for('stud.lecture_view', lecture_id=lecture.id))
    else:
        # load the lecutre if edited
        if lecture_id is not None:
            lecture = Lecture.query.get_or_404(lecture_id)
            form.id.data = lecture.id
            form.name.data = lecture.name
            form.description.data = lecture.description
        return render_template('teacher/edit_lecture.html', form=form)
