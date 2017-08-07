import pytest
from pathlib import Path
import yaml


from mattoolkit.template.representation import TransformationRepresentation


@pytest.mark.skip(reason='requires internet and auth')
def test_transformation_document(search_api=False):
    filename = Path('test_files/schemas/transformation.yaml')
    document = yaml.load(filename.open())
    transformation = TransformationRepresentation(document, filename)
    print(transformation.document)
