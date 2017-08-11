"""
This file contains assorted general utility functions used by other
modules in the aiml_bot package.
"""


def split_sentences(text: str) -> list:
    """Split the string s into a list of sentences."""
    if not isinstance(text, str):
        raise TypeError("s must be a string")
    position = 0
    sentenceList = []
    l = len(text)
    while position < l:
        try:
            period = text.index('.', position)
        except ValueError:
            period = l + 1
        try:
            question = text.index('?', position)
        except ValueError:
            question = l + 1
        try:
            exclamation = text.index('!', position)
        except ValueError:
            exclamation = l + 1
        end = min(period, question, exclamation) + 1
        sentenceList.append(text[position:end].strip())
        position = end
    # If no sentences were found, return a one-item list containing
    # the entire input string.
    if len(sentenceList) == 0:
        sentenceList.append(text)
    return sentenceList
