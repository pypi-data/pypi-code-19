#!/usr/bin/env python
# encoding: utf-8

from Recopytex import db
from Recopytex.models import Student, Tribe
from flask_restplus import Resource, Namespace, fields, reqparse, abort
from werkzeug.exceptions import BadRequest
import datetime

api = Namespace(
        name="students",
        desciption="Requests on students"
        )

tribe_model = api.model("tribe", {
    "id": fields.Integer,
    'name': fields.String,
    })


student_model = api.model("Student", {
    'id': fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'fullname': fields.String,
    'mail': fields.String,
    'comment': fields.String(default=""),
    'tribe': fields.List(fields.Nested(tribe_model)),
    })

@api.route("/")
class StudentsAPI(Resource):
    @api.marshal_with(student_model)
    def get(self):
        """ List of studentss """
        students = Student.query.all()
        return students

    @api.marshal_with(student_model)
    def post(self):
        """ Creating a students """
        pass


@api.route("/<int:student_id>")
class StudentsAPI(Resource):
    @api.marshal_with(student_model)
    def get(self, student_id):
        """ Get informations on the student"""
        student = Student.query.filter(Student.id == student_id).first()
        if not student:
            error = {
                    'code': 404,
                    'message': f"Student id:{student_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            abort(**error)
        return student

    @api.marshal_with(student_model)
    def put(self, student_id):
        """ Update the student """
        pass

    def delete(self, student_id):
        """ Delete the student """
        pass

@api.route("/tribe/<int:tribe_id>")
class StudentsTribeAPI(Resource):
    @api.marshal_with(student_model)
    def get(self, tribe_id):
        """ Get student in a tribe"""
        student = Student.query\
                .filter(Student.tribe_id == tribe_id)\
            .all()
        return student

@api.route("/grade/<string:grade>")
class StudentsGradeAPI(Resource):
    @api.marshal_with(student_model)
    def get(self, grade):
        """ Get student in a tribe"""
        student = Student.query\
                .join(Tribe, (Tribe.id==Student.tribe_id))\
                .filter(Tribe.grade == grade)\
            .all()
        return student

if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
