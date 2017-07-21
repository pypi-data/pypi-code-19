"""Strategies for trainable document similarity. Similarity models consist of
three components:

1. Tensorizer (optional):
    Given a doc object of length M, return an (M, N) array. If no
    tensorizer is provided, the `doc.tensor` attribute is used for
    prediction. The `.update()` method will expect a tuple of (docs,
    tensors) for the batch, and return list of gradients with respect to
    the input tensors.

2. Summarizer (optional):
    Given the pair of document tensors, construct a single vector
    representing the pair.

3. Predictor: Given the pair-vector, return a scalar similarity judgment.

The baseline strategy is to return the cosine of summary vectors of the two
documents, constructed by concatenating the elementwise max and mean of their
tensors.
"""
from .compat import get_array_module


def cosine(vec1, vec2):
    xp = get_array_module(vec1)
    dot = vec1.dot(vec2)
    return dot / xp.sqrt((vec1 * vec1).sum() * (vec2 * vec2).sum())


