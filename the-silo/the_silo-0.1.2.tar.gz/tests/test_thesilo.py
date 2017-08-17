# the_silo tests


def test_gizmo_wrapper(nuke, wrapper):
    wrapper.create_gizmo('grade_layer')
    assert nuke.toNode('grade_layer1')


def test_multichannel(nuke, wrapper):
    assert True


def test_reload(nuke, wrapper):
    assert True
