import mock

from seppelsmother.control import get_smother_filename  # nopep8


@mock.patch('seppelsmother.control.random')
@mock.patch('seppelsmother.control.socket')
@mock.patch('seppelsmother.control.os')
def test_parallel_mode_suffix(mock_os, mock_socket, mock_random):
    fake_pid = 12345
    fake_hostname = "the_host"
    fake_random_int = 99999
    mock_os.getpid.return_value = fake_pid
    mock_socket.gethostname.return_value = fake_hostname
    mock_random.randint.return_value = fake_random_int

    base_name = ".seppelsmother"
    fake_suffix = "the_host.12345.099999"
    assert get_smother_filename(base_name, False) == base_name
    assert (
        get_smother_filename(base_name, True) == base_name + "." + fake_suffix)

