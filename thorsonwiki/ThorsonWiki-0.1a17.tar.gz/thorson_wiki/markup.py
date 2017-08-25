import markdown

class ThorsonMarkdown(markdown.Markdown):

    def __init__(self, *args, **kwargs):

        super(ThorsonMarkdown, self).__init__(*args, **kwargs)

        self.namespace = kwargs.get('namespace', None)
        self.namespace_ = kwargs.get('namespace_', None)
        self.request = kwargs.get('request', None)
