"""
.. module:: view_train_images
   :synopsis: Example nuts-ml pipeline reading and viewing image data
"""

from nutsflow import Take, Consume, MapCol
from nutsml import ViewImageAnnotation, PrintColType

if __name__ == "__main__":
    from cnn_train import load_samples, load_names

    train_samples, _ = load_samples()
    names = load_names()

    id2name = MapCol(1, lambda i: names[i])
    show_image = ViewImageAnnotation(0, 1, pause=1, figsize=(2, 2),
                                     interpolation='spline36')

    (train_samples >> Take(10) >> id2name >> PrintColType() >>
     show_image >> Consume())
