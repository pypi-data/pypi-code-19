from pathlib import Path

import pytest
import yaml
from marshmallow import ValidationError
from mattoolkit.template.schema import VaspInputSchema


def test_correct_vasp_inputs():
    filename = Path('test_files/schemas/vasp_correct.yaml')
    for document in yaml.load_all(filename.open()):
        errors = VaspInputSchema(strict=True).validate(document)
        print(errors)

def test_incorrect_vasp_inputs():
    filename = Path('test_files/schemas/vasp_incorrect.yaml')
    for document in yaml.load_all(filename.open()):
        with pytest.raises(ValidationError) as error_info:
            errors = VaspInputSchema(strict=True).validate(document)
            print(errors)
