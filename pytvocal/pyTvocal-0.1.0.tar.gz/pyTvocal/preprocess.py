import os

import h5py
import soundfile
from pydub import AudioSegment

from calcLPCC import calcLPCC


def wavread(filename):
    x, fs = soundfile.read(filename)
    return x, fs


def wavwrite(filename, y, fs):
    soundfile.write(filename, y, fs)
    return 0


def format_2_wav(audioPath='audio.ogg'):
    song = AudioSegment.from_file(audioPath, audioPath[-3:])
    song = song.set_channels(1)
    song.export(audioPath.replace(audioPath[-3:], 'wav'), 'wav')
    return 0


def batch_format_2_wav(audioDir='dataset/'):
    for root, dirs, names in os.walk(audioDir):
        for name in names:
            audioPath = os.path.join(root, name)
            if '.ogg' in audioPath or '.mp3' in audioPath:
                format_2_wav(audioPath)
                print audioPath, '.........'

    return 0


def extract_lpcc_feat(audioPath):
    songXlpcc = []
    songYlabel = []
    audioData, fs = wavread(audioPath)
    if '/train/' in audioPath:
        lab_path = audioPath.replace('/train/', '/lab/')[:-3] + 'lab'
    elif '/test/' in audioPath:
        lab_path = audioPath.replace('/test/', '/lab/')[:-3] + 'lab'
    else:
        lab_path = audioPath.replace('/valid/', '/lab/')[:-3] + 'lab'
    lab_file = open(lab_path, 'r')
    lab_content = lab_file.readlines()
    lab_file.close()
    for segment in lab_content:
        list_segment = segment.split(' ')
        start = float(list_segment[0])
        end = float(list_segment[1])
        label = list_segment[2][:-1]
        segmentData = audioData[int(start * fs):int(end * fs)]
        temp_path = 'tempSegment.wav'
        wavwrite(temp_path, segmentData, fs)
        segmentLPCC = calcLPCC(temp_path)
        os.remove(temp_path)
        for lpcc_item in segmentLPCC:
            songXlpcc.append(lpcc_item)
            songYlabel.append(label)

    return songXlpcc, songYlabel


def batch_extract_lpcc_feat(audio_dir):
    finalX = []
    finalY = []

    for root, dirs, filenames in os.walk(audio_dir):
        for filename in filenames:
            audioPath = os.path.join(root, filename)
            if '.wav' in audioPath:
                print audioPath
                songLPCC, songLabel = extract_lpcc_feat(audioPath)
                finalX.extend(songLPCC)
                finalY.extend(songLabel)
    return finalX, finalY


def save_dataset_XY(trainX, trainY, testX, testY, validX, validY):
    file = h5py.File('../data/pyT7/dataset.h5', 'w')
    file.create_dataset('trainX', data=trainX)
    file.create_dataset('trainY', data=trainY)
    file.create_dataset('testX', data=testX)
    file.create_dataset('testY', data=testY)
    file.create_dataset('validX', data=validX)
    file.create_dataset('validY', data=validY)
    file.close()

    return 0


def get_dataset_XY(dataset_h5='../data/pyT7/dataset.h5'):
    file = h5py.File(dataset_h5, 'r')
    trainX = file['trainX'][:]
    trainY = file['trainY'][:]
    testX = file['testX'][:]
    testY = file['testY'][:]
    validX = file['validX'][:]
    validY = file['validY'][:]
    file.close()
    return trainX, trainY, testX, testY, validX, validY


def main():
    audioDir = '../data/pyT7/'
    # batch_format_2_wav(audioDir)
    trainX, trainY = batch_extract_lpcc_feat(audioDir + 'train')
    testX, testY = batch_extract_lpcc_feat(audioDir + 'test')
    validX, validY = batch_extract_lpcc_feat(audioDir + 'valid')
    save_dataset_XY(trainX, trainY, testX, testY, validX, validY)

    return 0


if __name__ == '__main__':
    main()