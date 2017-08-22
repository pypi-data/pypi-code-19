import sys

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QApplication
from mtb.Image import mImage


class ImageViewer(QWidget):

    def __init__(self,img=None):
        QWidget.__init__(self)

        #self.executor = ThreadPoolExecutor(max_workers=8)

        self.img = mImage(img)

        # if img:
        #     if type(img) == str:
        #         self.imgPath = img
        #     else:
        #         self.img = img


    def setImage(self,im):

        self.img.path = im
        print(self.img)


    def paintEvent(self, event):

        #print("Painting")
        # Get the widget current size

        qp = QPainter()
        qp.begin(self)
        self.drawBackground(event.rect(), qp)
        qp.end()

    def drawBackground(self,rect,qp):


        qp.setRenderHint(QPainter.Antialiasing, True)

        if self.img:
            pImg = self.img.qImage.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)

            qp.drawImage(0, 0, pImg)


    # def checkImage(self,image):
    #     print("checking image")
    #     if image:
    #         if type(image) == QImage or type(image) == ImageQt:
    #             return image
    #         elif type(image) == str:
    #             if isfile(image):
    #                 return  QImage(image)
    #             else:
    #                 print("File does not exist")
    #
    #         elif type(image) == Image:
    #             return  ImageQt(image)
    #         else:
    #             print(type(image))
    #             raise TypeError
    #     else:
    #         return None


    def sizeHint(self):
        return QSize(800, 600)

    def resizeEvent(self, event):
        # maintaining aspect ratio.
        if self.img:
            try:
                new_size = QSize(self.img.pil.width, self.img.pil.height)
                new_size.scale(event.size(),Qt.KeepAspectRatio)
                #new_size.scale(event.size(),Qt.KeepAspectRatioByExpanding)
                self.resize(new_size)
            except:
                pass




if __name__ == '__main__':

    app = QApplication(sys.argv)

    # w =  MVideo()

    w = ImageViewer()

    w.setImage("/Volumes/4TB/PROJETS/Code/PyQT/MTB_QT_Widgets/01-Image_Compare/b.jpg")

    # fp = pjoin(assets, "videos/poyz/Poyz_DV_0024.mov")
    # w.lut = pjoin(assets, "lut/F-9420-LOG.cube")
    w.show()
    # w.setVideo(fp)
    sys.exit(app.exec_())
