#!/usr/bin/env python
# encoding: utf-8

from Recopytex import db
from Recopytex.models import Tribe
from flask_restplus import Resource, Namespace, fields, reqparse
from werkzeug.exceptions import BadRequest

api = Namespace(
        name="tribes",
        desciption="Querying on Tribes"
        )

student_model = api.model("Student", {
    "id" : fields.Integer,
    "name" : fields.String(attribute="fullname"),
    })

eval_model = api.model("Eval", {
    "id" : fields.Integer,
    'name': fields.String,
    })

tribe_model = api.model("Tribe", {
    'id': fields.Integer,
    'name': fields.String,
    'grade': fields.String,
    'students': fields.List(fields.Nested(student_model)),
    'evals': fields.List(fields.Nested(eval_model)),
    })

tribe_parser = reqparse.RequestParser()
tribe_parser.add_argument('name',
                         type=int,
                         required=True,
                         help="Tribe number"
                         )
tribe_parser.add_argument('grade',
                         type=str,
                         help="Grade of the tribe"
                         )

@api.route("/")
class TribesAPI(Resource):
    @api.marshal_with(tribe_model)
    def get(self):
        """ List of tribes """
        tribes = Tribe.query.all()
        return tribes

    @api.marshal_with(tribe_model)
    def post(self):
        """ Creating a tribe """
        args = tribe_parser.parse_args()
        tribe_name = args["name"]
        if not args["grade"]:
            try:
                grade = int(str(tribe_name)[0])
            except ValueError:
                raise ValueError(f"Tribename needs to start with a digit if no grade are given")
        else:
            grade = args["grade"]
        tribe = Tribe(tribe_name, grade)
        db.session.add(tribe)
        db.session.commit()
        return tribe


@api.route("/<int:tribe_id>")
@api.response(404, "Tribe not found")
class TribeAPI(Resource):
    @api.marshal_with(tribe_model)
    def get(self, tribe_id):
        """ Get students and evaluations on the class """
        tribe = Tribe.query.filter(Tribe.id==tribe_id).first()
        return tribe

    def put(self, tribe_id):
        """ Update the tribe """
        raise BadRequest("Pour le mettre en oeuvre, il faudrait mettre un vrai id aux tribus")


    @api.response(204, 'Tribe deleted')
    def delete(self, tribe_id):
        """ Delete the tribe """
        tribe = Tribe.query.filter(Tribe.id==tribe_id).first()
        db.session.delete(tribe)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
