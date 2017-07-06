"""
This file contains the full ImageFeaturizer class, which allows users to upload
an image directory, a csv containing a list of image URLs, or a directory with a
csv containing names of images in the directory.

It featurizes the images using pretrained, decapitated InceptionV3 model, and
saves the featurized data to a csv, as well as within the ImageFeaturizer class
itself. This allows data scientists to easily analyze image data using simpler models.

Functionality:

    1. Build the featurizer model. The class initializer ImageFeaturizer() takes as input:
        depth : int
            1, 2, 3, or 4, depending on how far down you want to sample the featurizer layer

        auto_sample : bool
            a boolean flag signalling automatic downsampling

        downsample_size : int
            desired number of features to downsample the final layer to. Must be an
            integer divisor of the number of features in the layer.

    2. Load the data. The self.load_data() function takes as input:
            image_column_header : str
                the name of the column holding the image data, if a csv exists,
                or what the name of the column will be, if generating the csv
                from a directory

            image_path : str
                the path to the folder containing the images. If using URLs, leave blank

            csv_path : str
                the path to the csv. If just using a directory, leave blank, and
                specify the path for the generated csv in new_csv_name.
                If csv exists, this is the path where the featurized csv will be
                generated.

            new_csv_name : str
                the path to the new csv, if one is being generated from a directory.
                If no csv exists, this is the path where the featurized csv will
                be generated

            scaled_size : tuple
                The size that the images get scaled to. Default is (299, 299)

            grayscale : bool
                Decides if image is grayscale or not. May get deprecated. Don't
                think it works on the InceptionV3 model due to input size.

    3. Featurize the data. The self.featurize() function takes no input, and featurizes
       the loaded data, writing the new csvs to the same path as the loaded csv

    3a. Users can also load and featurize the data in one pass, with the
        self.load_and_featurize_data function, which takes the same input as the
        load_data function and performs the featurization automatically.

"""

import logging
import os

import numpy as np
import trafaret as t

from .build_featurizer import build_featurizer, supported_model_types
from .data_featurizing import featurize_data, features_to_csv
from .feature_preprocessing import preprocess_data


