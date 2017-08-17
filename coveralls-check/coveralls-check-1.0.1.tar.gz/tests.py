import responses
from coveralls_check import main
from testfixtures import replace, ShouldRaise, OutputCapture

SAMPLE_JSON = {
    "commit_sha": "xyz",
    "coverage_change": 0,
    "covered_percent": 99.38
}


@responses.activate
@replace('sys.argv', ['script.py', 'xyz', '--fail-under', '99'])
def test_ok():
    responses.add(responses.GET, 'https://coveralls.io/builds/xyz.json',
                  json=SAMPLE_JSON)
    with OutputCapture() as output:
        main()
    output.compare('Coverage OK for xyz as 99.38 >= 99.0')


@responses.activate
@replace('sys.argv', ['script.py', 'xyz'])
def test_not_ok():
    responses.add(responses.GET, 'https://coveralls.io/builds/xyz.json',
                  json=SAMPLE_JSON)
    with ShouldRaise(SystemExit(2)):
        with OutputCapture() as output:
            main()
    output.compare('Failed coverage check for xyz as 99.38 < 100')
