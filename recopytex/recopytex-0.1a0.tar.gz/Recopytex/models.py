#!/usr/bin/env python
# encoding: utf-8

from Recopytex import db


class Tribe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    grade = db.Column(db.String(64), unique=False)
    students = db.relationship(
        "Student",
        backref="tribe",
        lazy="dynamic"
        )
    evals = db.relationship(
        "Eval",
        backref="tribe",
        lazy="dynamic"
        )

    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

    def __repr__(self):
        return f"<Tribe {self.name} (id={self.id})>"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    surname = db.Column(db.String(64), unique=False)
    mail = db.Column(db.String(64), unique=False)
    commment = db.Column(db.String(400), unique=False)
    tribe_id = db.Column(db.Integer, db.ForeignKey('tribe.id'))

    scores = db.relationship(
        "Score",
        backref="student",
        lazy="dynamic"
        )

    def __init__(self, name, surname, tribe_id,
            mail="", comment = ""):
        self.name = name
        self.surname = surname
        self.tribe_id = tribe_id
        self.mail = mail
        self.comment = comment

    def __repr__(self):
        return f"<Student {self.name} {self.surname}>"

    @property
    def fullname(self):
        """ Get name and surname joined """
        if not self.surname:
            return self.name
        return " ".join([self.name, self.surname])


class Eval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    term = db.Column(db.Integer, unique=False)
    type = db.Column(db.String(10), unique=False)
    comment = db.Column(db.String(400), unique=False)
    tribe_id = db.Column(db.Integer, db.ForeignKey('tribe.id'))

    exercises = db.relationship(
        "Exercise",
        backref="eval",
        lazy="dynamic"
        )

    def __init__(self, name, term, tribe_id,
            type = "", comment = "", **kwrds):
        self.name = name
        self.term = term
        self.tribe_id = tribe_id
        self.type = type
        self.comment = comment

    def __repr__(self):
        return f"<Eval {self.name}>"


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    eval_id = db.Column(db.Integer, db.ForeignKey('eval.id'))
    date = db.Column(db.DateTime, unique=False)
    comment = db.Column(db.String(400), unique=False)

    questions = db.relationship(
        "Question",
        backref="exercise",
        lazy="dynamic"
        )

    def __init__(self, name, eval_id, date,
                 comment="", **kwrds):
        self.name = name
        self.eval_id = eval_id
        self.date = date
        self.comment = comment

    def __repr__(self):
        return f"<Exercise {self.name}>"


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    score_rate = db.Column(db.Integer, unique=False)
    is_leveled = db.Column(db.Boolean, unique=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
    competence = db.Column(db.String(64), unique=False)
    domain = db.Column(db.String(64), unique=False)
    comment = db.Column(db.String(400), unique=False)

    scores = db.relationship(
        "Score",
        backref="question",
        lazy="dynamic"
        )

    def __init__(self, name, exercise_id, score_rate, is_leveled,
                 competence = "", domain = "", comment="", **kwrds):
        self.name = name
        self.exercise_id = exercise_id
        self.score_rate = score_rate
        self.is_leveled = is_leveled
        self.competence = competence
        self.domain = domain
        self.comment = comment

    def __repr__(self):
        return f"<Question {self.name}>"


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    value = db.Column(db.Integer, unique=False)

    def __init__(self, question_id, student_id, value):
        self.question_id = question_id
        self.student_id = student_id
        self.value = value

    def __repr__(self):
        return f"<Score {self.value}>"


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
