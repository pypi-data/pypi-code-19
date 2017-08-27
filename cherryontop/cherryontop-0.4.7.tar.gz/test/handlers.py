from cherryontop import get, post
import json


@get("/foo")
def test():
    return json.dumps({"a": 1})


@post("/foo")
def blam():
    return json.dumps({"b": 2})


# @get("/foo")
# def x():
#     return "a"
