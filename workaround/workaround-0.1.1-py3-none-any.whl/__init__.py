from collections import namedtuple

WorkaroundBase = namedtuple('WorkaroundBase', ['match', 'path', 'context', 'line'])


class Workaround(WorkaroundBase):
    @property
    def value(self):
        return self.match['value']

    @property
    def adjective(self):
        return self.match['adjective']

    @property
    def statement(self):
        return self.match['statement']

    @property
    def statement_span(self):
        return self.match.span('statement')

    def split_context(self):
        context_start, context_end = self.context
        matched_line = self.match.string
        statement_start, statement_end = self.statement_span

        return (
            context_start + matched_line[:statement_start],
            matched_line[statement_start:statement_end],
            matched_line[statement_end:] + context_end
        )
