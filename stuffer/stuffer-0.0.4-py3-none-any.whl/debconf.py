from stuffer import apt
from stuffer.core import Action


class SetSelections(Action):
    def __init__(self, section, template, type_, value):
        self.section = section
        self.template = template
        self.type_ = type_
        self.value = value
        super(SetSelections, self).__init__()

    def prerequisites(self):
        return [apt.Install('debconf-utils', update=False)]

    def use_shell(self):
        return True

    def command(self):
        return "echo {} {} {} {} | debconf-set-selections".format(self.section, self.template, self.type_, self.value)
