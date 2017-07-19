"""
.. module:: view_train_images
   :synopsis: Example for showing images with annotation
"""

from nutsflow import Take, Consume
from nutsml import ViewImageAnnotation

if __name__ == "__main__":
    from mlp_train import load_samples

    samples, _ = load_samples()
    (samples >> Take(10) >> ViewImageAnnotation(0, 1, pause=1) >> Consume())
