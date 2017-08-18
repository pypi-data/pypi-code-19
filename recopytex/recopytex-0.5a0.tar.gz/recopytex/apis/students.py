#!/usr/bin/env python
# encoding: utf-8

from recopytex.app import db
from recopytex.models import Student, Tribe
from flask_restplus import Resource, Namespace, fields, reqparse, abort
from werkzeug.exceptions import BadRequest
import datetime

api = Namespace(
        name="students",
        desciption="Requests on students"
        )

student_model = api.model("Student", {
    'id': fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'fullname': fields.String,
    'mail': fields.String,
    'comment': fields.String(default=""),
    'tribe_id': fields.Integer(),
    })

student_parser = reqparse.RequestParser()
student_parser.add_argument('id',
        type=int,
        required=False,
        help="student's id"
        )
student_parser.add_argument('name',
        type=str,
        required=True,
        help="Student's name"
        )
student_parser.add_argument('surname',
        type=str,
        required=True,
        help="Student's surname"
        )
student_parser.add_argument('tribe_id',
        type=int,
        required=True,
        help="Tribe's id of the student"
        )
student_parser.add_argument('comment',
        type=str,
        required=False,
        default="",
        help="Student's comment"
        )

@api.route("/")
class StudentsAPI(Resource):
    @api.marshal_with(student_model)
    def get(self):
        """ List of studentss """
        students = Student.query.all()
        return students

    @api.marshal_with(student_model)
    def post(self):
        """ Creating a student """
        args = student_parser.parse_args()
        # Je pige pour d'où vient ce id...
        args.pop("id", None)
        student = Student(**args)
        db.session.add(student)
        db.session.commit()
        return student


@api.route("/<int:student_id>")
class StudentAPI(Resource):
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

    @api.marshal_with(student_model)
    def put(self, student_id):
        """ Update the student """
        args = student_parser.parse_args()
        try:
            assert args['id'] == student_id
        except AssertionError:
            error = {
                    'code': 400,
                    'message': f"Inconstitency beteewn id in url and in args",
                    'status': "INVALID_FIELD",
                    'field_name': 'id'
                    }
            abort(**error)

        student = Student.query.filter(Student.id == student_id)
        wanted_keys = ["name", "surname", "mail", "comment", "tribe_id"]
        student.update({k: args[k] for k in args if k in wanted_keys})
        student = student.first()
        db.session.commit()
        return student


csv_parser = reqparse.RequestParser()
csv_parser.add_argument('csv',
        type=str,
        required=True,
        default="",
        help="CSV type string"
        )

@api.route("/tribe/<int:tribe_id>/csv/")
class StudentsCSVTribeAPI(Resource):
    @api.marshal_with(student_model)
    def post(self, tribe_id):
        """ Creating students from a csv file """
        csv = csv_parser.parse_args()['csv']
        students = []
        for student_name in csv.split("\n"):
            name = []
            surname = []
            for name_part in student_name.split(" "):
                if name_part == name_part.upper():
                    name.append(name_part)
                else: 
                    surname.append(name_part)
            stud = {
                    'name': " ".join(name),
                    'surname': " ".join(surname),
                    "tribe_id": tribe_id,
                    }
            student = Student(**stud)
            db.session.add(student)
            students.append(student)
        db.session.commit()
        return students


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


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
