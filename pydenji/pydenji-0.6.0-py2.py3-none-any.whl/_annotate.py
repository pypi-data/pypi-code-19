# -*- coding: utf-8 -*-
# (C) 2011 Alan Franzoni.

# very basic annotation support.

def makeAnnotation(name, prefix="_PYDENJI_"):
    """
    @return decorator, is_annotated_with_name function
    """
    def annotate(obj):
        setattr(obj, prefix + name, True)
        return obj


    def is_object_annotated(obj):
        return getattr(obj, prefix + name, False)

    return annotate, is_object_annotated

