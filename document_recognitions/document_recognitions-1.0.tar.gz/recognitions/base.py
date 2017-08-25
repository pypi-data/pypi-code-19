import logging
import os
import subprocess

import chardet
import magic
from PIL import Image, ImageEnhance, ImageFilter
from wand.image import Image as WandImage


class BaseParser(object):
    def __init__(self, log_data=None):
        self.logger = logging.getLogger(__name__)
        if log_data is None:
            log_data = []
        self.log_data = log_data
        self.converter = Converter()

    def _extract(self, filename, **kwargs):
        """Этот метод должен быть переопределен для каждого типа документа.
        Вытаскивает текст из документа.
        """
        raise NotImplementedError('must be overwritten by child classes')

    def process(self, filename, **kwargs):
        """Этот метод должен быть переопределен для каждого типа документа.
        Запускает процесс распознавание аттрибутов из счета
        """
        raise NotImplementedError('must be overwritten by child classes')

    def _decode(self, text):
        if isinstance(text, str):
            return text
        if not text:
            return ''
        result = chardet.detect(text)
        return text.decode(result['encoding'])


class Converter(object):
    def __init__(self, filename=None, optimized=False):
        self.logger = logging.getLogger(__name__)
        self.filename = filename
        self.temp_filename = None
        if optimized:
            self.content_type = magic.from_file(filename, mime=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.content_type != 'application/pdf':
            os.remove(self.temp_filename)

    def image_enhancement(self, filename, **kwargs):
        """
        Предварительная обработка изображения.
        Включает в себя шаги:
        1) Медианный фильтр
        2) Увеличени уровня контрастности(зависит о шага)
        2) Конвертация картинки в ч/б
        :param filename:
        :param kwargs:
        :return:
        """
        with Image.open(filename) as im:
            temp_file_path = f'{filename.rsplit(".", 1)[0]}__temp.bmp'
            if not kwargs.get('no_enhancement'):
                try:
                    im = im.convert(kwargs.get('convert_mode', 'L'))
                    enhancer = ImageEnhance.Contrast(im)
                    im = enhancer.enhance(kwargs.get('enhance_level', 2))
                    try:
                        im = im.filter(ImageFilter.MedianFilter())
                    except ValueError:
                        im = im.filter(ImageFilter.SHARPEN)
                except OSError as error:
                    self.logger.warning(f'Не удалось обработать файл: {filename}', exc_info=True, extra={
                        'error': error,
                    })
            im.save(temp_file_path, dpi=(400, 400))
        return temp_file_path

    @staticmethod
    def image_optimize_size(filename):
        temp_file_path = f'{filename.rsplit(".", 1)[0]}__optimized.png'
        with Image.open(filename) as im:
            base_width = 600
            width_percent = (base_width / float(im.size[0]))
            height_size = int((float(im.size[1]) * float(width_percent)))
            im = im.resize((base_width, height_size), Image.ANTIALIAS)
            im.save(temp_file_path, dpi=(100, 100))
        return temp_file_path

    @staticmethod
    def pdf_to_image(filename, ext, resolution):
        with WandImage(filename=filename, resolution=resolution) as img:
            tmp_file_path = f'{filename.rsplit(".", 1)[0]}__temp_pdf.{ext}'
            img.save(filename=tmp_file_path)
        return tmp_file_path

    @staticmethod
    def doc_to_pdf(filename):
        outdir_path = filename.rsplit(os.sep, 1)[0]
        subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', filename, '--outdir', outdir_path])
        return f'{filename.rsplit(".", 1)[0]}.pdf'

    def optimize_file_before_s3(self):
        if 'image' in self.content_type:
            self.temp_filename = self.image_optimize_size(self.filename)
        elif self.content_type == 'application/pdf':
            self.temp_filename = self.filename
        else:
            self.temp_filename = self.doc_to_pdf(self.filename)
        return self.temp_filename
