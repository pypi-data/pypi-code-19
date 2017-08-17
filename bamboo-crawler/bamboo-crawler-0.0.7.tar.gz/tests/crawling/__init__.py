import subprocess
import unittest


class TestCrawling(unittest.TestCase):
    def setUp(self):
        server = subprocess.Popen([
            'python',
            '-m', 'http.server',
            '8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='tests/crawling/assets')
        self.server = server

    def tearDown(self):
        server = self.server
        server.stderr.close()
        server.stdout.close()
        server.kill()
        server.wait()

    def run_recipe(self, taskname):
        c = subprocess.run([
            'python', '-m',
            'bamboo_crawler',
            '-r', 'tests/crawling/recipe.yml',
            '-t', taskname],
            stdout=subprocess.PIPE)
        self.assertEqual(c.returncode, 0)
        return c

    def test_something(self):
        c = self.run_recipe('index_html')
        self.assertEqual(c.stdout, b'<body>test!test!test!</body>\n')
