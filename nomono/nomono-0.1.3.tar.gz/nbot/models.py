import logging
from django.db import models
from scrapyd_api import ScrapydAPI


class ScrapyTransaction:
    logger = logging.getLogger(__name__)

    def __init__(self, portal_url):
        self.portal_url = portal_url
        self.scrapyd = ScrapydAPI(portal_url)
        self.egg = None

    def __enter__(self):
        self.scrapyd = ScrapydAPI(self.portal.url)
        self.logger.debug('Open scrapy transaction to %(url)s' % self.portal)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.scrapyd.close()
        if self.egg is not None:
            self.egg.close()
        self.logger.debug('Close scrapy transaction to %(url)s' % self.portal)

    def projects(self):
        return self.scrapyd.list_projects()

    def create_project(self, egg_name='nomono.egg', project_name='nbot', project_version='1.0'):
        self.egg = open(egg_name)
        spider_count = self.scrapyd.add_version(project_name, project_version, egg_name)
        self.logger.debug(
            'From import %d spider to %s#%s.%s' % (spider_count, self.egg.name, self.portal.name, self.portal.version))

    def delete_project(self, project_name):
        self.scrapyd.delete_project(project_name)

    def versions_of_project(self, project_name):
        return self.scrapyd.list_versions(project_name)

    def delete_version(self, project_name, project_version):
        self.scrapyd.delete_version(project_name, project_version)

    def jobs_of_project(self, project_name):
        return self.scrapyd.list_jobs(project_name)

    def job_status(self, project_name, project_version):
        self.scrapyd.job_status(project_name, project_version)

    def job_cancel(self, project_name, consumer_tag):
        self.scrapyd.cancel(project_name, consumer_tag)

    def spiders_of_project(self, project_name):
        return self.scrapyd.list_spiders(project_name)

    def schedule_spider(self, project_name, spider_name, settings=None):
        self.scrapyd.schedule(project_name, spider_name, settings=settings)

    def schedule_spider(self, project_name, spider_name, extra_attribute):
        self.scrapyd.schedule(project_name, spider_name, extra_attribute=extra_attribute)

# Create your models here.
class Portal(models.Model):
    url = models.CharField(max_length=500)
    name = models.CharField(max_length=500)

    @property
    def projects(self):
        with ScrapyTransaction(portal_url=self.url) as t:
            return t.projects()

    @property
    def versions(self):
        with ScrapyTransaction(portal_url=self.url) as t:
            return t.versions_of_project(self.name)

    @property
    def spiders(self):
        with ScrapyTransaction(portal_url=self.url) as t:
            return t.spiders_of_project(self.name)

    @property
    def jobs(self):
        with ScrapyTransaction(portal_url=self.url) as t:
            return t.jobs_of_project(self.name)
