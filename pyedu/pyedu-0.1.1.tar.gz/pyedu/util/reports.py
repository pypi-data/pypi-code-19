"""
The Report classes create current state informatiion about the progress in the Lectures, Lessons or Overall for
a single User or all Users.
"""
from pyedu.models import User, Lecture, Log
import pandas as pd


class UserReport:
    """

    """
    def __init__(self, user_id):
        self.user = User.query.get_or_404(user_id)

    def lesson_progress(self, lesson):
        return lesson.progress(student=self.user) / lesson.task_count

    def lecture_progress(self, lecture):
        return sum([lesson.progress(student=self.user) for lesson in lecture.lessons])

    @property
    def progress(self):
        return sum([self.lecture_progress(lecture) for lecture in Lecture.query.all() if lecture.is_enrolled(self.user)])


    def lesson_total_tasks(self, lesson):
        return lesson.task_count

    def lecutre_total_tasks(self, lecture):
        return sum([lesson.task_count for lesson in lecture.lessons])

    @property
    def total_tasks(self):
        return sum([self.lecutre_total_tasks(lecture) for lecture in Lecture.query.all() if lecture.is_enrolled(self.user)])


class LogReport:
    """

    """
    def __init__(self, user_id):
        self.user = User.query.get_or_404(user_id)

    def _return_from_id(self, task_ids, period):
        # load the logs
        logs = Log.query.filter(Log.student_id==self.user.id).filter(Log.task_id.in_(task_ids)).all()
        activity = pd.Series(data=1, index=[l.tstamp for l in logs]).groupby(pd.TimeGrouper(period)).sum()

        return activity.index.values, activity.values

    def task(self, task, period='1D'):
        return self._return_from_id(task.id, period)

    def lesson(self, lesson, period='1D'):
        return self._return_from_id([t.id for t in lesson.tasks], period)

    def lecture(self, lecture, period='1D'):
        task_ids = []
        for lesson in lecture.lessons:
            task_ids.extend([task.id for task in lesson])
        return self._return_from_id(task_ids, period)