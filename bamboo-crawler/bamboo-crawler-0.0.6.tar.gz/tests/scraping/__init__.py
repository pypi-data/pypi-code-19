import json
import subprocess
import unittest


class TestScraping(unittest.TestCase):
    def run_recipe(self, taskname):
        c = subprocess.run([
            'python', '-m',
            'bamboo_crawler',
            '-r', 'tests/scraping/recipe.yml',
            '-t', taskname],
            stdout=subprocess.PIPE)
        self.assertEqual(c.returncode, 0)
        return c

    def test_mixed_scraper(self):
        c = self.run_recipe('mixed_scrape')
        j = json.loads(c.stdout)
        self.assertEqual(j['x'][0], 'test_message01')
        self.assertEqual(j['y'][0], 'test_message02')

    def test_python_processor(self):
        c = self.run_recipe('python_processor')
        j = json.loads(c.stdout)
        self.assertEqual(j['x'], 'abc')
        self.assertEqual(j['y'], 'xxxyyyzzz')
