from collections import defaultdict
from io import BytesIO
from os.path import basename

import numpy
from PIL import Image
from pymediainfo import MediaInfo
from sh import ffmpeg
from timecode import Timecode
from mtb.database import LUT_LIB, cherbourg

def quoted(string):
    s = "'" + str(string) + "'"
    return s


__all__ = ["Video","VideoQt"]

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
    def __init__(self, file = None):

        super(Video, self).__init__()

        self.title = None
        self.file = file
        self.LUT = None
        self.frame = None
        self.cache = defaultdict()
        self.cached_frame = None


    def __str__(self):

        return "MTB-VIDEO-OBJECT\ntitle: {}\nsize: {}x{}\nframerate: {}FPS\ntotal frameCount: {}\npixel aspect ratio: {}\nratio: {}\ncurrent_tc: {}".format(
        self.title,
        self.width,
        self.height,
        self.frame_rate,
        self.frame_count,
        self.pixelAspect,
        self.ratio,
        self.tc,)
        return


    ############################################################################################################
    @property
    def cached_frame(self):
        try:
            c = self.cache[self.title][self.lut_name][str(self.tc.frames)]["image"]
            if c:
                print("C is equal to : {}".format(c))
                return c
            return False

        except:
            return False

    @cached_frame.setter
    def cached_frame(self,frame):
        if frame:

            #self.cache[self.title][self.lut_name] = {}
            self.cache[self.title][self.lut_name][str(self.tc.frames)] = {
                "image" : frame
            }
            #print("I'm {}".format(self.title))
            #pprint(self.cache,width=3)

    # @property
    # def cache(self):
    #     return self._cache
    #
    # @cache.setter
    # def cache(self,c):
    #     self._cache = c




    @property
    def file(self):
        return self._file

    @file.setter
    def file(self,filepath):

        if filepath:
            filepath = str(filepath)
            self.title = basename(filepath)[:-4]
            self._file = filepath
            self.parse()

            self.cache[self.title] = {}
            self.cache[self.title][self.lut_name] = {}
            self.cache[self.title][self.lut_name][str(self.tc.frames)] = {}


    @property
    def fftc(self):
        return self.TCtoFF()

    @fftc.setter
    def fftc(self,fftctimecode):
        self.tc = self.FFtoTC(fftctimecode)

    @property
    def tc(self):
        return self._tc

    @tc.setter
    def tc(self,timecode):
        #print("running setter for TC")
        if type(timecode) == str:
            #print("TC is String")
            if type(self._tc) == Timecode:
                self._tc.set_timecode(timecode)
        if type(timecode) == Timecode:
            #print("TC is a Timecode")
            self._tc = timecode
        if type(timecode) == int:
            if timecode >=1:
                t = [self._tc.frames_to_tc(timecode)]
                new_tc = ""
                for h, m, s, f in t:
                    new_tc = "{0:02d}:{1:02d}:{2:02d}:{3:02d}".format(h, m, s, f)
                self._tc = Timecode(new_tc)
        try:
            if self.cache[self.title][self.lut_name][str(self._tc.frames)]:
                pass
            else:
                self.cache[self.title][self.lut_name][str(self._tc.frames)] = {}
        except:
            pass
    @property
    def LUT(self):
        return self._LUT

    @LUT.setter
    def LUT(self,lutpath):
        try:
            if lutpath == self._LUT:
                return
        except:
            pass
        if lutpath == None:
            self._LUT = "Original"
            self.filters = None
            return

        lutpath = str(lutpath)
        #self.filters = ["-vf", "lut3d=file=" + quoted(lutpath)]
        self.filters = ["-vf", "lut3d=" + quoted(lutpath)]

        try:
            if type(self.cache[self.title][basename(lutpath)[:-5]][str(self.tc.frames)] == dict):
                pass

        except:
            self.cache[self.title][basename(lutpath)[:-5]] = {}


        self._LUT = lutpath


    @LUT.deleter
    def LUT(self):
        self._LUT = None
        self.filters = None

    @property
    def lut_name(self):
        if self.LUT == None or self.LUT == "Original":
            return "Original"
        else:
            return basename(self.LUT)[:-5]
    ############################################################################################################
    def parse(self):
        # Using mediainfo to return video infos

        media_info = MediaInfo.parse(self.file)

        # NOTE: VIDEO METADATAS
        for t in media_info.tracks:
            if t.track_type == 'Video':

                self.height = t.height
                self.width = t.width

                self.frame_rate = float(t.frame_rate)

                self.frame_count = int(t.frame_count)
                self.pixelAspect = t.pixel_aspect_ratio
                self.ratio = t.other_display_aspect_ratio[0]

        self.tc = Timecode(int(self.frame_rate), "00:00:00:00")

    def flush(self):

        self.frame = None
        self.LUT = None

    def done(self,*args):
        """
        Callback once ffmpeg is done reading the frame.
        """
        #print("Frame read.")
        #frame = self.out.getvalue()
        frame = self.out.getbuffer()

        byteorder = '>'


        # try:
        #     header, width, height, maxval = re.search(
        #         b"(^P5\s(?:\s*#.*[\r\n])*"
        #         b"(\d+)\s(?:\s*#.*[\r\n])*"
        #         b"(\d+)\s(?:\s*#.*[\r\n])*"
        #         b"(\d+)\s(?:\s*#.*[\r\n]\s)*)", frame).groups()
        #
        # except:
        #     print("not pgm")

        #frame = numpy.frombuffer(frame,dtype='u1' if int(maxval) < 256 else byteorder+'u2',)


        #print(frame.dtype)
        frame = numpy.frombuffer(frame, dtype='uint8')

        #print(len(frame))
        #print(type(frame[0]))



        #print(frame[1],frame[2],frame[3])
        frame.shape = (self.height, self.width, 3)
        #self.array = frame
        self.frame = Image.fromarray(frame)
        self.cached_frame = Image.fromarray(frame)



        if self.callback:
            self.callback()

    def FFtoTC(self, ff):
        millis = 1000 / self.frame_rate

        f = []
        f.append(ff[:-4])
        f.append(ff[-3:])
        mtof = float(f[1]) / float(millis)

        tc = f[0] + ":{:02d}".format(int(mtof))
        return tc
    def TCtoFF(self, tc = None):

        if tc == None:
            tc = self.tc

        millis = int(1000 / int(tc.framerate))
        t = str(tc)
        t = t.split(":")
        h, m, s, f = t
        f = int(f)
        return "{}:{}:{}.{}".format(h.zfill(2), m.zfill(2), s.zfill(2), str(millis * f).zfill(3))

    def add_frames(self,frames):

        if self.tc.frames >= 1:
            self.tc.add_frames(frames)
        else:
            self.tc = 1
    def readFrame(self,adddone=None):
        """
        Async command to read frames.
        Returns an object that can block execution using .wait() on it.
        
        Args:
            done: Callback to attach to once the command is done.
            
        """
        if not self.cached_frame:
            self.out = BytesIO()


            tc = self.fftc


            if adddone == None:

                self.callback = None

            else:
                self.callback = adddone

            #print(self.LUT)
            if self.LUT == "Original":
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
                    '-',
                    _out=self.out,
                    _bg=True,
                    _done=self.done)

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
                    self.filters[0],
                    self.filters[1],
                    '-',
                    _out=self.out,
                    _bg=True,
                    _done=self.done)
        else:

            return self.cached_frame


class VideoQt(Video):
    def __init__(self, file):
        Video.__init__(self,file)

    def done(self,*args):
        Video.done(self)
        #self.frame.save("a.jpg")
        #self.imageQt = ImageQt(self.frame)

        #self.pixmap = QPixmap.fromImage(self.imageQt)

if __name__ == '__main__':

    fp = cherbourg()[15]
    print(fp)
    #v = VideoQt(fp)
    v = Video(None)
    v.file = fp
    v.LUT = LUT_LIB()[5]
    print(LUT_LIB()[5])
    a = v.readFrame()

    print(
        "a is using sh Async so you can do stuff while ffmpeg reads the frame")
    print(
        "Add a.wait() when you need to access data outputed from the command.")

    a.wait()
    im = v.frame.show()
