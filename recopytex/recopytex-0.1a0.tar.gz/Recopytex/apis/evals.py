#!/usr/bin/env python
# encoding: utf-8

from Recopytex import db
from Recopytex.models import Eval, Exercise, Question, Score, Student
from flask_restplus import Resource, Namespace, fields, reqparse
from werkzeug.exceptions import BadRequest
import datetime

api = Namespace(
        name="evals",
        desciption="Manipulate evaluation"
        )

question_model = api.model("question", {
    "id": fields.Integer,
    'name': fields.String,
    "score_rate": fields.Fixed(decimals=1),
    "is_leveled": fields.Boolean,
    "competence": fields.String,
    "domain": fields.String,
    "comment": fields.String,
    })

exercise_model = api.model("exercise", {
    "id": fields.Integer,
    'name': fields.String,
    'date': fields.Date,
    'questions': fields.List(fields.Nested(question_model)),
    })

tribe_model = api.model("tribe", {
    "id": fields.Integer,
    'name': fields.String,
    })

eval_model = api.model("Eval", {
    'id': fields.Integer,
    #'tribe': fields.Nested(tribe_model),
    'tribe': fields.Integer(attribute="tribe_id"),
    'name': fields.String,
    'term': fields.Integer,
    'type': fields.String,
    'comment': fields.String,
    'exercises': fields.List(fields.Nested(exercise_model)),
    })

eval_parser = reqparse.RequestParser()
eval_parser.add_argument('id',
                         type=int,
                         required=False,
                         help="Eval id"
                         )
eval_parser.add_argument('name',
                         type=str,
                         required=True,
                         help="Eval name"
                         )
eval_parser.add_argument('tribe',
                         #type=dict,
                         type=int,
                         required=True,
                         help="Tribe's id of the eval"
                         )
eval_parser.add_argument('term',
                         type=int,
                         required=True,
                         help="Term of the eval"
                         )
eval_parser.add_argument('type',
                         type=str,
                         required=False,
                         help="Type of the eval (DS, DM, Conn...)"
                         )
eval_parser.add_argument('comment',
                         type=str,
                         help="Comments on the eval"
                         )
eval_parser.add_argument('exercises',
                         type=list,
                         #required=True,
                         help="List of exercises",
                         location='json'
                         )

@api.route("/")
class EvalsAPI(Resource):
    @api.marshal_with(eval_model)
    def get(self):
        """ List of evals """
        evals = Eval.query.all()
        return evals

    @api.marshal_with(eval_model)
    def post(self):
        """ Creating a eval """
        args = eval_parser.parse_args()
        args["tribe_id"] = args["tribe"]
        eval_= Eval(**args)
        db.session.add(eval_)
        db.session.commit()
        print(f"Create Eval -> {eval_} ({eval_.id})")

        try:
            assert not(args["exercises"] is None)
        except AssertionError:
            pass
        else:
            for exo in args["exercises"]:
                exo["eval_id"] = eval_.id
                exo["date"] = datetime.datetime.strptime(exo['date'], '%Y-%m-%d')
                newExercise(exo)
        return eval_

@api.route("/<int:eval_id>")
class EvalAPI(Resource):
    @api.marshal_with(eval_model)
    def get(self, eval_id):
        """ Get students and evaluations on the class """
        eval_ = Eval.query.filter(Eval.id == eval_id).first()
        print(f"getting: {eval_}")
        return eval_

    @api.marshal_with(eval_model)
    def put(self, eval_id):
        """ Update the eval """
        args = eval_parser.parse_args()
        assert args['id'] == eval_id

        eval_ = Eval.query.filter(Eval.id == eval_id)
        eval_.update({
            'name': args["name"],
            'term': args["term"],
            'tribe_id': args["tribe"],
            'type': args["type"],
            'comment': args["comment"]
            })
        eval_ = eval_.first()
        print(f"Updating: {eval_}")
        db.session.commit()
        for exo in args["exercises"]:
            exo["eval_id"] = eval_.id
            exo["date"] = datetime.datetime.strptime(exo['date'], '%Y-%m-%d')
            try:
                exo["id"]
            except KeyError:
                newExercise(exo)
            else:
                updateExercise(exo)
        return eval_

    def delete(self, eval_id):
        """ Delete the eval """
        eval_ = Eval.query.filter(Eval.id == eval_id).first()
        db.session.delete(eval_)
        db.session.commit()
        print(f"Delete {eval_}")
        return '', 204

@api.route("/tribe/<int:tribe_id>")
@api.response(404, "Tribe not found")
class EvalsTribeAPI(Resource):
    @api.marshal_with(eval_model)
    def get(self, tribe_id):
        """ Get evals of a tribe"""
        evals = Eval.query\
                .filter(Eval.tribe_id == tribe_id)\
                .all()
        return evals

@api.route("/student/<int:student_id>")
@api.response(404, "Student not found")
class EvalsTribeAPI(Resource):
    @api.marshal_with(eval_model)
    def get(self, student_id):
        """ Get evals of a student"""
        evals = Eval.query\
                .join(Exercise, (Exercise.eval_id==Eval.id))\
                .join(Question, (Question.exercise_id==Exercise.id))\
                .join(Score, (Score.question_id==Question.id))\
                .join(Student, (Score.student_id==Student.id))\
                .filter(Student.id==student_id)\
                .all()
                
        return evals

def newExercise(exercise):
    """ Create a new  exercise in DDB """
    ex = Exercise(**exercise)
    db.session.add(ex)
    db.session.commit()
    print(f"Create exercise -> {ex} ({ex.id})")
    for quest in exercise["questions"]:
        quest["exercise_id"] = ex.id
        newQuestion(quest)
    return ex

def updateExercise(exercise):
    """ Create a new  exercise in DDB """
    ex = Exercise.query.filter(Exercise.id == exercise['id'])
    ex.update({
            'name': exercise['name'],
            'eval_id': exercise['eval_id'],
            'date': exercise['date'],
            #'comment': exercise['comment'],
            })
    db.session.commit()
    ex = ex.first()
    print(f"Updating exercise -> {ex} ({ex.id})")
    for quest in exercise["questions"]:
        quest["exercise_id"] = ex.id
        try:
            quest["id"]
        except KeyError:
            newQuestion(quest)
        else:
            updateQuestion(quest)
    return ex

def newQuestion(quest):
    """ Create a new question in DDB """
    qu = Question(**quest)
    db.session.add(qu)
    db.session.commit()
    print(f"Creating quest -> {qu} ({qu.id})")
    return qu

def updateQuestion(quest):
    """ Update the question """
    qu = Question.query.filter(Question.id == quest['id'])
    #qu.update(**quest)
    qu.update({
            'name': quest['name'],
            'score_rate': quest['score_rate'],
            'is_leveled': quest['is_leveled'],
            'exercise_id': quest['exercise_id'],
            'competence': quest['competence'],
            'domain': quest['domain'],
            'comment': quest['comment'],
            })
    db.session.commit()
    qu = qu.first()
    print(f"Updating quest -> {qu} ({qu.id})")
    return qu

if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
