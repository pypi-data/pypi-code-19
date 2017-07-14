"""The fetch commands."""

from ORCSchlange.command import BaseCommand
from ORCSchlange.orcid import API
import itertools
import pybtex.database
from ORCSchlange.bib import join_bibliography, write_html
import shutil
from ORCSchlange.config import Config
import os.path


class FetchReporeter(BaseCommand):
    """The class that contains all fetch commands."""
    
    def fetch(self):
        """Fetch data from public ORCID API"""
        self.debug("Read config")
        Config(self.args)
        if not Config().ready:
            if self.args.config == 1:
                self.error("No configuration found in db.")
            else:
                self.error("No valid json file.")
            return
        self.open()
        
        self.debug("Read orchids")
        orcs = self.db.get_orcids()
        
        self.close()
        
        self.debug("Open API connection")
        api = API()
        
        self.debug("Get all work summaries")
        alldocs = []
        for orc in orcs:
            docs = api.get_worksums(orc)
            alldocs += docs
        
        self.debug("Sort all work summaries")
        alldocs.sort()
        
        self.debug("Make entries uniques")
        uniqdocs = []
        for doc, _ in itertools.groupby(alldocs):
            uniqdocs.append(doc)
        
        works_api = dict()
        uniqdocs.sort(key=lambda x: x.orc)
        for key, docs in itertools.groupby(uniqdocs, key=lambda x: x.orc):
            works_api[key] = [str(x.id) for x in docs]
        
        self.debug("Get complete works")
        entries = pybtex.database.BibliographyData()
        
        for key in works_api:
            for ent in api.get_works(key, works_api[key]):
                join_bibliography(entries, ent)
        
        self.args.path = self.args.path if self.args.path.endswith("/") else self.args.path + "/"
        
        if self.args.bib:
            self.debug("Write bib in {path}{name}.bib".format(**vars(self.args)))
            entries.to_file(open("{path}{name}.bib".format(**vars(self.args)), "w"))
        if self.args.html:
            self.debug("Write html in {path}{name}.html".format(**vars(self.args)))
            write_html(entries, path="{path}{name}.html".format(**vars(self.args)))
        if self.args.jquery:
            jname = "jquery-3.2.1.min.js"
            self.debug("Copy jQuery to {path}{jname}".format(path=self.args.path, jname=jname))
            shutil.copyfile(os.path.dirname(__file__) + "/{jname}".format(jname=jname),
                            "{path}{jname}".format(path=self.args.path, jname=jname))
