def test_split_context(workaround):
    split_context = workaround.split_context()
    assert len(split_context) == 3
    assert all(split_context)


def test_adjective(workaround):
    assert workaround.adjective == 'one two'


def test_value(workaround):
    assert workaround.value == 'three'


def test_statement(workaround):
    assert workaround.statement == workaround.match.string
