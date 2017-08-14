import os
from timer import Timer
from hash import Hash
import tempfile
from matplotlib.pyplot import gcf, savefig


class Thumbnail(object):
    SIZE_PIXELS = 256

    @staticmethod
    def save_matplotlib_thumbnail(filename):
        fig = gcf()
        fig_size = fig.get_size_inches()
        Thumbnail.__resize_save_and_restore_matplotlib_thumbnail(filename,
                                                                 fig, fig_size)

    @staticmethod
    def __resize_save_and_restore_matplotlib_thumbnail(filename,
                                                       fig, fig_size):
        try:
            scale = Thumbnail.SIZE_PIXELS / (max(fig_size) * fig.dpi)
            fig.set_size_inches(scale * fig_size[0],
                                scale * fig_size[1])
            savefig(filename)
        finally:
            fig.set_size_inches(fig_size[0], fig_size[1])


class Figures(object):
    FIGURE_FORMAT = 'png'

    @staticmethod
    def add_output_figure(thumbnail_dir):
        with Timer() as timer:
            fighash = Figures.__current_figure_hash()
            Figures.__store_figure_thumbnail(thumbnail_dir, fighash)
        return {'hash': fighash, 'timing': timer.duration_ms()}

    @staticmethod
    def __current_figure_raw_png_data():
        try:
            tmp, temp_filename = tempfile.mkstemp(suffix='.png')
            os.close(tmp)  # os may prohibit saving to an already open file
            savefig(temp_filename)
            with open(temp_filename) as f:
                file_data = f.read()
        finally:
            os.remove(temp_filename)
        return file_data

    @staticmethod
    def __current_figure_hash():
        return Hash.hash(Figures.__current_figure_raw_png_data())

    @staticmethod
    def __save_current_figure_thumbnail(thumbnail_dir, filename):
        Thumbnail.save_matplotlib_thumbnail('%s/%s.%s' % (thumbnail_dir,
                                            filename, Figures.FIGURE_FORMAT))

    @staticmethod
    def __store_figure_thumbnail(thumbnail_dir, filename):
        if not os.path.exists(thumbnail_dir):
            os.makedirs(thumbnail_dir)
        Figures.__save_current_figure_thumbnail(thumbnail_dir, filename)
