def __ngrams(s, n=3):
    # Raw n-grams on sequences
    # If given a string, it will return char-level n-grams.
    # If given a list of words, it will return word-level n-grams.
    return list(zip(*[s[i:] for i in range(n)]))

def ngrams(s, n=3):
    # Does not take n-grams across word boundaries (' ')
    # If a word is shorter than n, the n-gram is the word.
    unpack = lambda l: sum(l, [])
    return unpack([__ngrams(w, n=min(len(w), n)) for w in s.split()])

def matching_ngrams(s1, s2, n=5):
    # See also: SequenceMatcher.get_matching_blocks
    ngrams1, ngrams2 = set(ngrams(s1, n=n)), set(ngrams(s2, n=n))
    return ngrams1.intersection(ngrams2)

def diff_ngrams(s1, s2, n=5):
    ngrams1, ngrams2 = set(ngrams(s1, n=n)), set(ngrams(s2, n=n))
    matches = ngrams1.intersection(ngrams2)
    return 2 * len(matches) / (len(ngrams1) + len(ngrams2))



