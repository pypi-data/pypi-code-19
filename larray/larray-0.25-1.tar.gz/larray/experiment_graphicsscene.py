import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics, QPen
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication

app = QApplication(sys.argv)

scene = QGraphicsScene()
font = QFont("Calibri", 11)
font_metrics = QFontMetrics(font)

padding = 2
column_width = font_metrics.width("X") * 8 + padding * 2
row_height = font_metrics.height() + padding * 2
rows = 200
columns = 80

for x in range(columns):
    for y in range(rows):
        item = scene.addSimpleText("%d / %d" % (x, y), font)
        item.setPos(x * column_width + padding, y * row_height + padding)

for x in range(columns):
    line_x = x * column_width
    scene.addLine(line_x, 0, line_x, rows * row_height).setPen(QPen(Qt.gray))

for y in range(rows):
    line_y = y * row_height
    scene.addLine(0, line_y, columns * column_width, line_y).setPen(QPen(Qt.gray))

view = QGraphicsView(scene)
view.resize(700, 700)
view.show()

sys.exit(app.exec_())