class ImageFeaturizer:
    """
    This object can load images, rescale, crop, and vectorize them into a
    uniform batch, and then featurize the images for use with custom classifiers.

          Methods
    ------------------
        __init__(depth, auto_sample,
                 downsample_size):
            --------------------------------
            Initialize the ImageFeaturizer. Build the featurizer model with the
            depth and feature downsampling specified by the inputs.



        load_and_featurize_data(image_column_header, image_path,
                                csv_path, new_csv_name, scaled_size, grayscale):
            --------------------------------
            Loads image directory and/or csv into the model, and
            featurizes the images



        load_data(image_column_header, image_path, csv_path,
                  new_csv_name, scaled_size, grayscale):
            --------------------------------
            Loads image directory and/or csv into the model, and vectorize the
            images for input into the featurizer



        featurize():
            --------------------------------
            Featurize the loaded data, append the features to the csv, and
            return the full dataframe


    """

    @t.guard(depth=t.Int(gte=1, lte=4),
             auto_sample=t.Bool,
             downsample_size=t.Int(gte=0),
             model=t.Enum(*supported_model_types.keys()))
    def __init__(self,
                 depth=1,
                 auto_sample=False,
                 downsample_size=0,
                 model='squeezenet'
                 ):
        """
        Initializer.

        Loads an initial InceptionV3 pretrained network, decapitates it and
        downsamples according to user specifications.

        Parameters:
        ----------
            depth : int
                How deep to decapitate the model. Deeper means less specific but
                also less complex

            auto_sample : bool
                If True, feature layer is automatically downsampled to the right size.

            downsample_size: int
                The number of features to downsample the featurizer to

        Returns:
        --------
        None. Initializes and saves the featurizer object attributes.

        """
        # BUILDING THE MODEL #
        logging.info("\nBuilding the featurizer.")

        featurizer = build_featurizer(depth, auto_sample,
                                      downsample_size, model_str=model.lower())

        # Saving initializations of model
        self.depth = depth
        self.auto_sample = auto_sample
        self.downsample_size = downsample_size

        # Save the model
        self.model_name = model.lower()
        self.featurizer = featurizer
        self.visualize = featurizer.summary

        # Initializing preprocessing variables for after we load the images
        self.data = np.zeros((1))
        self.featurized_data = np.zeros((1))
        self.csv_path = ''
        self.image_list = ''
        self.image_column_header = ''
        self.image_path = ''

        # Image scaling and cropping
        self.scaled_size = (0, 0)
        self.crop_size = (0, 0)
        self.number_crops = 0
        self.isotropic_scaling = False

    def load_and_featurize_data(self,
                                image_column_header,
                                image_path='',
                                csv_path='',
                                new_csv_name='featurizer_csv/generated_images_csv',
                                grayscale=False

                                # crop_size = (299, 299),
                                # number_crops = 0,
                                # random_crop = False,
                                # isotropic_scaling = True
                                ):
        """
        Load image directory and/or csv, and vectorize the images for input into the featurizer.
        Then, featurize the data.

        Parameters:
        ----------
            image_column_header : str
                the name of the column holding the image data, if a csv exists,
                or what the name of the column will be, if generating the csv
                from a directory

            image_path : str
                the path to the folder containing the images. If using URLs, leave blank

            csv_path : str
                the path to the csv. If just using a directory, leave blank, and
                specify the path for the generated csv in new_csv_name.
                If csv exists, this is the path where the featurized csv will be
                generated.

            new_csv_name : str
                the path to the new csv, if one is being generated from a directory.
                If no csv exists, this is the path where the featurized csv will
                be generated

            grayscale : bool
                Decides if image is grayscale or not. May get deprecated. Don't
                think it works on the InceptionV3 model due to input size.

            ### These features haven't been implemented yet.
            # isotropic_scaling : bool
            #     if True, images are scaled keeping proportions and then cropped
            #
            # crop_size: tuple
            #     if the image gets cropped, decides the size of the crop
            #
            # random_crop: bool
            #    If False, only take the center crop. If True, take random crop
            #

        Returns:
        --------
            full_dataframe :
                Dataframe containing the features appended to the original csv.
                Also writes csvs containing the features only and the full dataframe
                to the same path as the csv containing the list of names

        """
        self.load_data(image_column_header, image_path, csv_path, new_csv_name, grayscale)
        return self.featurize()

    def load_data(self,
                  image_column_header,
                  image_path='',
                  csv_path='',
                  new_csv_name='featurizer_csv/generated_images_csv',
                  grayscale=False

                  # crop_size = (299, 299),
                  # number_crops = 0,
                  # random_crop = False,
                  # isotropic_scaling = True
                  ):
        """
        Load image directory and/or csv, and vectorize the images for input into the featurizer.

        Parameters:
        ----------
            image_column_header : str
                the name of the column holding the image data, if a csv exists,
                or what the name of the column will be, if generating the csv
                from a directory

            image_path : str
                the path to the folder containing the images. If using URLs, leave blank

            csv_path : str
                the path to the csv. If just using a directory, leave blank, and
                specify the path for the generated csv in new_csv_name.
                If csv exists, this is the path where the featurized csv will be
                generated.

            new_csv_name : str
                the path to the new csv, if one is being generated from a directory.
                If no csv exists, this is the path where the featurized csv will
                be generated

            grayscale : bool
                Decides if image is grayscale or not. May get deprecated. Don't
                think it works on the InceptionV3 model due to input size.

            ### These features haven't been implemented yet.
            # isotropic_scaling : bool
            #     if True, images are scaled keeping proportions and then cropped
            #
            # crop_size: tuple
            #     if the image gets cropped, decides the size of the crop
            #
            # random_crop: bool
            #    If False, only take the center crop. If True, take random crop
            #

        """
        size_dict = {'squeezenet': (227, 227), 'vgg16': (224, 224), 'vgg19': (224, 224),
                     'resnet50': (224, 224), 'inceptionv3': (299, 299), 'xception': (299, 299)}

        scaled_size = size_dict[self.model_name]

        # If new csv_path is being generated, make sure the folder exists.
        if (csv_path == ''):
            path_to_new_csv = os.path.dirname(new_csv_name)
            if not os.path.isdir(path_to_new_csv) and path_to_new_csv != '':
                os.makedirs(os.path.dirname(new_csv_name))

        # Add backslash to end of image path if it is not there
        if image_path != '' and image_path[-1] != "/":
            image_path = '{}/'.format(image_path)

        # Save the full image tensor, the path to the csv, and the list of image paths
        (full_image_data, csv_path, list_of_image_paths) = \
            preprocess_data(image_column_header, image_path, csv_path,
                            new_csv_name, scaled_size, grayscale)

        # Save all of the necessary data to the featurizer
        self.data = full_image_data
        self.csv_path = csv_path
        self.image_list = list_of_image_paths
        self.image_column_header = image_column_header
        self.scaled_size = scaled_size
        self.image_path = image_path

    def featurize(self):
        """
        Featurize the loaded data, returning the dataframe and writing the features
        and the full combined data to csv

        Parameters
        ----------
        None, just operates on the loaded data

        Returns
        -------
            full_dataframe : pandas.DataFrame
                Dataframe containing the features appended to the original csv.
                Also writes csvs containing the features only and the full dataframe
                to the same path as the csv containing the list of names

        """
        logging.info("Checking array initialized.")
        if np.array_equal(self.data, np.zeros((1))):
            raise IOError('Must load data into the model first. Call load_data.')

        logging.info("Trying to featurize data.")
        self.featurized_data = featurize_data(self.featurizer, self.data)
        full_dataframe = features_to_csv(self.featurized_data, self.csv_path,
                                         self.image_column_header, self.image_list)
        return full_dataframe
