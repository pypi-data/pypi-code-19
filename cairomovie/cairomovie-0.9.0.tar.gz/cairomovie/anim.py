# -*- coding: utf-8 -*-
"""Makes animations from cairo frames, based on moviepy."""

import collections
import os.path
import argparse
import math

import moviepy.editor as mpy
import numpy as np
import abc
try:
    import cairo
except ImportError:
    import cairocffi as cairo

FILENAME_SEPARATOR = '.'

# -----------------------------------------------------------------------
# Animation Interface
# -----------------------------------------------------------------------

class Animation(metaclass=abc.ABCMeta):
    """Implement a class of this method to perform the animation."""

    @abc.abstractmethod
    def duration(self, config):
        """Return the total duration of the animation."""
        return 0

    @abc.abstractmethod
    def draw_frame(self, c, t, config):
        """Draw one animation frame to the cairo context."""
        return

    # Default implementations

    def get_cairo_frame(self, t, config, img=None):
        """Create a cairo image representing one frame, using draw_frame."""
        if img is None:
            img = cairo.ImageSurface(cairo.FORMAT_RGB24, config.w, config.h)
        else:
            assert img.get_width() == config.w
            assert img.get_height() == config.h
            assert img.get_format() == cairo.FORMAT_RGB24
        c = cairo.Context(img)
        c.save()
        self.draw_frame(c, t, config)
        c.restore()
        return img

# -----------------------------------------------------------------------
# Support classes
# -----------------------------------------------------------------------

class Timing(collections.namedtuple('Timing', ('start','end'))):
    __slots__ = ()

    @classmethod
    def parse(Cls, timing_str):
        if '-' in timing_str:
            start_str, end_str = timing_str.split('-')
            start = 0 if start_str.strip() in ('', '*') else float(start_str)
            end = None if end_str.strip() in ('', '*') else float(end_str)
            return Cls(start, end)
        else:
            time = float(timing_str)
            return Cls(time, time)

    @property
    def explicit(self):
        """Is this an explicit, ratgher than a generic 'all time' range."""
        return self.start > 0 or self.end is not None

    @property
    def duration(self):
        return None if self.end is None else self.end - self.start

    def expand_for_fps(self, fps, anim_duration):
        """Return a new timing, enclosing this one, taking fps into account."""

        # Round down the start-time.
        start_time = self.start
        start_frame = math.floor(start_time * fps)
        start_time = start_frame / fps

        # Round up the end-time.
        if self.end is not None:
            end_time = self.end
        else:
            end_time = anim_duration
        end_frame = math.ceil(end_time * fps) + 1
        end_time = end_frame / fps

        return Timing(start_time, end_time)

    def __str__(self):
        if self.start == self.end:
            return "{}".format(self.start)
        else:
            return "{}-{}".format(
                self.start if self.start is not 0 else 'start',
                self.end if self.end is not None else 'end'
                )    

Timing.ALL = Timing(0, None)

_AnimConfig = collections.namedtuple('AnimConfig', ('w', 'h', 'fps', 't'))
class AnimConfig(_AnimConfig):
    __slots__ = ()

    def __new__(Cls, w, h, fps=0, t=None):
        return super(AnimConfig, Cls).__new__(Cls, w, h, fps, t)

# -----------------------------------------------------------------------
# Rendering support
# -----------------------------------------------------------------------

def render_animation(anim, filename, config, verbose=True):
    """Renders the animation to a file."""

    fps = config.fps
    time = config.t if config.t is not None else Timing.ALL

    # Modify filename, if we're using a subset of time.
    if time.explicit:
        name, ext = os.path.splitext(filename)
        filename = '{}{}{}{}'.format(name, FILENAME_SEPARATOR, time, ext) 

    # Include start and end bounds.
    time = time.expand_for_fps(fps, anim.duration(config))

    # Create the animation.
    img = None
    def render_frame(t_from_start):
        nonlocal img
        # Render as cairo img.
        t = t_from_start + time.start
        img = anim.get_cairo_frame(t, config, img)
        # Convert to numpy array.
        im = np.frombuffer(img.get_data(), np.uint8)
        im.shape = (img.get_height(), img.get_width(), 4)
        return im[:,:,[2,1,0]] # RGB order

    clip = mpy.VideoClip(render_frame, duration=time.duration)

    # Save as the correct filetype
    _, ext = os.path.splitext(filename)
    if ext == '.gif':
        clip.write_gif(
            filename,
            fps=fps, opt="OptimizePlus", fuzz=10, verbose=verbose)
    else:
        clip.write_videofile(
            filename,
            fps=fps, verbose=verbose)

def render_one_frame(anim, filename, config, verbose=True):
    """Export one moment in the animation (for testing)."""
    t = config.t
    t = anim.duration(config) if t is None or t.end is None else t.end
    img = anim.get_cairo_frame(t, config)
    img.write_to_png(filename)
    if verbose:
        print(f"Wrote to: {filename}")

def render(anim, filename, config, verbose=True):
    """Renders either a frame or an animation, depending on filename."""
    _, ext = os.path.splitext(filename)
    if ext == '.png':
        render_one_frame(anim, filename, config, verbose)
    else:
        render_animation(anim, filename, config, verbose)

# -----------------------------------------------------------------------
# Command line support.
# -----------------------------------------------------------------------

def add_anim_arguments(
        parser,
        default_filename='out.mp4',
        default_width=1280, default_height=720, default_fps=15
        ):
    """Adds argparse arguments."""
    parser.add_argument(
        '-o', '--out', type=str, default=default_filename, action='store',
        help="the output file (use .png for still frame)")
    parser.add_argument(
        '-x', '--width', type=int, default=default_width, action='store',
        help="the image width")
    parser.add_argument(
        '-y', '--height', type=int, default=default_height, action='store',
        help="the image height")
    parser.add_argument(
        '-f', '--fps', type=float, default=default_fps, action='store',
        help="the fps (for animations)")
    parser.add_argument(
        '-t', '--time', type=Timing.parse, default=None, action='store',
        help="the time or time range to export ('-' for the whole range)")
    parser.add_argument(
        '-q', '--quiet', default=False, action='store_true',
        help="reduces output")

def render_from_args(anim, args):
    """Processes arguments and calls the correct renderer."""
    config = AnimConfig(args.width, args.height, args.fps, args.time)
    if not args.quiet:
        duration = anim.duration(config)
        frames = math.ceil(duration * config.fps) if config.fps > 0 else 1
        print("{:d}x{:d} - {:.2f}s (t={}) @ {}fps = {:d} frames".format(
            config.w, config.h, duration, config.t, config.fps, frames
            ))        
    render(anim, args.out, config, verbose=not args.quiet)
