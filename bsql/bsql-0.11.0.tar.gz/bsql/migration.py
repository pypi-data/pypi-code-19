
import os, subprocess, traceback, logging
from glob import glob
from bl.dict import Dict

from .model import Model

LOG = logging.getLogger(__name__)

class Migrate(Dict):
    def __init__(self, db, **Database):
        super().__init__(db=db, **Database)
    def __call__(self):
        Migration.migrate(self.db, migrations=self.migrations)

class Migration(Model):
    relation = 'migrations'
    pk = ['id']

    @classmethod
    def create_id(M, filename):
        return os.path.basename(os.path.splitext(filename)[0])

    @classmethod
    def migrate(M, db, migrations=None):
        """update the database with unapplied migrations"""
        migrations = migrations or db.migrations
        try:
            # will throw an error if this is the first migration -- migrations table doesn't yet exist.
            # (and this approach is a bit easier than querying for the existence of the table...)
            migrations_ids = [r.id for r in M(db).select()]
            LOG.debug("migrations_ids = " + str(migrations_ids))
        except:
            migrations_ids = []
        fns = [fn for fn 
                in glob(os.path.join(migrations, "[0-9]*-*.*"))     # active migrations have SEQ-NAME.*
                if M.create_id(fn) not in migrations_ids]
        fns.sort()
        LOG.info("Migrate Database: %d migrations in %r" % (len(fns), migrations))
        for fn in fns:
            id = M.create_id(fn)
            LOG.debug(id + ': ' + fn)
            ext = os.path.splitext(fn)[1]
            if id in migrations_ids: 
                continue
            else:
                f = open(fn, 'r'); script = f.read(); f.close()
                description = script.split("\n")[0].strip('-#/*; ') # first line is the description
                LOG.info(id+ext + ': ' + description)
                cursor = db.cursor()
                try:
                    if ext=='.sql':                                     # script is a SQL script, db.execute it
                        db.execute(script, cursor=cursor)
                    else:                                               # script is system script, subprocess it
                        subprocess.check_output(script, {'db': db})
                    migration = M(db, id=id, description=description)
                    cursor.connection.commit()
                    migration.insert()
                except:
                    cursor.connection.rollback()
                    raise
                cursor.close()
