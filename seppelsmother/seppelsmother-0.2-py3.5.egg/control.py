import json
import os
import random
import re
import socket
from contextlib import contextmanager
import logging

import six
from portalocker import Lock

from .python import PythonFile


logging.basicConfig(filename='.seppelsmother_log', filemode='w', level=logging.DEBUG)


def get_smother_filename(base_name, parallel_mode):
    if parallel_mode:
        suffix = "%s.%s.%06d" % (
            socket.gethostname(), os.getpid(),
            random.randint(0, 999999)
        )
        base_name += "." + suffix
    return base_name


@contextmanager
def noclose(file):
    """
    A "no-op" contextmanager that prevents files from closing.
    """
    try:
        yield file
    finally:
        pass

pattern = re.compile("[\(\[].*?[\)\]]")

class SeppelSmother(object):

    def __init__(self, coverage=None):
        self.coverage = coverage
        self.data = []

    def start(self):
        # We will never need branch coverage
        self.coverage.collector.branch = False
        self.coverage.collector.reset()
        self.coverage.start()

    def delete_program_part_identifier(self, string):
        new_string = re.sub(pattern, "", string)
        return new_string.replace(" ", "")

    def save_context(self, label):
        # The first unnamed part is the coverage during import, but this is not interesting to us
        if not label:
            return

        # If first part of label ends with .py, we have a pytest
        parts = label.split(":")
        if parts[0].endswith(".py"):
            logging.info("Found py.test")
            label = label.replace("::", ":")
            parts = label.split(":")
            module = parts[0].replace("/", ".")[:-3]

            if len(parts[1:-1]) > 0:
                namespace = ""
            else:
                namespace = None

            for part in parts[1:-1]:
                # () can be things from classes
                if part != "()":
                    namespace += part+"."

            # arguments to tests are wrapped into [], but we do not need it here
            if "[" in parts[-1]:
                method = parts[-1].split("[")[0]
            else:
                method = parts[-1]

            if namespace is not None:
                namespace = namespace.strip(".")
                unique_id = module+":"+namespace+":"+method
            else:
                unique_id = module+":"+method
        else:
            logging.info("Found nosetest")
            unique_id = label
            module = label.split(":")[0]

            qualified_name = label.split(":")[1]
            namespace = ".".join(qualified_name.split(".")[0:-1])
            if not namespace:
                namespace = None
            method = qualified_name.split(".")[-1]

        test = {
            "unique_id": unique_id,
            "module": module,
            "namespace": namespace,
            "method": method,
            "tests": list(),
        }
        logging.info("Looking at test with id: %s" % unique_id)
        logging.debug("Module: %s, Namespace: %s, Method: %s" % (module, namespace, method))
        # Go through the whole coverage data
        # label = semantic test name (e.g., tests.test_module2:Module2Test.testYWithX
        # key = path to python file (e.h. ~/src/test/resources/module2.py
        # val = list of covered lines
        for key, val in self.coverage.collector.data.items():
            dict_with_tested_part_and_lines = {}

            # Parse the python file
            pf = PythonFile(key)

            # Go through all covered lines
            try:
                lines = sorted(map(int, val.keys()))
            except Exception:
                logging.warning("Got tuple %s for key %s. This is strange.. So skip it (but not silently)!" % (val.keys(), key))
                continue
                
            for line in lines:
                # Get the semantic name of the line
                semantic_name = pf.context(line)

                # If it is already in the dictionary we add the line to covered_lines, and remove it from
                # the uncovered_lines
                if semantic_name in dict_with_tested_part_and_lines:
                    dict_with_tested_part_and_lines[semantic_name]["covered_lines"].append(line)
                    dict_with_tested_part_and_lines[semantic_name]["uncovered_lines"].remove(line)

                else:
                    # Get the start and the enf of the method/class/whatever and create a list of lines
                    (lo, hi) = pf.context_range(semantic_name)
                    uncovered_lines = list(range(lo, hi))

                    # Remove the start, as the definition is never covered
                    uncovered_lines.remove(lo)

                    # If the covered line is the start, than do nothing
                    if line in uncovered_lines:
                        uncovered_lines.remove(line)

                    dict_with_tested_part_and_lines[semantic_name] = {
                        "uncovered_lines": uncovered_lines,
                        "covered_lines": [line]
                    }

            for test_name, values in dict_with_tested_part_and_lines.items():
                # If there is no ":" we can just continue, as no function was called
                if ":" not in test_name:
                    continue
                qualified_name = test_name.split(":")[1]
                namespace = self.delete_program_part_identifier(".".join(qualified_name.split(".")[0:-1]))
                if not namespace:
                    namespace = None
                tested = {
                    "location": key,
                    "unique_id": test_name,
                    "module": self.delete_program_part_identifier(test_name.split(":")[0]),
                    "namespace": namespace,
                    "method": self.delete_program_part_identifier(qualified_name.split(".")[-1]),
                    "uncovered_lines": values["uncovered_lines"],
                    "covered_lines": values["covered_lines"],
                }
                logging.info("Tests: %s" % tested["unique_id"])
                logging.debug("Tested part has: location %s, module %s, namespace %s, method %s, uncovered_lines %s, covered_lines %s" % (tested["location"], tested["module"], tested["namespace"], tested["method"], tested["uncovered_lines"], tested["covered_lines"]))
                test["tests"].append(tested)
        self.data.append(test)


    def write(self, file_or_path, timeout=10):
        """
        Write Smother results to a file.

        Parameters
        ----------
        file_or_path : str
            Path to write report to
        timeout : int
            Time in seconds to wait to acquire a file lock, before
            raising an error.

        Note
        ----
        Append mode is atomic when file_or_path is a path,
        and can be safely run in a multithreaded or
        multiprocess test environment.

        When using `parallel_mode`, file_or_path is given a unique
        suffix based on the machine name and process id.
        """
        if isinstance(file_or_path, six.string_types):
            if self.coverage:
                file_or_path = get_smother_filename(
                    file_or_path, self.coverage.config.parallel)

            outfile = Lock(
                file_or_path, mode='a+',
                timeout=timeout,
                fail_when_locked=False
            )
        else:
            outfile = noclose(file_or_path)

        with outfile as fh:
            fh.seek(0)
            fh.truncate()  # required to overwrite data in a+ mode
            json.dump(self.data, fh)


