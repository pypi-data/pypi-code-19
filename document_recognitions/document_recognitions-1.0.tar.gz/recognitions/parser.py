import os
import subprocess

import PyPDF2

from recognitions import tesseract
from recognitions.base import BaseParser


class ImageParser(BaseParser):
    SUPPORTED_LANG = 'rus'

    def _start_tesseract(self, prepared_image, **kwargs):
        return tesseract.image_to_string(
            image_path=prepared_image, lang=self.SUPPORTED_LANG, config=kwargs.get('options', '')
        )

    def _extract(self, filename, step=0, **kwargs):
        if step == 0:
            prepared_image = self.converter.image_enhancement(filename, no_enhancement=True)
            text = self._start_tesseract(prepared_image=prepared_image)
        elif step == 1:
            prepared_image = self.converter.image_enhancement(filename, enhance_level=3)
            text = self._start_tesseract(prepared_image=prepared_image)
        elif step == 2:
            prepared_image = self.converter.image_enhancement(filename, enhance_level=1)
            text = self._start_tesseract(prepared_image=prepared_image, options='--oem0 -psm 11')
        else:
            prepared_image = self.converter.image_enhancement(filename, enhance_level=1)
            text = self._start_tesseract(prepared_image=prepared_image, options='--oem0 -psm 12')
        os.remove(prepared_image)
        return self._decode('\n'.join([element.strip() for element in text.split('\n') if element.strip()]))

    def process(self, filename, **kwargs):
        return self._extract(filename, **kwargs)


class PDFParser(BaseParser):
    MAX_STEPS_COUNT = 2

    def _text_from_pdf(self, *args):
        return subprocess.check_output(*args).decode('utf-8')

    def _get_num_pages(self, filename):
        num_pages = 1
        with open(filename, 'rb') as pdf_file_obj:
            try:
                pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
                num_pages = pdf_reader.getNumPages()
            except PyPDF2.utils.PdfReadError as error:
                pass
        return num_pages

    def _pdf_to_image(self, filename):
        num_pages = self._get_num_pages(filename=filename)
        tmp_file_path = self.converter.pdf_to_image(filename=filename, ext='png', resolution=600)
        if num_pages > 1:
            for page_number in range(num_pages):
                name, ext = tmp_file_path.rsplit('.', 1)
                yield '.'.join([f'{name}-{page_number}', ext])
        else:
            yield tmp_file_path

    def _extract(self, filename, step=0, **kwargs):
        text = ''
        if step == 0:
            text = self._text_from_pdf(['pdftotext', '-raw', filename, '-'])
        elif step == 1:
            text = self._text_from_pdf(['pdftotext', filename, '-'])
        elif step == 2:
            with open(filename, 'rb') as pdf_file_obj:
                pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
                try:
                    text = '\n'.join(
                        [pdf_reader.getPage(page).extractText() for page in range(pdf_reader.getNumPages())]
                    )
                except PyPDF2.utils.PdfReadError as error:
                    pass
        return text

    def process(self, filename, **kwargs):
        return self._extract(filename)


class DocParser(PDFParser):
    def _pdf_to_image(self, filename):
        return super(DocParser, self)._pdf_to_image(filename=self.converter.doc_to_pdf(filename))

    def _extract(self, filename, step=0, **kwargs):
        return super(DocParser, self)._extract(self.converter.doc_to_pdf(filename), step, **kwargs)
