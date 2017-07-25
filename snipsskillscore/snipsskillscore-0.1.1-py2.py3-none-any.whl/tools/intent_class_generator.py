# -*-: coding utf-8 -*-
""" Tools to automatically generate intent classes from an assistant
definition.
"""

import os
import glob
import re
import json
import zipfile

from jinja2 import Environment, FileSystemLoader

JINJA_ENV = Environment(loader=FileSystemLoader('tools'))


def camel_case_to_underscore(text):
    """ Convert camel-case to underscore.

    :param text: a text, potentially in camel-case format.
    :return: the text, converted to underscore format.
    """
    underscored = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', underscored).lower()


def to_camelcase_capitalized(text):
    """ Convert to camel-case and capitalize.

    :param text: a text, potentially with dashes and underscores.
    :return: the text, converted to cancel-case format, and capitalized.
    """
    hyphens = re.sub(r'(?!^)-([a-zA-Z])', lambda m: m.group(1).upper(), text)
    underscores = re.sub(r'(?!^)_([a-zA-Z])',
                         lambda m: m.group(1).upper(), hyphens)
    return underscores[:1].upper() + underscores[1:]


def save_file(output_dir, filename, text):
    """ Save a text string to a given file.

    :param filename: a file name.
    :param text: a text to save.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists("{}/intents".format(output_dir)):
        os.makedirs("{}/intents".format(output_dir))
    output_filename = "{}/intents/{}".format(output_dir, filename)
    with open(output_filename, "w") as output_file:
        output_file.write(text)


def generate_intent_file(intent, output_dir):
    """ Given a JSON intent, generate the corresponding Python intent class
        file.

    :param intent: a JSON intent.
    """
    template = JINJA_ENV.get_template('templates/intent_template.py')
    # pylint: disable=no-member
    file_content = template.render(intent=intent)
    filename = camel_case_to_underscore(
        to_camelcase_capitalized(intent["name"])) + "_intent.py"
    save_file(output_dir, filename, file_content)


def generate_intent_registry_file(intents, output_dir):
    """ Given a list of intents, generate an intents registry, which is
        a list of intent classes.

    :param intents: a list of intents.
    """
    template = JINJA_ENV.get_template('templates/intent_registry_template.py')
    # pylint: disable=no-member
    file_content = template.render(intents=intents)
    with open("{}/intent_registry.py".format(output_dir), "w") as output_file:
        output_file.write(file_content)


def generate(assistant_dir, output_dir):
    """ Generate intent classes from assistant.json specification.

    :param assistant_dir: directory containing the zipped assistants.
    :param output_dir: directory to which the intents and registry should be
                       written.
    """
    JINJA_ENV.globals.update(
        camel_case_to_underscore=camel_case_to_underscore)
    JINJA_ENV.globals.update(
        to_camelcase_capitalized=to_camelcase_capitalized)

    intents = []
    for filename in glob.glob(assistant_dir + "/*.zip"):
        content = zipfile.ZipFile(filename).read('assistant/assistant.json')
        data = json.loads(content)
        for intent in data["intents"]:
            generate_intent_file(intent, output_dir)
            try:
                next(i for i in intents if i["name"] == intent["name"])
                print("****************************************************")
                print(
                    "WARNING: Duplicate intents found. " +
                    "This might lead to unexpected results.")
                print("****************************************************")
            except StopIteration:
                intents.append(intent)

    generate_intent_registry_file(intents, output_dir)
