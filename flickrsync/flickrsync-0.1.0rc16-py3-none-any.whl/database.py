import sqlite3
import time
import logging
from flickrsync.log import Log
from flickrsync.error import Error

logger = logging.getLogger(Log.NAME)

class Database:

    def __init__(self, database):
        logger.debug('database<%s>' % database)
        assert database, 'Database is <%s>' % database

        try:
            self.con = sqlite3.connect(database, check_same_thread=False)
        except Exception:
            raise Error("Unable to connect to database <%s>" % database)

        self.con.row_factory = sqlite3.Row
        assert self.con, "Database connection not created"

        self.__create_tables_if_not_exist()

    def __exit__(self):
        self.do_commit()
        self.con.close()

    def do_commit(self):
        try:
            self.con.commit()
            logger.debug('committed')
        except Exception as e:
            logger.error(e)

    def get_new_files(self, newsearch):
        assert newsearch, "No newsearch records supplied"
        logger.debug('newsearch.count<%d>' % len(newsearch))
        self.__drop_table('Search')
        self.__create_search_table()
        self.__insert_search_files(newsearch)
        newfiles = self.__select_new_files()

        return newfiles

    def drop_local_photos_table(self):
        self.__drop_table('LocalPhotos')

    def drop_flickr_photos_table(self):
        self.__drop_table('FlickrPhotos')

    def create_flickr_photosets_table(self):
        with self.con:
            self.con.execute("""CREATE TEMPORARY TABLE FlickrPhotosets(
                                            Id INTEGER PRIMARY KEY,
                                            Title TEXT,
                                            Description TEXT,
                                            DateCreate INTEGER,
                                            DateUpdate INTEGER)""")
            logger.debug('FlickrPhotosets table created')

            self.con.execute("CREATE INDEX idx_fps1 ON FlickrPhotosets(Title)")
            logger.debug('index created')

    def create_flickr_photos_table(self):
        with self.con:
            self.con.execute("""CREATE TABLE FlickrPhotos(
                                            Id INTEGER PRIMARY KEY,
                                            Title TEXT,
                                            OriginalFormat TEXT,
                                            DateUpload INTEGER,
                                            DateTaken TEXT,
                                            DateTakenUnknown INTEGER,
                                            DateTakenGranularity INTEGER,
                                            Url_o TEXT,
                                            OriginalSecret TEXT,
                                            Farm INTEGER,
                                            Server INTEGER,
                                            Tags TEXT,
                                            Machine_Tags TEXT,
                                            Signature TEXT,
                                            ShortName TEXT,
                                            DateFlat INTEGER)""")
            logger.info('FlickrPhotos table created')

            self.con.execute("CREATE INDEX idx_fp1 ON FlickrPhotos(Signature, DateFlat, ShortName)")
            self.con.execute("CREATE INDEX idx_fp2 ON FlickrPhotos(Signature)")
            self.con.execute("CREATE INDEX idx_fp3 ON FlickrPhotos(DateFlat)")
            self.con.execute("CREATE INDEX idx_fp4 ON FlickrPhotos(ShortName)")
            self.con.execute("CREATE INDEX idx_fp5 ON FlickrPhotos(Id, OriginalSecret)")
            logger.debug('index created')

    def create_local_photos_table(self):
        with self.con:
            self.con.execute("""CREATE TABLE LocalPhotos(
                                            Directory TEXT,
                                            FileName TEXT,
                                            DateTimeOriginal TEXT,
                                            Signature TEXT,
                                            FlickrId INTEGER,
                                            FlickrSecret TEXT,
                                            FlickrTitle TEXT,
                                            FlickrExtension TEXT,
                                            ImageError TEXT,
                                            ShortName TEXT,
                                            DateFlat INTEGER,
                                            Deleted INTEGER,
                                            Timestamp INTEGER)""")
            logger.info('LocalPhotos table created')

            self.con.execute("CREATE INDEX idx_lp1 ON LocalPhotos(Signature, DateFlat, ShortName)")
            self.con.execute("CREATE INDEX idx_lp2 ON LocalPhotos(Signature)")
            self.con.execute("CREATE INDEX idx_lp3 ON LocalPhotos(DateFlat)")
            self.con.execute("CREATE INDEX idx_lp4 ON LocalPhotos(ShortName)")
            self.con.execute("CREATE INDEX idx_lp5 ON LocalPhotos(Directory)")
            self.con.execute("CREATE INDEX idx_lp6 ON LocalPhotos(Directory, FileName)")
            self.con.execute("CREATE INDEX idx_lp7 ON LocalPhotos(FlickrId, FlickrSecret)")
            logger.debug('index created')

    def create_local_photos_view(self):
        with self.con:
            self.con.execute("""CREATE """)
            logger.info('view created')

    def __create_search_table(self):
        with self.con:
            self.con.execute("""CREATE TEMPORARY TABLE Search(
                                        Directory TEXT,
                                        FileName TEXT)""")
            logger.debug('table created')

            self.con.execute("CREATE INDEX idx_s1 ON Search(Directory, FileName)")
            logger.debug('index created')

    def insert_flickr_photosets(self, photosets):
        assert photosets, "no photosets to insert"
        logger.debug('photosets.count<%d>' % len(photosets))

        sqlstring = ("""INSERT INTO FlickrPhotosets(
                            Id, Title, Description, DateCreate, DateUpdate)
                        VALUES(
                            :id, :title, :description, :datecreate, :dateupdate)""")

        with self.con:
            cur = self.con.executemany(sqlstring, photosets)
            logger.debug("Number of rows inserted: %d" % cur.rowcount)

    def insert_flickr_photos(self, photos):
        assert photos, "no photos to insert"
        logger.debug('photos.count<%d>' % len(photos))

        sqlstring = ("""INSERT OR REPLACE INTO FlickrPhotos(
                            Id, Title, OriginalFormat, DateUpload,
                            DateTaken, DateTakenUnknown, DateTakenGranularity,
                            Url_o, OriginalSecret, Farm, Server,
                            Tags, Machine_Tags, ShortName, DateFlat, Signature)
                        VALUES(
                            :id, :title, :originalformat, :dateupload,
                            :datetaken, :datetakenunknown, :datetakengranularity,
                            :url_o, :originalsecret, :farm, :server,
                            :tags, :machine_tags, :shortname, :dateflat, :signature)""")

        with self.con:
            cur = self.con.executemany(sqlstring, photos)
            logger.debug("Number of rows inserted: %d" % cur.rowcount)

    def insert_local_photos(self, photos):
        assert photos, "no photos to insert"
        logger.debug('photos.count<%d>' % len(photos))

        sqlstring = ("""INSERT INTO LocalPhotos(
                            Directory, FileName, DateTimeOriginal,
                            FlickrId, FlickrSecret, FlickrTitle, FlickrExtension,
                            Signature, ImageError, DateFlat, ShortName, Timestamp)
                        VALUES(
                            :directory, :filename, :datetimeoriginal,
                            :flickrid, :flickrsecret, :flickrtitle, :flickrextension,
                            :signature, :imageerror, :dateflat, :shortname, %d)""" % time.time())

        with self.con:
            cur = self.con.executemany(sqlstring, photos)
            logger.debug("Number of rows inserted: %d" % cur.rowcount)

    def __insert_search_files(self, records):
        assert records, "no records to insert"
        logger.debug('records.count<%d>' % len(records))

        sqlstring = ("""INSERT INTO Search(
                            Directory, FileName)
                       VALUES(
                           :directory, :filename)""")

        with self.con:
            cur = self.con.executemany(sqlstring, records)
            logger.debug("Number of rows inserted: %d" % cur.rowcount)

    def get_directories_from_local(self):
        sqlstring = ("""SELECT DISTINCT(Directory)
                        FROM LocalPhotos
                        WHERE Deleted IS NULL
                        AND ImageError IS NULL
                        AND Signature IS NOT NULL
                        ORDER BY Directory""")

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return [row['directory'] for row in rows]

    def get_photoset_id(self, photosetname) :
        assert photosetname, "photosetname not supplied"

        sqlstring = ("""SELECT MAX(psr.Id) AS Id
                        FROM FlickrPhotosets psr
                        WHERE psr.Title = :photosetname""")
        with self.con:
            cur = self.con.execute(sqlstring, {'photosetname': photosetname})
            row = cur.fetchone()

            logger.debug("Id<%s>" % row['id'])

        return row['id']

    def select_flickr_photos_matching_local_by_directory(self, directory):
        assert directory, "directory not supplied"

        sqlstring = ("""SELECT pr.Id
                        FROM FlickrPhotos pr
                            ,LocalPhotos pl
                        WHERE (
                                   pr.Signature = pl.Signature
                                OR (
                                       pr.ShortName = pl.ShortName
                                   AND pr.DateFlat = pl.DateFlat
                                   AND pr.DateTakenUnknown = 0)
                                OR (
                                        pr.Id = pl.FlickrId
                                    AND pr.OriginalSecret = pl.FlickrSecret
                                )
                            )
                        AND pl.Deleted IS NULL
                        AND pl.ImageError IS NULL
                        AND pl.Directory = :directory""")

        with self.con:
            cur = self.con.execute(sqlstring, {'directory': directory})
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_photos_for_upload(self):
        sqlstring = ("""SELECT *
                        FROM LocalPhotos l
                        WHERE l.Signature IS NOT NULL
                        AND l.Deleted IS NULL
                        AND l.Signature NOT IN(
                            SELECT Signature
                            FROM LocalPhotos pl
                            WHERE EXISTS(
                                SELECT 1
                                FROM FlickrPhotos pr
                                WHERE pr.Signature = pl.Signature
                                UNION
                                SELECT 1
                                FROM FlickrPhotos pr
                                WHERE pr.Id = pl.FlickrId
                                AND pr.OriginalSecret = pl.FlickrSecret
                                UNION
                                SELECT 1
                                FROM FlickrPhotos pr
                                WHERE pr.ShortName = pl.ShortName
                                AND pr.DateFlat = pl.DateFlat
                                AND pr.DateTakenUnknown = 0
                            )
                        )
                        GROUP BY l.Signature
                        HAVING MIN(IFNULL(l.DateFlat, 99999999999999))""")

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_all_flickr_photos_matching_tag(self, tagstring):
        assert tagstring, 'tagstring not supplied'
        sqlstring = ("""SELECT *
                        FROM FlickrPhotos
                        WHERE Tags LIKE '%{tagstring}%'""".format(tagstring=tagstring))

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_missing_flickr_photos(self):
        sqlstring = ("""SELECT *
                        FROM FlickrPhotos pr
                        WHERE NOT EXISTS(
                            SELECT 1
                            FROM LocalPhotos pl
                            WHERE Signature IS NOT NULL
                            AND Deleted IS NULL
                            AND pl.Signature = pr.Signature
                        )
                        AND NOT EXISTS(
                            SELECT 1
                            FROM LocalPhotos pl
                            WHERE Signature IS NOT NULL
                            AND Deleted IS NULL
                            AND pl.FlickrId = pr.Id
                            AND pl.FlickrSecret = pr.OriginalSecret
                        )
                        AND NOT EXISTS(
                            SELECT 1
                            FROM LocalPhotos pl
                            WHERE Signature IS NOT NULL
                            AND Deleted IS NULL
                            AND pl.DateFlat = pr.DateFlat
                            AND pl.ShortName = pr.ShortName
                            AND pr.DateTakenUnknown = 0
                        )""")

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_unmatchable_flickr_photos(self, nodatematch=False):
        sqlstring = ("""SELECT *
                        FROM FlickrPhotos pr
                        WHERE Signature IS NULL
                        AND (    :nodatematch = 1
                            OR NOT EXISTS(
                                SELECT 1
                                FROM LocalPhotos pl
                                WHERE Signature IS NOT NULL
                                AND Deleted IS NULL
                                AND pl.DateFlat = pr.DateFlat
                                AND pl.ShortName = pr.ShortName
                                AND pr.DateTakenUnknown = 0
                            )
                        )
                        AND NOT EXISTS(
                            SELECT 1
                            FROM LocalPhotos pl
                            WHERE Signature IS NOT NULL
                            AND Deleted IS NULL
                            AND pl.FlickrId = pr.Id
                            AND pl.FlickrSecret = pr.OriginalSecret
                        )""")

        with self.con:
            cur = self.con.execute(sqlstring, {'nodatematch': nodatematch})
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_unmatched_photos_with_flickr_id(self):
        sqlstring = ("""SELECT *
                        FROM LocalPhotos pl
                        WHERE Signature IS NOT NULL
                        AND Deleted IS NULL
                        AND pl.FlickrId IS NOT NULL
                        AND pl.FlickrSecret IS NOT NULL
                        AND EXISTS(
                            SELECT 1
                            FROM FlickrPhotos pr
                            WHERE pr.Signature IS NULL
                            AND pr.Id = pl.FlickrId
                            AND pr.OriginalSecret = pl.FlickrSecret
                        )""")

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_all_local_photos(self):
        sqlstring = ("""SELECT *
                        FROM LocalPhotos""")

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of rows found: %d" % len(rows))

        return rows

    def select_min_upload_date_without_signature(self):
        sqlstring = ("""SELECT MIN(DateUpload) AS mindateupload
                        FROM FlickrPhotos
                        WHERE Signature IS NULL""")

        with self.con:
            cur = self.con.execute(sqlstring)
            row = cur.fetchone()

            mindateupload = row["mindateupload"]

        if mindateupload == None:
            mindateupload = 0

        logger.debug("mindateupload<%s>" % mindateupload)
        return mindateupload

    def select_last_upload_date(self):
        sqlstring = ("""SELECT MAX(DateUpload) AS lastdateuploaded
                        FROM FlickrPhotos""")

        with self.con:
            cur = self.con.execute(sqlstring)
            row = cur.fetchone()

            lastdateuploaded = row["lastdateuploaded"]

        if lastdateuploaded == None:
            lastdateuploaded = 0

        logger.debug("lastdateuploaded<%s>" % lastdateuploaded)
        return lastdateuploaded

    def update_deleted_photos(self, deletedfiles):
        assert deletedfiles, "no deletedfiles records supplied"
        logger.debug('deletedfiles.count<%d>' % len(deletedfiles))

        sqlstring = ("""UPDATE LocalPhotos
                        SET Deleted = :deleted
                        WHERE Directory = :directory
                          AND FileName = :filename""")

        with self.con:
            cur = self.con.executemany(sqlstring, deletedfiles)
            logger.debug("Number of rows updated: %d" % cur.rowcount)

    def __create_tables_if_not_exist(self):
        if not self.__table_exist('LocalPhotos'):
            self.create_local_photos_table()

        if not self.__table_exist('FlickrPhotos'):
            self.create_flickr_photos_table()

    def __table_exist(self, tablename):
        assert tablename, "tablename not supplied"
        logger.debug('tablename<%s>' % tablename)

        sqlstring = ("""SELECT COUNT(1) AS result
                        FROM sqlite_master
                        WHERE type='table'
                        AND name=:tablename""")

        with self.con:
            cur = self.con.execute(sqlstring, {'tablename': tablename})
            row = cur.fetchone()

            logger.debug("result<%s>" % row['result'])

        return (row['result'] == 1)

    def __drop_table(self, table):
        assert table, "Table not supplied"

        with self.con:
            self.con.execute("DROP TABLE IF EXISTS %s" % table)

        logger.debug('table<%s> dropped' % table)


    def __select_new_files(self):
        sqlstring = ("""SELECT Directory, Filename
                     FROM Search s
                     WHERE NOT EXISTS(
                                   SELECT 1
                                   FROM LocalPhotos pl
                                   WHERE pl.Directory = s.Directory
                                   AND pl.FileName = s.FileName
                                   AND pl.Deleted IS NULL)""")

        with self.con:
            cur = self.con.execute(sqlstring)
            rows = cur.fetchall()

            logger.debug("Number of new photos found: %d" % len(rows))

        return rows
