from .config import DBFILE
from bs4 import BeautifulSoup
from clint.textui import progress
from dateutil.parser import parse as parsedate
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TALB, TPE2, TPE1, COMM, TCOM, TPOS, TCON, APIC, TIT2, TRCK, TDRC
from peewee import *
from PIL import Image
from pprint import pprint as pp
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from slugify import slugify, SLUG_OK
import collections
import datetime
import feedparser
import imghdr
import io
import mimetypes
import os
import pprint
import requests
import shutil
mimetypes.init()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
db = SqliteDatabase(DBFILE)
SUPPORTED_FORMATS = ['mp3']

class Base(Model):
  class Meta:
    database = db

class Release(Model):
  class Meta:
    database = db

  title = TextField()
  image_path = TextField(default='')
  published = TextField(default='')

  @property
  def date(self):
    if not self.published:
      return
    return str(parsedate(self.published).date())

  @property
  def year(self):
    if not self.published:
      return
    return str(parsedate(self.published).year)

class Audio():
  def __init__(self, path):
    self.path = path

  def formatted(self):
    preview = ui.get('preview')

    if self.path.endswith('mp3'):
      if preview:
        return MP3(self.path)

      try:
        ID3(self.path)
        return MP3(self.path)
      except:
        logger.error('Invalid MP3 file.')
        return
    return

class MP3(Audio):
  def __init__(self, path):
    self.path = path
    self.preview = ui.get('preview')
    if not self.preview:
      self.audio = ID3(self.path)

  @property
  def fields(self):
    yield 'album', 'TALB'
    yield 'albumartist', 'TPE2'
    yield 'artist', 'TPE1'
    yield 'comment', 'COMM'
    yield 'composer', 'TCOM'
    yield 'date', 'TDRC'
    yield 'genre', 'TCON'
    yield 'title', 'TIT2'
    yield 'track', 'TRCK'

  def query(self, tag):
    try:
      return EasyID3(self.path).get(tag)[0]
    except:
      return {}

  def clear(self):
    fields = dict(self.fields)
    for name, field in fields.items():
      self.audio.delall(field)

  def write_tags(self, tags):
    clear = ui.get('clear')

    if self.preview:
      logger.info('Tags:')
      tags = pprint.pformat(tags, indent=2, width=80, depth=None)
      logger.info(tags)
      return

    if clear:
      self.clear()

    fields = dict(self.fields)
    for name, field in fields.items():
      setter = eval(field)
      value = tags[name]
      self.audio.add(setter(encoding=3, text=f'{value}'))
    
    image = tags.get('image')
    if image:
      self.write_image(image)

    self.audio.save()

  def write_image(self, image):
    try:
      img_bytes = io.BytesIO()
      Image.open(image, mode='r').save(img_bytes, format=imghdr.what(image))

      self.audio.delall('APIC')
      self.audio.add(
        APIC(
          encoding=3,
          mime=mimetypes.guess_type(image)[0],
          type=3,
          desc='Cover',
          data=img_bytes.getvalue()
        )
      )
    except:
      pass

class Download(Base):
  basename = TextField(default='')
  output = TextField()
  extension = TextField(default='')
  size = IntegerField(default=0)
  url = TextField()
  logname = TextField(default='')
  validated = BooleanField(default=False)

  @property
  def fullname(self):
    return f'{self.basename}.{self.extension}'

  @property
  def exists(self):
    if not os.path.isfile(self.output):
      return
    return self.output

  def parse(self):
    if "?" in self.url:
      self.url = self.url.split("?")[0]
    if not self.basename:
      self.basename = self.url.split('/')[-1].split('.')[0]
    self.extension = self.url.split('.')[-1]
    self.save()
    self.output = os.path.join(self.output, self.fullname)
    self.save()
    return True

  def validate(self):
    try:
      requests.head(self.url)
      return True
    except:
      return

  def grab(self):
    preview = ui.get('preview')

    self.parse()

    if self.exists:
      logger.debug('Download exists.')
      return self.output

    if not self.validate():
      logger.debug('Download invalid.')
      return

    logger.info(f'In: {self.url}')
    logger.info(f'Out: {self.output}')
    logger.info('')

    if preview:
      return self.output
    
    request = requests.get(self.url, stream=True, verify=False)
    content_length = int(request.headers.get('content-length'))
    with open(self.output, 'wb') as file:
      for chunk in progress.bar(request.iter_content(chunk_size=1024), expected_size=(content_length/1024) + 1): 
        if chunk:
          file.write(chunk)
          file.flush()

    if os.path.isfile(self.output):
      return self.output

class Podcast(Release):
  output = TextField(default='')

  def set_output(self):
    output = ui.get('output', os.getcwd())
    subdir = ui.get('subdir')
    purge = ui.get('purge')

    if subdir:
      output = os.path.join(output, slugify(self.title))

    if purge:
      shutil.rmtree(output)

    if not os.path.isdir(output):
      try:
        os.makedirs(output)
        return output
      except OSError as e:
        logger.error(e)
        return

    self.output = output
    self.save()
    return output

  def set_image(self, feed):
    tag = ui.get('tag')

    if not tag:
      return ''

    try:
      cover = feed.get('image').get('href')
      download, added = Download.get_or_create(url=cover, basename='cover', output=self.output)

      if download.grab():
        return download.output
      else:
        return ''
    except AttributeError:
      logger.warning('Podcast image not found.')
      return ''

  def parse(self, feed):
    if not self.set_output():
      return

    self.image_path = self.set_image(feed)
    self.published = feed.get('published', '')
    self.save()
    return True

