class TemplateNotEqualError(AssertionError):
    def __init__(self, msg, filename, *args, **kwargs):
        self.filename = filename
        super().__init__(msg, *args, **kwargs)
