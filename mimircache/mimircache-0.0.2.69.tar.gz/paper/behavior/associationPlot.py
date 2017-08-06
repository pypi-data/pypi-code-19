# coding=utf-8


"""
plot associations discovered by Mithril
"""
import glob

import imageio as imageio
import matplotlib
from PIL import Image

matplotlib.use("agg")
import matplotlib.pyplot as plt
import os


def loadData(dat):
    association_x = []
    association_y = []
    with open(dat) as ifile:
        for line in ifile:
            line = line.strip(", \n")
            if not line:
                continue
            lineSplitted = line.split(',')
            for i in range(1, len(lineSplitted)):
                association_x.append(int(lineSplitted[0].strip()))
                association_y.append(int(lineSplitted[i].strip()))


    return association_x, association_y


def plotData(dat):
    association_x, association_y = loadData(dat)
    plt.scatter(association_x, association_y, s=[2]*len(association_x), alpha=0.6)
    m = max(association_x)
    plt.xlim(xmin=-20000, xmax=m+20000)
    plt.ylim(ymin=-20000, ymax=m+20000)
    # plt.gca().get_xaxis().set_visible(False)
    # plt.gca().get_yaxis().set_visible(False)

    plt.xticks([])
    plt.yticks([])

    plt.xlabel("logical block address(LBA)", fontsize=20)
    plt.ylabel("logical block address(LBA)", fontsize=20)

    plt.savefig(dat+'.png', dpi=600)




################################################## animation ###################################################
def loadDataAnimation(dat):
    retVal = []
    association_x = []
    association_y = []
    with open(dat) as ifile:
        for line in ifile:
            line = line.strip(", \n")
            if not line:
                continue
            if 'output' in line:
                retVal.append([association_x, association_y])
                association_x = []
                association_y = []
                continue
            if 'size' in line:
                continue
            lineSplitted = line.split(',')
            for i in range(1, len(lineSplitted)):
                association_x.append(int(lineSplitted[0].strip()))
                association_y.append(int(lineSplitted[i].strip()))

    retVal.append([association_x, association_y])
    return retVal


def plotDataAnimation(dat):
    data = loadDataAnimation(dat)
    counter = 0
    for (association_x, association_y) in data:
        plt.scatter(association_x, association_y, s=[2]*len(association_x), alpha=0.6)
        m = 326597
        plt.xlim(xmin=-20000, xmax=m+20000)
        plt.ylim(ymin=-20000, ymax=m+20000)

        plt.xticks([])
        plt.yticks([])

        plt.xlabel("logical block address(LBA)", fontsize=20)
        plt.ylabel("logical block address(LBA)", fontsize=20)

        plt.savefig('assoc.ani/s{}.png'.format(counter)) #, dpi=600)
        plt.clf()
        counter += 1


def sort_filenames(filenames):
    return sorted(filenames, key=lambda x: int(x.split('/')[-1].split('_')[-1][:-4]))


def offline_plotting(folder_loc):
    DIRECTORY = "temp"
    if not os.path.exists(DIRECTORY):
        os.makedirs(DIRECTORY)
    gif_list = []
    for fileloc in glob.glob(folder_loc + "/*.png"):
        if not fileloc.split('/')[-1].split('_')[0] in gif_list:
            gif_list.append(fileloc.split('/')[-1].split('_')[0])
        im = Image.open(fileloc)
        im.save(DIRECTORY + fileloc.split('/')[-1])

    for prefix in gif_list:
        images = []
        png_list = []
        for fileloc in glob.glob(DIRECTORY + prefix + '*.png'):
            png_list.append(fileloc)
        print(png_list)
        png_list = sort_filenames(png_list)
        print(png_list)
        for fileloc in png_list:
            images.append(imageio.imread(fileloc))
        imageio.mimsave(prefix + '.gif', images, duration=0.6)





if __name__ == "__main__":
    # plotData("w94.association")
    # plotDataAnimation("assoc.ani/association.animation.raw")
    offline_plotting("assoc.ani")