class Episode(Release):
  podcast = ForeignKeyField(Podcast, related_name='episodes')
  index = IntegerField()
  description = TextField(default='')

  def set_image(self, entry):
    image_src = ui.get('image_src')
    rename = ui.get('rename')

    if not image_src == 'episode':
      return self.podcast.image_path

    try:
      cover = entry.get('image').get('href')

      basename = self.renamed if rename else ''
      download, added = Download.get_or_create(url=cover, basename=basename, output=self.podcast.output)
      if download.grab():
        return download.output
    except AttributeError:
      logger.warning('Episode image not found.')
      return self.podcast.image_path or ''

  def parse(self, entry):
    self.published = entry.get('published', '')
    self.save()
    self.image_path = self.set_image(entry) or ''
    self.description = entry.get('description', '')
    self.save()
    return True

  @property
  def comment(self):
    if self.description:
      comment = self.description.replace('\xa0', '')
      comment = BeautifulSoup(comment, "html.parser").get_text()
      return comment

  @property
  def renamed(self):
    name = []
    if self.date:
      name.append(self.date)
    name.append(slugify(self.podcast.title))
    name.append(slugify(self.title))
    name = list(filter(None, name))
    name = ' - '.join(name)
    return name

  @property
  def release(self):
    start = 0
    title = self.title

    if '#' in self.title:
      pound = title.index('#')
      title = title[pound+1:]

    numbers = []
    for index, char in enumerate(title):
      try:
        number = int(char)
        numbers.append(char)
      except:
        consecutive = ''.join(numbers)

        if not char == '.':
          return consecutive

        tenths = title[index + 1]
        return str( float( f'{consecutive}.{tenths}' ) )

class Enclosure(Base):
  episode = ForeignKeyField(Episode, related_name='enclosures')
  href = TextField(default='')
  length = IntegerField(default=0)
  mime = TextField(default='')
  priority = IntegerField(default=99)
  rel = TextField(default='')

  def tag(self, audio):
    image_src = ui.get('image_src')
    track_src = ui.get('track_src')

    podcast = self.episode.podcast

    if track_src == 'release':
      track = self.episode.release
    else:
      track = self.episode.index

    if image_src == 'episode' and self.episode.image_path:
      image = self.episode.image_path
    else:
      image = podcast.image_path
    
    tags = {
      'album': ui.get('album', f'{podcast.title} ({self.episode.year})'),
      'albumartist': ui.get('albumartist', podcast.title),
      'artist': ui.get('artist', podcast.title),
      'comment': ui.get('comment', self.episode.comment),
      'composer': ui.get('composer', podcast.title),
      'date': self.episode.date,
      'genre': ui.get('genre', 'Podcast'),
      'title': self.episode.title,
      'track': track,
      'image': ui.get('image', image)
    }
    audio.write_tags(tags)

  def match(self):
    rename = ui.get('rename')
    episode = self.episode
    podcast = self.episode.podcast

    match = None
    for root, dirs, files in os.walk(podcast.output):
      for file in files:
        path = os.path.join(podcast.output, file)
        audio = Audio(path).formatted()

        if not audio:
          continue

        logger.info(f'Matching episode "{episode.title}" against: "{file}"')

        if self.length == os.path.getsize(file):
          logger.info('Match found by size.')
          match = audio
          break
        
        if episode.title == audio.tag_query('title'):
          logger.info('Match found by title.')
          match = audio
          break

        if episode.date == audio.tag_query('date'):
          logger.info('Match found by date.')
          match = audio
          break

    if not match:
      logger.warning('No match found.')
      return False

    logger.info('In: {match.path}')
    if rename:
      logger.info('Out: {self.episode.renamed}')
    logger.info('')

  def set_download(self):
    rename = ui.get('rename')
    basename = self.episode.renamed if rename else ''
    download, added = Download.get_or_create(url=self.href, basename=basename, output=self.episode.podcast.output)
    return download

  def set_audio(self, path):
    audio = Audio(path).formatted()
    if not audio:
      logger.debug('Invalid audio file.')
      return
    return audio

  def download(self):
    download = self.set_download()
    logger.debug(f'Enclosure download url: {download.url}')
    logger.debug(f'Enclosure download output: {download.output}')
    if download.grab():
      return self.set_audio(download.output)

  def parse(self, link):
    if not any(x in link.get('href') for x in SUPPORTED_FORMATS):
      return

    params = {
      'href': link.get('href'),
      'length': link.get('length'),
      'mime': link.get('type'),
    }

    if self.rel == 'enclosure':
      params['priority'] = 1

    self.update(**params)
    return True