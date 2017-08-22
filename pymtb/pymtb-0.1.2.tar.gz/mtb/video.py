from io import BytesIO
from os.path import basename

import numpy
from PIL import Image
from pymediainfo import MediaInfo
from sh import ffmpeg
from timecode import Timecode


def quoted(string):
    s = "'" + string + "'"
    return s


class Video(object):
    """
    This is the main Video object

    Args:
        file: Path to the video file.
    
    
    Properties:
        .LUT: Path to the LUT file.
        .title: Title extracted from filename
        .width
        .height
        .frame_rate
        
    """
    def __init__(self, file):

        super(Video, self).__init__()

        self.file = file
        self.LUT = None
        self.frame_tc = 0
        self.title = basename(self.file)[:-4]


        # Using mediainfo to return video infos

        media_info = MediaInfo.parse(self.file)


        # NOTE: VIDEO METADATAS
        for t in media_info.tracks:
            if t.track_type == 'Video':

                self.height = t.height
                self.width = t.width

                self.frame_rate = float(t.frame_rate)
                self.tc = Timecode(int(self.frame_rate), "00:00:00:00")
                self.frame_count = int(t.frame_count)
                self.pixelAspect = t.pixel_aspect_ratio
                self.ratio = t.other_display_aspect_ratio[0]

    def done(self,*args):
        """
        Callback once ffmpeg is done reading the frame.
        """
        #print("Frame read.")
        frame = self.out.getvalue()
        frame = numpy.fromstring(frame, dtype='uint8')
        frame.shape = (self.height, self.width, 3)
        self.array = frame
        self.frame = Image.fromarray(frame)

    def FFtoTC(self, ff):
        millis = 1000 / self.frame_rate

        f = []
        f.append(ff[:-4])
        f.append(ff[-3:])
        mtof = float(f[1]) / float(millis)

        tc = f[0] + ":{:02d}".format(int(mtof))
        return tc

    def TCtoFF(self, tc='tc'):
        if tc == 'tc':
            tc = self.tc

        millis = 1000 / self.frame_rate
        millis = int(str(tc)[-2:]) * millis
        #print millis
        return str(tc)[:-3] + ".{:03d}".format(int(millis))

    def removeLUT(self):
        self.LUT = None
        self.filter = None

    def setLUT(self, lut):

        """
        Sets the lut and update the filter accordingly (don't call readframe)
        
        Args:
            lut: Path to the LUT file
        
        """


        if lut.endswith(".cube") == 0:
            print('You need to first convert the LUT to *.cube')
            return
        lut_name = basename(lut)[:-5]
        self.LUT = lut
        self.filters = ["-vf", "lut3d=file=" + quoted(lut)]
        #self.readFrame()

    def readFrame(self,done=None):
        """
        Async command to read frames.
        Returns an object that can block execution using .wait() on it.
        
        Args:
            done: Callback to attach to once the command is done.
            
        """



        self.out = BytesIO()
        tc = self.TCtoFF()
        if done == None:
            done = self.done




        if self.LUT:
            # print("using {} LUT to read the frame at {}".format(basename(self.LUT)[:-5], self.tc))
            return ffmpeg(
                "-ss",
                tc,
                "-i",
                self.file,
                "-frames:v",
                "1",
                "-f",
                "image2pipe",
                '-pix_fmt',
                'rgb24',
                '-vcodec',
                'rawvideo',
                self.filters[0],
                self.filters[1],
                '-',
                _out=self.out,
                _done=done,
                _bg=True)
        else:
            return ffmpeg(
                "-ss",
                tc,
                "-i",
                self.file,
                "-frames:v",
                "1",
                "-f",
                "image2pipe",
                '-pix_fmt',
                'rgb24',
                '-vcodec',
                'rawvideo',
                '-',
                _out=self.out,
                _done=done,
                _bg=True)


class VideoQt(Video):
    def __init__(self, file):
        Video.__init__(self,file)

    def done(self,*args):
        Video.done(self)
        #self.frame.save("a.jpg")
        #self.imageQt = ImageQt(self.frame)

        #self.pixmap = QPixmap.fromImage(self.imageQt)

if __name__ == '__main__':

    fp = '/Volumes/4TB/PROJETS/Code/PyQT/MTB_QT_Widgets/21-MTB_Lib_tests/assets/videos/poyz/Poyz_DV_0024.mov'
    v = VideoQt(fp)
    v.setLUT(
        "/Volumes/4TB/PROJETS/Code/PyQT/MTB_QT_Widgets/21-MTB_Lib_tests/assets/lut/F-9420-LOG.cube"
    )
    a = v.readFrame()

    print(
        "a is using sh Async so you can do stuff while ffmpeg reads the frame")
    print(
        "Add a.wait() when you need to access data outputed from the command.")

    a.wait()
    im = v.frame.show()
