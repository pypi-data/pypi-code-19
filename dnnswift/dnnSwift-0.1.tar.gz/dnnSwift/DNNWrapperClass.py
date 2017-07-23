import ImageHandler
import DNN
import os
import numpy as np

# __all__ = ["DNNSwift", "DNNSwiftException"]


class DNNSwiftException(Exception):
    pass


class DNNWrapper(object):
    """
    This is an interface class that serves only to simplify the calls to this
    package. Most of the functionality lies in the DNN and ImageHandler
    classes.

    This class stores and reuses the DNN to save time. It only reinitializes
    the DNN if parameters change.
    """

    def __init__(self, categories, layout, base_dir):
        """
        This is an interface class that serves only to simplify the calls to
        this package. Most of the functionality lies in the DNN and
        ImageHandler classes.

        ### --------------------------------------------------------------- ###
        ### categories ###
        ### --------------------------------------------------------------- ###
        Internally, labels are one-hot unit vectors. 'categories' indicates
        the order of labels. For example, a category dictionary of
        {'label_A': 0, 'label_B': 1, 'label_C': 2} would expand 'label_A' into
        the vector (1, 0, 0), 'label_B' into the vector (0, 1, 0), and
        'label_C' into the vector (0, 0, 1).
        ### --------------------------------------------------------------- ###

        ### --------------------------------------------------------------- ###
        ### layout ###
        ### --------------------------------------------------------------- ###
        Defines the layout of the DNN. This should be a list of dictionaries
        in the format
            [{name: "A", type: "conv", ...},
             {name: "B", type: "conv", ...},
             {name: "C", type: "fc", ...}]

        A detailed guide on the structure of the layout file can be seen in the
        vignette.
        ### --------------------------------------------------------------- ###

        :param layout: A list of dictionaries
        :param categories: A dictionary of image categories with their
            corresponding annotation values. All categories present in
            the dataset must be indicated here
        :param base_dir: The directory into which output should be saved (e.g.
            the weights, the index lists for the training / validation /
            testing data, etc.
        """
        self._ready_for_training = False
        self._image_handler = None
        self._dnn = None

        # Params needed by multiple functions
        self._categories = categories
        self._base_dir = base_dir
        self._layout = layout
        pass

    def initialize_training_data(
            self, filename, data_split=None,
            index_dict=None, image_key="images", label_key="labels",
            outfile=None):
        """
        Initialize the ImageHandler. It can either be initialized from
        scratch, in which case it splits the data into the training,
        validation, and test sets as indicated by the ratios of 'data_split',
        or it can be initialized from an existing index dictionary
        'index_dict'. If index_dict is not None, then the data_split argument
        is ignored. 'index_dict' should be a dictionary as returned by
        'save_lists(...)'.

        ### --------------------------------------------------------------- ###
        ### hdf5 file structure ###
        ### --------------------------------------------------------------- ###
        The hdf5 file must have the following structure:
        FILE
            <HDF5 dataset "images": shape (num_images, num_channels, x, y)>
            <HDF5 dataset "labels": shape (num_images, 1)>

        The names of the dataset can be custom, but must match the parameters
        'label_key' and 'image_key'.
        ### --------------------------------------------------------------- ###

        ### --------------------------------------------------------------- ###
        ### data_split ###
        ### --------------------------------------------------------------- ###
        'data_split' should be a list of values indicating the relative sizes
        of the training, validation, and testing image sets. E.g.

            - data_split = [0.8, 0.1, 0.1] will create three datasets, the
                "train" dataset consisting of 80% of the segments, the "val"
                dataset consisting of 10%, and the "test" dataset consisting
                of 10% of the data.

        The values are normalized internally, so [0.8, 0.1, 0.1] is equivalent
        to [8, 1, 1] or [16, 2, 2]
        ### --------------------------------------------------------------- ###

        :param filename: The full filename of the hdf5 file with the images to
            train on
        :param data_split: A list of relative image set sizes for, in this
            order, the training, validation, and testing image sets.
        :param index_dict: A dictionary containing: 1) A dictionary of
            indices and 2) a hash of the data file. The correct dictionary
            structure is returned by 'save_lists(...)'
        :param label_key: A string indicating which dataset to use as
            labels. This is particularly useful if a single hdf5 file has
            multiple possible label sets. Defaults to 'labels'
        :param image_key: A string indicating which dataset to use as
            images. Defaults to 'images'
        :param outfile: A string. ImageHandler saves the index lists for each
            data set (training, validation, testing). This is the filename
            of that pickled data set. Will be saved under self._base_dir.
            If 'None', the dictionary isn't saved. Defaults to 'None'. Never
            overwrites an existing file.
        :return:
        """

        # Initialize the image handler
        self._image_handler = ImageHandler.ImageHandler(
            filename=filename, categories=self._categories,
            data_split=data_split, index_dict=index_dict,
            image_key=image_key, label_key=label_key)
        self._ready_for_training = True

        # Save the resulting index lists
        if outfile is not None:
            if not os.path.isfile(os.path.join(self._base_dir, outfile)):
                self._image_handler.save_lists(filename=outfile)
            else:
                print(
                    "WARNING: '%s' already exists, index lists not being "
                    "saved" % os.path.join(self._base_dir, outfile))

        return None

    def train_dnn(
            self, num_epochs, batch_size=1, weights=None,
            verbose=True, weights_dir=".", logfile=None, learning_rate=1e-3,
            start_epoch=0):
        """
        Trains the DNN

        :param num_epochs: An integer defining the number of epochs for which
            to train the DNN
        :param batch_size: An integer defining the batchsize of the DNN.
            Typical values should be powers of 2 to optimize speed.
        :param weights: A dictionary of weights with keys corresponding to the
            node names in layer_params, which require weights (e.g. pooling
            layers do not require weights and complex nodes such as the
            'inception' nodes require multiple weights). The weights files
            output by the training are in the correct format to be read back
            in, i.e. to continue training.
        :param verbose: A boolean defining the level of detail to be output.
            If 'True', then the progress within an epoch is printed. If
            'False', then only the validation accuracy after each epoch is
             printed.
        :param weights_dir: A string defining the output directory into which
            to save the weights. This is a relative directory under
            "base_dir".
        :param logfile: A string defining the file into which to write the
            status output. This is an absolute path for easier integration
            into other workflows. If 'None' then output is printed to stdout.
        :param learning_rate: A floating point value indicating the learning
            rate at which to train the DNN. Note that many optimizers already
            dynamically adjust the learning rate throughout the learning,
            making this parameter unpredictable and possible useless. It only
            exists for legacy reasons
        :param start_epoch: An integer defining the epoch at which to start
            training. If start_epoch == 4, then the first output will have the
            name "weights_4.pkl" and "val_4.pkl". This is useful for continuing
            training and avoiding filename conflicts. NOTE: This does not
            automatically read in the previous weight set. To properly continue
            training, you must load the correct weights file manually and pass
            the contents to the 'weights' parameter.
        :return:
        """

        if not self._ready_for_training:
            raise DNNSwiftException(
                "Run 'initialize_training_data(...)' before training DNN")

        image_dims = self._image_handler.get_image_dims()
        categories = self._categories

        # Create DNN object
        self._dnn = DNN.DNN(
            img_dims=image_dims, categories=categories,
            layer_params=self._layout, learning_rate=learning_rate,
            weights=weights, basedir=self._base_dir)

        # Train DNN
        self._dnn.train_network(
            batch_size=batch_size, image_handler=self._image_handler,
            num_epochs=num_epochs, verbose=verbose, subdir=weights_dir,
            logfile=logfile, start_epoch=start_epoch)

        return None

    def apply_dnn(self, images, weights=None):
        """
        Applies the DNN to an input image.

        This function reinitializes the DNN when necessary. Specifically, it
        compares the weights to the internal weights of the DNN and the
        spatial dimensions of 'images' with the internally stored image size
        of the DNN. If 'weights' is None, the internal DNN is always used.

        :param images: An iterable of numpy arrays with the shape
            (spatial, spatial, num_channels). This can also be a 4D numpy
            array with the dimensions
            (num_images, spatial, spatial, num_channels). Images must all
            have the same shape.
        :param weights: A dictionary of weights to use. Should match the node
            names of the class' layout. In general, only the files outputted
            by this class during training should be used as input. If
            'weights' is None, the function attempts to use the current
            weights of the DNN
        :return:
        """

        # Ensure all images have the same shape
        imshapes = [image.shape for image in images]
        if len(set(imshapes)) != 1:
            raise DNNSwiftException("All images must have the same shape")

        # Extract image shape
        image_dims = images[0].shape

        # If 'weights' is None, load the DNN weights
        if weights is None:
            try:
                weights = self._dnn.get_weights()
            except AttributeError:
                raise DNNSwiftException(
                    "'weights' cannot be None if no initialized DNN exists.")

        # Determine if a new DNN must be made
        if self._dnn is None:
            make_new_dnn = True
        else:
            make_new_dnn = False
            # compare 'weights'
            dnn_weights = self._dnn.get_weights()
            if set(dnn_weights.keys()) != set(weights.keys()):
                make_new_dnn = True
            else:
                for key in dnn_weights.keys():
                    if np.sum(~np.equal(dnn_weights[key], weights[key])) != 0:
                        make_new_dnn = True
                        break
            # compare image dimensions
            if image_dims != self._dnn.get_image_dims():
                make_new_dnn = True

        print("Reinitializing DNN: %s" % str(make_new_dnn))

        if make_new_dnn:
            self._dnn = DNN.DNN(
                img_dims=image_dims, categories=self._categories,
                layer_params=self._layout, basedir=self._base_dir,
                weights=weights)

        # Apply network to images
        output = self._dnn.run_network(input_images=np.array(images))
        return output

    def get_images(self, list_name, index_low=None, index_high=None):
        """
        This is a wrapper for ImageHandler.get_images

        :param list_name: The name of the list to use. This should be one of
            "train", "val", or "test"
        :param index_low: The first image to retrieve. If 'None' then set to 0
        :param index_high: The last image to retrieve (inclusive, not like
            python's slicing rules). If 'None' then set to last image of list
        :return: A dictionary containing the images and the corresponding
            labels in the keys 'images' and 'labels', respectively
        """
        return self._image_handler.get_images(
            list_name=list_name, index_low=index_low, index_high=index_high)

    def get_weights(self):
        """
        This is a wrapper function for DNN.get_weights(). Returns None if the
        DNN hasn't been initiated yet.
        :return:
        """
        try:
            weights = self._dnn.get_weights()
        except AttributeError:
            weights = None

        return weights

    def get_image_dims(self):
        """
        This is a wrapper function for DNN.get_image_dims(). Returns None if
        the DNN hasn't been initiated yet
        :return:
        """

        try:
            img_dims = self._dnn.get_image_dims()
        except AttributeError:
            img_dims = None

        return img_dims

    def print_structure(self, filename):
        """
        This is a wrapper function for DNN.print_structure(). Prints the
        structure as an image to 'filename' if the DNN has been initialized.
        Otherwise it does nothing
        :return:
        """
        try:
            self._dnn.print_structure(filename=filename)
        except AttributeError:
            pass

        return None
