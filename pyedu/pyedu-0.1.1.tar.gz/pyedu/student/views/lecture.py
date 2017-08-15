"""
This file collects the different lecture views including list, enroll or unroll.

"""
from flask import render_template, flash, redirect, url_for
from flask_login import current_user

from pyedu.student import stud
from pyedu.models import Lecture, User, Level


@stud.route('/lectures/view')
def lecture_view_all():
    lectures = Lecture.query.all()
    return render_template('student/lectures.html', lectures=lectures)

@stud.route('/lecture/view/<int:lecture_id>')
def lecture_view(lecture_id):
    # load the lecture or abort
    lecture = Lecture.query.get_or_404(lecture_id)
    return render_template('student/view_lecture.html', lecture=lecture, lessons=lecture.lessons)


@stud.route('/lecture/<int:lecture_id>/enroll/<int:student_id>')
def enroll(lecture_id, student_id):
    lecture = Lecture.query.get_or_404(lecture_id)
    student = User.query.get_or_404(student_id)

    # check if the user is either a TEACHER or enrolling himself
    if current_user.id == student_id or current_user.has_level(Level.TEACHER):
        if not lecture.is_enrolled(student):
            lecture.enroll(student)
            flash('%s was enrolled to %s.' % (student.full_name, lecture.name), category='success')
        else:
            flash('%s is already enrolled to %s.' % (student.full_name, lecture.name), category='warning')

    else:
        flash('You are not allowed to enroll other students than yourself.', category='danger')

    # redirect to the Lecture
    return redirect(url_for('stud.lecture_view', lecture_id=lecture.id))