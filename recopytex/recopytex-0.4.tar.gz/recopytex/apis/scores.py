#!/usr/bin/env python
# encoding: utf-8

from recopytex.app import db
from recopytex.models import Score, Question, Exercise, Eval, Student
from flask_restplus import Resource, Namespace, fields, reqparse
from werkzeug.exceptions import BadRequest

api = Namespace(
        name="scores",
        desciption="Querying on Scores"
        )

score_model = api.model("score", {
    "id": fields.Integer,
    "value": fields.String,
    "question_id": fields.Integer,
    "student_id": fields.Integer,
    })

scores_parser = reqparse.RequestParser()
scores_parser.add_argument('scores',
                         type=list,
                         #required=True,
                         help="List of scores",
                         location='json'
                         )

@api.route("/")
class ScoreAPI(Resource):
    @api.marshal_with(score_model)
    def put(self):
        """ Saving scores """
        scores = scores_parser.parse_args()['scores']
        saved_scores = []
        for score in scores:
            try:
                sc_id = score['id']
            except KeyError:
                sc = Score(**score)
                db.session.add(sc)
            else:
                sc = Score.query.filter(Score.id == sc_id)
                sc.update({'value': score['value']})
                sc = sc.first()
            saved_scores.append(sc)
        db.session.commit()
        return saved_scores


@api.route("/eval/<int:eval_id>")
class ScoreEvalAPI(Resource):
    @api.marshal_with(score_model)
    def get(self, eval_id):
        """ Get all scores in the evaluation"""
        scores = Score.query\
                .join(Question, Question.id == Score.question_id)\
                .join(Exercise, Exercise.id == Question.exercise_id)\
                .join(Eval, Eval.id == Exercise.eval_id)\
                .filter(Eval.id == eval_id).all()
        return scores


@api.route("/exercise/<int:exercise_id>")
class ScoreExerciseAPI(Resource):
    @api.marshal_with(score_model)
    def get(self, exercise_id):
        """ Get all scores in the exerciseuation"""
        scores = Score.query\
                .join(Question, Question.id == Score.question_id)\
                .join(Exercise, Exercise.id == Question.exercise_id)\
                .filter(Exercise.id == exercise_id).all()
        return scores


@api.route("/student/<int:student_id>")
class ScoreEvalAPI(Resource):
    @api.marshal_with(score_model)
    def get(self, student_id):
        """ Get all scores of the student"""
        scores = Score.query\
                .join(Student, Student.id == Score.student_id)\
                .filter(Student.id == student_id).all()
        return scores

if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
