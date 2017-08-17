#!/usr/bin/env python
# encoding: utf-8

from recopytex.app import db
from recopytex.models import Eval, Exercise, Question, Score, Student
from flask_restplus import Resource, Namespace, fields, reqparse, abort
from werkzeug.exceptions import BadRequest
from datetime import datetime

api = Namespace(
        name="exercises",
        desciption="Manipulate exercises"
        )


exercise_model = api.model("exercise", {
    "id": fields.Integer,
    'eval_id': fields.Integer,
    'name': fields.String,
    'date': fields.Date,
    'comment': fields.String,
    })

exercise_parser = reqparse.RequestParser()
exercise_parser.add_argument('id',
                         type=int,
                         required=False,
                         help="Exercise's id"
                         )
exercise_parser.add_argument('name',
                         type=str,
                         required=True,
                         help="Exercise's name"
                         )
exercise_parser.add_argument('eval_id',
                         type=int,
                         required=True,
                         help="Exercise's eval"
                         )
exercise_parser.add_argument('date',
                         type=str,
                         required=False,
                         default=datetime.now().strftime("%Y-%m-%d"),
                         help="Exercise's date"
                         )
exercise_parser.add_argument('comment',
                         type=str,
                         required=False,
                         default="",
                         help="Exercise'e eval"
                         )

@api.route("/")
class ExercisesAPI(Resource):
    @api.marshal_with(exercise_model)
    def post(self):
        """ Creating a exercises """
        args = exercise_parser.parse_args()
        args["date"] = datetime.strptime(args['date'], '%Y-%m-%d')
        # TODO: Il faudrait teste que l'id de l'évaluation existe bien. |ven. août  4 08:48:06 EAT 2017
        exercise = Exercise(**args)
        db.session.add(exercise)
        db.session.commit()
        return exercise

@api.route("/<int:exercise_id>")
class ExerciseAPI(Resource):
    @api.marshal_with(exercise_model)
    def get(self, exercise_id):
        """ Get students and exerciseuations on the class """
        exercise = Exercise.query.filter(Exercise.id == exercise_id).first()
        if not exercise:
            error = {
                    'code': 404,
                    'message': f"Exercise id:{exercise_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            abort(**error)
        return exercise

    @api.marshal_with(exercise_model)
    @api.errorhandler
    def put(self, exercise_id):
        """ Update the exercise """
        args = exercise_parser.parse_args()
        try:
            assert args['id'] == exercise_id
        except AssertionError:
            error = {
                    'code': 400,
                    'message': f"Inconstitency beteewn id in url and in args",
                    'status': "INVALID_FIELD",
                    'field_name': 'id'
                    }
            abort(**error)

        exercise = Exercise.query.filter(Exercise.id == exercise_id)
        if not exercise.first():
            error = {
                    'code': 404,
                    'message': f"Exercise id:{exercise_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            abort(**error)

        exercise.update({
            'name': args["name"],
            'eval_id': args["eval_id"],
            "date": datetime.strptime(args['date'], '%Y-%m-%d'),
            'comment': args["comment"]
            })
        exercise = exercise.first()
        db.session.commit()
        return exercise, 200

    @api.errorhandler
    def delete(self, exercise_id):
        """ Delete the exercise """
        exercise = Exercise.query.filter(Exercise.id == exercise_id).first()
        if exercise:
            db.session.delete(exercise)
            db.session.commit()
            return '', 204
        else:
            message = {
                    'code': 404,
                    'message': f"Exercise id:{exercise_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            return message, 404


if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
