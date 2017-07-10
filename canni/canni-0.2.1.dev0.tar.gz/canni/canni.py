from jinja2 import Environment, PackageLoader
import importlib
import os


class StaticHtmlGenerator:
    def __init__(self, output_directory, print_before_write=False):
        self.output_directory = output_directory
        self.print_before_write = print_before_write
        self.rendered_switches = []
        env = Environment(loader=PackageLoader('canni', 'templates'))
        self.switch_template = env.get_template('switch.html')
        self.index_template = env.get_template('index.html')

    def _import_switch(self, conf_name):
        conf_module = importlib.import_module("configurations.{}".format(conf_name))
        return conf_module.Switch()

    def render_index(self, *, output_filename, pagetitle):
        rendered = self.index_template.render(switches=self.rendered_switches, pagetitle=pagetitle)
        self._write_to_file(rendered, output_filename)

    def render_switch(self, conf_name, *, output_filename, pagetitle):
        switch = self._import_switch(conf_name)
        for tab in switch.get_tabinfos():
            tab.zipped_choices = self._zip_choices(tab)
        rendered = self.switch_template.render(switch=switch, pagetitle=pagetitle)
        self._write_to_file(rendered, output_filename)
        self.rendered_switches.append({'filename': output_filename, 'pagetitle': pagetitle})

    def _write_to_file(self, content, output_filename):
        if self.print_before_write:
            print(content)
        with open(os.path.join(self.output_directory, output_filename), 'w') as f:
            f.write(content)

    @staticmethod
    def _zip_choices(tab):
        zipped_choices = []
        for oc in tab.ordered_choices:
            zipped_choices.append((oc, tab.choices[oc]['text']))
        return zipped_choices


if __name__ == '__main__':
    shg = StaticHtmlGenerator(output_directory='gitlab-pages')
    shg.render_switch('tripletrouble', output_filename='tripletrouble.html', pagetitle='Canni Demo: Triple Trouble')
    shg.render_index(output_filename='index.html', pagetitle='Canni Demo')
