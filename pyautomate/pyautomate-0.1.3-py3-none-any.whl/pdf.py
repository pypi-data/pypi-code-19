import io
from pdfminer import high_level as pdf
from . import office


def clean_string(src):
    """Removes control characters"""
    return src.translate(dict.fromkeys(range(32)))


class PDFDocument:
    def __init__(self, filepath):
        self.filepath = filepath

    def extract_text(self, output_file=None, **options):
        """extract text from the pdf file.

        Keyword arguments:
        output_file -- file path to save the content of the pdf file.
        Default is None. If None, returns the content as string.
        If filepath ends with .docx, the content is saved as Word format.
        Else, saved as text file.
        """
        output = io.StringIO()

        in_file = open(self.filepath, 'rb')
        pdf.extract_text_to_fp(in_file, output)

        content = clean_string(output.getvalue())
        output.close()

        if not output_file:
            return content

        elif output_file.endswith('.docx'):
            word_doc = office.Word()
            word_doc.add_paragraph(content)
            word_doc.save(output_file)

        else:
            encoding = options.get('encoding', 'utf-8')
            with open(output_file, 'w', encoding=encoding) as fout:
                fout.write(content)
