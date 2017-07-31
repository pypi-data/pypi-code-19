# coding: utf-8

# Copyright (C) 2017 avideo authors (see AUTHORS)

#
#    This file is part of avideo.
#
#    avideo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    avideo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with avideo.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals


import os
import subprocess

from .ffmpeg import FFmpegPostProcessor

from ..utils import (
    check_executable,
    encodeArgument,
    encodeFilename,
    PostProcessingError,
    prepend_extension,
    shell_quote
)


class EmbedThumbnailPPError(PostProcessingError):
    pass


class EmbedThumbnailPP(FFmpegPostProcessor):
    def __init__(self, downloader=None, already_have_thumbnail=False):
        super(EmbedThumbnailPP, self).__init__(downloader)
        self._already_have_thumbnail = already_have_thumbnail

    def run(self, info):
        filename = info['filepath']
        temp_filename = prepend_extension(filename, 'temp')

        if not info.get('thumbnails'):
            raise EmbedThumbnailPPError('Thumbnail was not found. Nothing to do.')

        thumbnail_filename = info['thumbnails'][-1]['filename']

        if not os.path.exists(encodeFilename(thumbnail_filename)):
            self._downloader.report_warning(
                'Skipping embedding the thumbnail because the file is missing.')
            return [], info

        if info['ext'] == 'mp3':
            options = [
                '-c', 'copy', '-map', '0', '-map', '1',
                '-metadata:s:v', 'title="Album cover"', '-metadata:s:v', 'comment="Cover (Front)"']

            self._downloader.to_screen('[ffmpeg] Adding thumbnail to "%s"' % filename)

            self.run_ffmpeg_multiple_files([filename, thumbnail_filename], temp_filename, options)

            if not self._already_have_thumbnail:
                os.remove(encodeFilename(thumbnail_filename))
            os.remove(encodeFilename(filename))
            os.rename(encodeFilename(temp_filename), encodeFilename(filename))

        elif info['ext'] in ['m4a', 'mp4']:
            if not check_executable('AtomicParsley', ['-v']):
                raise EmbedThumbnailPPError('AtomicParsley was not found. Please install.')

            cmd = [encodeFilename('AtomicParsley', True),
                   encodeFilename(filename, True),
                   encodeArgument('--artwork'),
                   encodeFilename(thumbnail_filename, True),
                   encodeArgument('-o'),
                   encodeFilename(temp_filename, True)]

            self._downloader.to_screen('[atomicparsley] Adding thumbnail to "%s"' % filename)

            if self._downloader.params.get('verbose', False):
                self._downloader.to_screen('[debug] AtomicParsley command line: %s' % shell_quote(cmd))

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()

            if p.returncode != 0:
                msg = stderr.decode('utf-8', 'replace').strip()
                raise EmbedThumbnailPPError(msg)

            if not self._already_have_thumbnail:
                os.remove(encodeFilename(thumbnail_filename))
            # for formats that don't support thumbnails (like 3gp) AtomicParsley
            # won't create to the temporary file
            if b'No changes' in stdout:
                self._downloader.report_warning('The file format doesn\'t support embedding a thumbnail')
            else:
                os.remove(encodeFilename(filename))
                os.rename(encodeFilename(temp_filename), encodeFilename(filename))
        else:
            raise EmbedThumbnailPPError('Only mp3 and m4a/mp4 are supported for thumbnail embedding for now.')

        return [], info
