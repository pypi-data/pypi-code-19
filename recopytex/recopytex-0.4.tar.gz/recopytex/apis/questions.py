#!/usr/bin/env python
# encoding: utf-8

from recopytex.app import db
from recopytex.models import Eval, Exercise, Question, Score, Student
from flask_restplus import Resource, Namespace, fields, reqparse, abort, inputs
from werkzeug.exceptions import BadRequest
from datetime import datetime

api = Namespace(
        name="questions",
        desciption="Manipulate questions"
        )


question_model = api.model("questions", {
    "id": fields.Integer,
    'name': fields.String,
    'score_rate': fields.Float,
    'is_leveled': fields.Boolean,
    'exercise_id': fields.Integer,
    'competence': fields.String,
    'domain': fields.String,
    'comment': fields.String,
    })

question_parser = reqparse.RequestParser()
question_parser.add_argument('id',
        type=int,
        required=False,
        help="question's id"
        )
question_parser.add_argument('name',
        type=str,
        required=True,
        help="Question's name"
        )
question_parser.add_argument('exercise_id',
        type=int,
        required=True,
        help="Question's exercise"
        )
question_parser.add_argument("score_rate",
        type=float, 
        required=True,
        help="Question's score rate"
        )
question_parser.add_argument("is_leveled",
        type=inputs.boolean, 
        required=True,
        help="The notation is a level (true) or a score (false)"
        )
question_parser.add_argument('competence',
        type=str,
        required=False,
        default="",
        help="Question's competence"
        )
question_parser.add_argument('domain',
        type=str,
        required=False,
        default="",
        help="Question's domain"
        )
question_parser.add_argument('comment',
        type=str,
        required=False,
        default="",
        help="Question's eval"
        )

@api.route("/")
class QuestionAPI(Resource):
    @api.marshal_with(question_model)
    def post(self):
        """ Creating a questions """
        args = question_parser.parse_args()
        question = Question(**args)
        db.session.add(question)
        db.session.commit()
        return question

@api.route("/<int:question_id>")
class QuestionAPI(Resource):
    @api.marshal_with(question_model)
    def get(self, question_id):
        """ Get everything about the question"""
        question = Question.query.filter(Question.id == question_id).first()
        if not question:
            error = {
                    'code': 404,
                    'message': f"Question id:{question_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            abort(**error)
        return question

    @api.marshal_with(question_model)
    @api.errorhandler
    def put(self, question_id):
        """ Update the question """
        args = question_parser.parse_args()
        try:
            assert args['id'] == question_id
        except AssertionError:
            error = {
                    'code': 400,
                    'message': f"Inconstitency beteewn id in url and in args",
                    'status': "INVALID_FIELD",
                    'field_name': 'id'
                    }
            abort(**error)

        question = Question.query.filter(Question.id == question_id)
        if not question.first():
            error = {
                    'code': 404,
                    'message': f"Question id:{question_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            abort(**error)

        question.update({
            "name": args["name"],
            "score_rate": args["score_rate"],
            "is_leveled": args["is_leveled"],
            "exercise_id": args["exercise_id"],
            "competence": args["competence"],
            "domain": args["domain"],
            "comment": args["comment"],
            })
        question = question.first()
        db.session.commit()
        return question, 200

    @api.errorhandler
    def delete(self, question_id):
        """ Delete the question """
        question = Question.query.filter(Question.id == question_id).first()
        if question:
            db.session.delete(question)
            db.session.commit()
            return '', 204
        else:
            message = {
                    'code': 404,
                    'message': f"Question id:{question_id} does not exist",
                    'status': 'NOT_FOUND'
                    }
            return message, 404


if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
