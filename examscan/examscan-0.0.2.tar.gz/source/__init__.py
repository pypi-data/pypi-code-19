
''' Examscan is a program for adding tags to a pdf.
It can then analyse scans of these exams to extract scoring information.

Get started by running:
	> python -m examscan.tag [options]
or analyse some completed exams by using:
	> python -m examscan.scan [options] '''

from examscan.version import __version__

import examscan.tag
import examscan.scan
