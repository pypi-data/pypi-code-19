# coding=utf8
import os
import re
import wave
import subprocess

import numpy as np
from pymongo import MongoClient

class Decoder(object):
    home_path = os.path.expanduser("~")
    lib_path = home_path + '/Music/lib/'
    tmp_path = home_path + '/tmp.wav'

    def __init__(self):
        try:
            print 'start db logger...'
            self.client = MongoClient()
            self.db = self.client.musicfp
            #self.db.raw.drop()
        except:
            print 'mongodb service down!\nto install:[brew install mongodb]\nto start:[brew services start mongodb]'

        self.all_music = [f[:-4] for f in os.listdir(self.lib_path) if f[-4:] == '.mp3'][:10] + ['初音ミク - 千本桜']
        self.initFp()
        
    def initFp(self):
        for n in self.all_music:
            if not self.query(n):
                self.insert(n, self.fingerprint(self.lib_path + n + '.mp3'))

    def insert(self, name, fp):
        self.db.raw.insert_one(
                { 'name':name, 'data':fp }
                )

    def update(self, name, fp):
        self.db.raw.update_one(
                { 'name':name },
                { 'name':name, 'data':fp }, 
                upsert=True)

    def query(self, name):
        d = self.db.raw.find_one({'name': name})
        if d: return d['data']

    def queryAll(self):
        cursor = self.db.raw.find()
        return [(d['name'], d['data']) for d in cursor]

    def fingerprint(self, path):
        try:
            os.remove(self.tmp_path)
        except OSError:
            pass
        
        cmd = ['ffmpeg','-i',path,'-acodec','pcm_u8','-ar','22050',self.tmp_path]
        p = subprocess.Popen(cmd, shell=False)
        p.wait()

        f = wave.open(self.tmp_path, 'rb')
        params = f.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        str_data = f.readframes(nframes)
        wave_data = np.fromstring(str_data, dtype=np.short)
        wave_data.shape = -1, sampwidth
        wave_data = wave_data.T
        f.close()

        return self.fft(wave_data, framerate, nframes)

    def fft(self, wave_data, framerate, nframes, frames=20):
        block = []
        fft_blocks = []
        high_point = []
        blocks_size = framerate / frames  # block_size为每一块的frame数量
        print framerate, blocks_size, frames
        blocks_num = nframes / blocks_size  # 将音频分块的数量
        a = []
        for i in xrange(0, len(wave_data[0]) - blocks_size, blocks_size):
            block.append(wave_data[0][i:i + blocks_size])
            w = (np.fft.fft(wave_data[0][i:i + blocks_size]))
            freqs = np.fft.fftfreq(len(w))
            idx = np.argmax(np.abs(w))
            freq = freqs[idx]
            freq_in_hertz = abs(freq * framerate)
            a += [int(freq_in_hertz)]
            #print(freq_in_hertz)
            
            
            fft_blocks.append(np.abs(w))
            #print fft_blocks[-1], len(fft_blocks[-1])
            #print xxx
            high_point.append([
                #np.argmax(fft_blocks[-1][:40]),
                np.argmax(fft_blocks[-1][11:22]) + 11,
                np.argmax(fft_blocks[-1][22:44]) + 22,
                np.argmax(fft_blocks[-1][44:88]) + 44
                ])
            
        print a
        return high_point

    def similarity(self, fp1, fp2):
        if len(fp1) > len(fp2):
            fp1, fp2 = fp2, fp1
        max_similar = 0
        for i in range(len(fp2) - len(fp1)):
            temp = 0
            for j in range(len(fp1)):
                if fp1[j][0] == fp2[i + j][0]: temp += 1
                if fp1[j][1] == fp2[i + j][1]: temp += 2
                if fp1[j][2] == fp2[i + j][2]: temp += 1
                    #print i, j, list(fp1[j]), fp2[i+j]
            if temp > max_similar:
                max_similar = temp
        return max_similar

    def match(self, path):
        search = self.fingerprint(path)
        #search = search[100:200]
        name, m = 'none', 0
        for n, fp in self.queryAll():
            similar = self.similarity(search, fp)
            print n, similar
            if similar > m: name, m = n, similar
        return name

#path = '/Users/kliner/1.mp3'
path = '/Users/kliner/a.wav'
#path = '/Users/kliner/b.mp3'
d = Decoder()
print len(d.queryAll())
print d.match(path)
#print Decoder().fingerprint(path)
