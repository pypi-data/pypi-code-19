from jinja2 import Environment, PackageLoader
import importlib
import os


class StaticHtmlGenerator:
    def __init__(self, output_directory, print_before_write=False, conf_import_path='configurations'):
        """
        Initialises the StaticHtmlGenerator
        :param output_directory: directory where the html files should be generated/written in.
        :param print_before_write: print html to stdout before writing to file.
        :param conf_import_path: import path for configurations, without any trailing dots. 
            Example: 'data.confs' or 'configurations'
        """
        self.output_directory = output_directory
        self.print_before_write = print_before_write
        self.conf_import_path = conf_import_path
        self.rendered_things = []
        self.jinja2_env = Environment(loader=PackageLoader('canni', 'templates'))  # this doesn't seem right (package)

    def _import_switch(self, conf_name):
        """
        Imports a configuration module based on the conf_import_path and the conf_name.
        :param conf_name: name of the configuration file to be loaded from the "./configurations/" path.
        :return: instance of the Switch class inside the configuration
        """
        return importlib.import_module(
            "{conf_dir}.{conf_name}".format(conf_dir=self.conf_import_path,conf_name=conf_name)).Switch()

    def render_index(self, *, output_filename, pagetitle):
        """
        Renders an index page which links to all rendered switch-pages.
        :param output_filename: name of the file to be rendered.
        :param pagetitle: html-title for the page.
        """
        rendered = self.jinja2_env.get_template('index.html').render(things=self.rendered_things, pagetitle=pagetitle)
        self._write_to_file(rendered, output_filename)

    def render_switch(self, conf_name, *, output_filename, pagetitle):
        """
        Renders a specific Switch of a configuration as html page.
        :param conf_name: name of the configuration to be used (source of the Switch)
        :param output_filename: name of the file to be rendered.
        :param pagetitle: html-title for the page.
        """
        switch = self._import_switch(conf_name)
        for tab in switch.get_tabinfos():
            tab.zipped_choices = self._zip_choices(tab)
        rendered = self.jinja2_env.get_template('switch.html').render(switch=switch, pagetitle=pagetitle)
        self._write_to_file(rendered, output_filename)
        self.rendered_things.append({'filename': output_filename, 'pagetitle': pagetitle})

    def _write_to_file(self, content, output_filename):
        """
        Write content into a file, which path is determined based on the set output_directory and the output_filename parameter.
        :param content: content to be written into the file.
        :param output_filename: name of the file to be written.
        """
        if self.print_before_write:
            print(content)
        with open(os.path.join(self.output_directory, output_filename), 'w') as f:
            f.write(content)

    @staticmethod
    def _zip_choices(tab):
        """
        Combine each title and text of a configuration into a touple and return the ordered list of touples.
        :param tab: tab, which choices should be zipped. 
        :return: ordered list of (title, text) touples.
        """
        zipped_choices = []
        for oc in tab.ordered_choices:
            zipped_choices.append((tab.choices[oc]['title'], tab.choices[oc]['text']))
        return zipped_choices


if __name__ == '__main__':
    shg = StaticHtmlGenerator(output_directory='gitlab-pages')
    shg.render_switch('tripletrouble', output_filename='tripletrouble.html', pagetitle='Canni Demo: Triple Trouble')
    shg.render_switch('amber', output_filename='amber.html', pagetitle='Canni Demo: Amber Wurm')
    shg.render_index(output_filename='index.html', pagetitle='Canni Demo')
