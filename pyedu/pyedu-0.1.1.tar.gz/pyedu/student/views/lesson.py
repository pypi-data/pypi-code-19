"""

"""
from flask import render_template
from pyedu.student import stud
from pyedu.models import Lesson


@stud.route('/lessons/view', defaults={'lecture_id':None})
@stud.route('/lessons/view/<int:lecture_id>')
def lesson_view_all(lecture_id):
    if lecture_id is None:
        lessons = Lesson.query.all()
    else:
        lessons = Lesson.query.filter_by(lecture_id=lecture_id).all()
    return render_template('student/lessons.html', lessons=lessons)


@stud.route('/lesson/view/<int:lesson_id>')
def lesson_view(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    return render_template('student/view_lesson.html', lesson=lesson, tasks=lesson.tasks)