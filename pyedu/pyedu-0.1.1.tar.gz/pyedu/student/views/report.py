"""

"""
from flask import render_template
from pyedu.student import stud
from pyedu.util import UserReport, LogReport

@stud.route('/report/<int:student_id>')
def report(student_id):
    userreport = UserReport(student_id)
    logreport = LogReport(student_id)
    return render_template('student/report.html', userreport=userreport, logreport=logreport)