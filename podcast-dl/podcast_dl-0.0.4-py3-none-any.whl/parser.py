from .models import *
import feedparser
from pprint import pprint as pp

class Parser():
  def __init__(self, source):
    self.data = feedparser.parse(source)
    self.feed = self.data.get('feed')
    self.entries = self.data.get('entries')

  def parse(self):
    if not self.validate():
      return
    if not self.parse_podcast():
      return
    if not self.parse_episodes():
      return

    return True

  def validate(self):
    if self.data.bozo:
      raise ParserException('Invalid XML.')
    if not self.feed:
      raise ParserException('XML has no feed.')
    if not self.entries:
      raise ParserException('XML has no entries.')
    if not self.feed.get('title'):
      raise ParserException('Feed has no title.')

    return True

  def parse_podcast(self):
    self.podcast, added = Podcast.get_or_create(title=self.feed.get('title'))
    if not self.podcast.parse(self.feed):
      raise ParserException('Podcast parsing failed.')

    return True

  def parse_episodes(self):
    order = ui.get('order')
    offset = ui.get('offset')
    limit = ui.get('limit')
    match = ui.get('match')
    offline = ui.get('offline')
    tag = ui.get('tag')
    preview = ui.get('preview')

    # Entries
    if order == 'asc':
      self.entries = reversed(self.entries)
    if offset and limit:
      self.entries = self.entries[offset:(limit + offset)]
    elif offset:
      self.entries = self.entries[offset:]
    elif limit:
      self.entries = self.entries[:limit]

    if not self.entries:
      scope = pprint.pformat({ 'order': order, 'offset': offset, 'limit': limit })
      raise ParserException(f'Scope returned 0 episodes: {params}')

    logger.info('Parsing episodes.', color='green')
    for index, entry in enumerate(self.entries):
      index += 1
      title = entry.get('title')
      if not title:
        logger.warning('Skipping episode with no title.')
        continue

      # Episode
      logger.info(entry.title, color='cyan')
      episode, added = Episode.get_or_create(title=entry.get('title'), index=index, podcast=self.podcast)
      if not episode.parse(entry):
        logger.warning('Episode entry parse failed.')
        continue

      # Links
      try:
        links = list(entry.get('links'))
      except TypeError:
        logger.warning('Episode entry has no links.')
        continue

      # Enclosures
      enclosure_link = None
      for link in links:
        if link.get('rel') == 'enclosure':
          enclosure_link = link

      if enclosure_link:
        logger.debug(f'Parsing {enclosure_link}')
        enclosure, added = Enclosure.get_or_create(episode=episode, href=enclosure_link.get('href'))
        if not enclosure.parse(enclosure_link):
          logger.warning('Parsing failed.')
          enclosure_link = None

      if not enclosure_link:
        for link in links:
          logger.debug(f'Parsing {link}')
          enclosure, added = Enclosure.get_or_create(episode=episode, href=link.get('href'))
          if not enclosure.parse(link):
            logger.warning('Parsing failed.')
            continue

      if not episode.enclosures:
        logger.warning('Episode has no enclosures.')
        continue

      # Match || Download
      audio = None
      for enclosure in episode.enclosures.order_by(Enclosure.priority):
        logger.debug(f'Parsing {enclosure.href}')
        if audio:
          break
        if match:
          audio = enclosure.match()
          if offline and not audio:
            continue

        audio = enclosure.download()
      if not audio:
        logger.warning('All enclosure downloads and/or matches failed.')
        continue

      if audio and tag:
        enclosure.tag(audio)

      if preview:
        logger.info('')

    return True