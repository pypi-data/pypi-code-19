from PIL import Image
import sys



def most_frequent_colour(image):

    w, h = image.size
    pixels = image.getcolors(w * h)

    most_frequent_pixel = pixels[0]

    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)

    return most_frequent_pixel[1]


def average_colour_in_k_clusters(image, k):
    pass


def compare(title, image, colour_tuple):
    image.show(title=title)
    image = Image.new("RGB", (200, 200,), colour_tuple)
    return image


def kmeans(pixels, k):
    numFeatures = len(pixels)

    centroids = getRandomCentroids(numFeatures, k)

    iterations = 0
    oldCentroids = None

    while not shouldStop(oldCentroids, centroids, iterations):

        oldCentroids = centroids

        interations += 1


def save(name, result, image):
    image.save("images/results/{}.jpg".format(name))
    sample = Image.new("RGB", (200, 200,), result)
    sample.save("images/results/{}-result.jpg".format(name))


def main():
    image = Image.open("/Volumes/4TB/PROJETS/Code/PyQT/MTB_QT_Widgets/01-Image_Compare/b.jpg")

    print(most_frequent_colour(image))

    # if "mode" in sys.argv:
    #     result = most_frequent_colour(image)
    #
    # if "ave" in sys.argv:
    #     result = average_colour(image)
    #
    # save("Wheatbelt", result, image)


if __name__ == "__main__":
    main()