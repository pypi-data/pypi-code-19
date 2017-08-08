class Automata:
    """
    Implements an Automaton.

    Definition:

    (Wikipedia) A deterministic finite automaton is represented formally by a
    5-tuple (Q, Σ, δ, q0, F), where:

    * ``.states``: Q is a finite set of states
    * ``.alphabet``: Σ is a finite set of symbols, called the alphabet of the
      automaton.
    * ``.sigma(state, tk)``: δ is the transition function, that is,
      δ: Q × Σ → Q.
    * ``.start``: q0 is the start state, that is, the state of the automaton
      before any input has been processed, where q0 ∈ Q.
    * ``.accept``: F is a set of states of Q (i.e. F ⊆ Q) called accept states.
    """

    start = None
    states = set()
    alphabet = set()
    accept = set()
    description = ""

    @staticmethod
    def sigma(state, tk):
        "Return the next state from the current one and an input token."
        raise NotImplementedError('must implement the sigma method!')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(k)
        
        self.state = self.start 

        assert self.start is not None, \
            'Start state must be defined!'
        assert self.is_valid_state(self.start), \
            'Start state (%r) is not listed on the list of states' % self.start

    def is_valid_state(self, state):
        "True if state is an acceptable state."
        return state in self.states

    def is_valid_token(self, token):
        "True if token is an accetable token."
        return token in self.alphabet

    def next(self, tk):
        """
        Performs a single step with automata and transition from current
        state to the next by consuming the given word.
        """

        if not self.is_valid_token(tk):
            raise RuntimeError('invalid token: %r' % tk)

        state = self.sigma(self.state, tk)

        if self.is_valid_state(state):
            self.state = state
        else:
            raise RuntimeError('invalid state: %r' % state)

    def run(self, tk_seq):
        """
        Takes a (possibly lazy) sequence of words and consume it until it 
        terminates or if the machine halts (in which case it raises an
        RuntimeError).
        """

        for tk in tk_seq:
            self.next(tk)

    def __call__(self, tk_seq):
        self.state = self.start
        self.run(tk_seq)
        return self.state


class DFA(Automata):
    """
    Discrete finite automata.

    The transition function is defined by a dictionary mapping tuples of
    {(state, token): new state}.
    """

    transitions = {}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        assert all(self.is_valid_state(s) for s in self.accept), \
            'Some valid states are not present on the list of states.'

        if not self.alphabet:
            self.alphabet = {k for _st, k in self.transitions}

    def sigma(self, state, tk):
        return self.transitions[state, tk]

    def validate(self, tk_seq):
        "Runs automata and return True if it ends in a valid state."

        return self(tk_seq) in self.accept


class NFA(Automata):
    """
    A nondeterministic finite automata.
    """
    # TODO


class Turing(Automata):
    """
    A turing machine.
    """
    # TODO
