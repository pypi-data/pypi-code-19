from .parser import Parser
from .models import *
from .config import DBFILE

class Application():
  def __init__(self):
    pass

  @classmethod
  def run(self):
    Application.connect()

    source = ui.get('source')
    parser = Parser(source)
    parser.parse()

    Application.disconnect()

  @classmethod
  def connect(self):
    if ui.get('drop'):
      os.remove(DBFILE)
      open(DBFILE, 'w+')

    tables = [Download, Enclosure, Episode, Podcast]
    db.connect()
    db.create_tables(tables, safe=True)

  @classmethod
  def disconnect(self):
    db.close()

  @classmethod
  def parse_document(self):
    source = ui.get('source')

    document = XMLDocument.from_source(source)
    channel = XMLChannel.from_document(document)
    if not document and channel:
      return

    d_entries = document.data.get('entries')
    if not d_entries:
      return

    for d_index, d_entry in enumerate(d_entries):
      params = {
        'description': d_entry.get('description'),
        'document': document,
        'image': d_entry.get('image').get('href'),
        'index': d_index,
        'published': d_entry.get('published'),
        'title': d_entry.get('title'),
        'href': d_entry.get('id')
      }

      entry = XMLEntry.from_params(params)
      if not entry:
        continue
      
      for link in d_entry.get('links'):
        params = {
          'entry': entry,
          'href': link.get('href'),
          'length': int(link.get('length', 0)),
          'mime': link.get('type'),
          'rel': link.get('rel'),
        }

        enclosure = XMLEnclosure.from_params(params)
        if not enclosure:
          continue

    return document

  @classmethod
  def parse_podcast(self, document):
    channel = XMLChannel.get(XMLChannel.document == document)
    if not channel:
      return

    params = {
      'channel': channel,
      'clear': ui.get('clear', False),
      'image_src': ui.get('image_src'),
      'match': ui.get('match', False),
      'offline': ui.get('offline', False),
      'output': ui.get('output', os.getcwd()),
      'purge': ui.get('purge', False),
      'rename': ui.get('rename', False),
      'subdir': ui.get('subdir', False),
      'tag': ui.get('tag', False),
      'track_src': ui.get('track_src'),
    }

    podcast = Podcast.from_params(params)
    return podcast

  @classmethod
  def parse_episodes(self, document, podcast):
    limit = ui.get('limit')
    offset = ui.get('offset')
    order = ui.get('order')

    entries = document.entries.where(XMLEntry.downloaded == False, XMLEntry.matched == False)
    entries = XMLEntry.scope(query=entries, order=order, offset=offset, limit=limit)

    for entry in entries:
      episode, added = Episode.get_or_create(entry=entry)
      if not episode:
        logger.warning('Episode creation failed.')
        continue

      audio = episode.create_audio()
      if not audio:
        logger.warning('Audio creation failed.')
        continue

      if not podcast.tag:
        continue

      if podcast.clear:
        audio.clear()

      channel = XMLChannel.get(XMLChannel.document == document)
      tags = {
        'album': ui.get('album', f'{channel.title} ({entry.year})'),
        'albumartist': ui.get('albumartist', channel.title),
        'artist': ui.get('artist', channel.title),
        'comment': ui.get('comment', entry.comment),
        'composer': ui.get('composer', channel.title),
        'date': entry.date,
        'genre': ui.get('genre', 'Podcast'),
        'object': episode.audio,
        'title': entry.title,
      }

      Tags.create(**tags)
      episode.audio.write_tags()

    return True