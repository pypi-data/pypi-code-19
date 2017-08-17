
''' Examscan is a program for adding tags to a pdf.
It can then analyse scans of these exams to extract scoring information.

Get started by running:
	> python -m examscanuiuc.tag [options]
or analyse some completed exams by using:
	> python -m examscanuiuc.scan [options] '''

from examscanuiuc.version import __version__

import examscanuiuc.tag
import examscanuiuc.scan
