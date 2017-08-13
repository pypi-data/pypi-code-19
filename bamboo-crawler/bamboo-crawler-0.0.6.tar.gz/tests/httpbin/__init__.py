import json
import subprocess
import unittest


class TestRecipeTask(unittest.TestCase):
    def setUp(self):
        httpbin = subprocess.Popen([
            'python', '-m', 'httpbin.core',
            '--host', '127.0.0.1',
            '--port', '4000'],
            stderr=subprocess.PIPE)
        httpbin.stderr.readline()
        self.httpbin = httpbin

    def tearDown(self):
        httpbin = self.httpbin
        httpbin.stderr.close()
        httpbin.kill()
        httpbin.wait()

    def run_recipe(self, taskname):
        c = subprocess.run([
            'python', '-m',
            'bamboo_crawler',
            '-r', 'tests/httpbin/recipe.yml',
            '-t', taskname],
            stdout=subprocess.PIPE)
        self.assertEqual(c.returncode, 0)
        return c

    def test_constant_inputter_test(self):
        c = self.run_recipe('constant_inputter_test')
        expect = b'abc1234'
        self.assertEqual(c.stdout, expect)

    def test_constant_inputter_with_metadata(self):
        c = self.run_recipe('constant_inputter_with_metadata')
        expect = b'abc1234'
        self.assertEqual(c.stdout, expect)

    def test_fetch_task(self):
        c = self.run_recipe('fetch_task')
        expect = b'User-agent: *\nDisallow: /deny\n'
        self.assertEqual(c.stdout, expect)

    def test_user_agent(self):
        c = self.run_recipe('user_agent')
        j = json.loads(c.stdout)
        expect = 'Testing User Agent'
        self.assertEqual(j['user-agent'], expect)
