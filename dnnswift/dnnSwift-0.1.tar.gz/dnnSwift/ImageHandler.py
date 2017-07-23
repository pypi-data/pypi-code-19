from __future__ import division
import h5py
import numpy as np
import pickle
import hashlib


class ImageHandlerException(Exception):
    pass


class H5FileException(Exception):
    pass


class ImageHandler(object):
    """
    This class loads and handles the image segments used for training the DNN
    """

    def __init__(
            self, filename, categories, data_split=None, index_dict=None,
            label_key="labels", image_key="images"):
        """
        Initialize the ImageHandler. It can either be initialized from
        scratch, in which case it splits the data into the training,
        validation, and test sets as indicated by the ratios of 'data_split',
        or it can be initialized from an existing index dictionary
        'index_dict'. If index_dict is not None, then the data_split argument
        is ignored. 'index_dict' should be a dictionary as returned by
        'save_lists(...)'.

        ### --------------------------------------------------------------- ###
        ### categories ###
        ### --------------------------------------------------------------- ###
        Internally, labels are one-hot unit vectors. 'categories' indicates
        the order of labels. For example, a category dict of {'label_A': 0,
        'label_B': 1, 'label_C': 2} would expand 'label_A' into the vector
        (1, 0, 0), 'label_B' into the vector (0, 1, 0), and 'label_C' into the
        vector (0, 0, 1).
        ### --------------------------------------------------------------- ###


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
        :param categories: A dictionary of image categories with their
            corresponding annotation values. All categories present in
            the dataset must be indicated here
        :param data_split: A list of relative image set sizes for, in this
            order, the training, validation, and testing image sets.
        :param index_dict: A dictionary containing: 1) A dictionary of
            indices and 2) a hash of the data file. The correct dictionary
            structure is returned by 'save_lists(...)'
        :param label_key: A custom key indicating which dataset to use as
            labels. This is particularly useful if a single hdf5 file has
            multiple possible label sets. Defaults to 'labels'
        :param image_key: A custom key indicating which dataset to use as
            images. Defaults to 'images'
        :return:
        """

        self._h5file = filename
        self._image_categories = categories
        self._indices = None
        self._hash = None
        self._label_key = label_key
        self._image_key = image_key
        self._image_dims = None

        # Load file and make sure the file has the correct structure
        image_dims = None
        all_labels = None
        label_dims = None
        hdf5_has_md5sum = None
        with h5py.File(filename, "r") as h5handle:
            try:
                image_dims = h5handle[image_key].shape
            except KeyError:
                raise H5FileException(
                    "The hdf5 file did not contain a '%s' dataset."
                    % image_key)
            try:
                all_labels = h5handle[label_key][()]
                label_dims = all_labels.shape
            except KeyError:
                raise H5FileException(
                    "The hdf5 file did not contain a '%s' dataset."
                    % label_key)

            hdf5_has_md5sum = "md5sum" in h5handle.keys()

        # Store image dimensions
        # NOTE: The hdf5 file is stored with the shape
        # (num_images, num_channels, x, y) because this is the most
        # logical indexing scheme , but the DNN requires the data to
        # have the shape (num_images, x, y, num_channels).
        # These differences are entirely internal and handled by ImageHandler
        self._image_dims = tuple([image_dims[1:][i] for i in (1, 2, 0)])

        # Ensure dataset shapes
        if len(image_dims) != 4:
            raise H5FileException("The '%s' dataset must be 4D")
        if len(label_dims) != 2:
            raise H5FileException("The '%s' dataset must be 2D")

        if image_dims[0] != label_dims[0]:
            raise H5FileException(
                "The number of images ('%s') and the number of labels "
                "('%s') must match")

        # Make sure all labels in the dataset are represented in 'categories'
        if np.sum(np.invert(np.in1d(all_labels, categories.keys()))) != 0:
            raise ValueError(
                "Some labels in the dataset are not represented in "
                "'categories'. This class is currently unable to deal with "
                "this ambiguity.")

        # Calculate has of hdf5 file (if it doesn't already exist)
        # Save it to the hdf5 file if it isn't present
        if hdf5_has_md5sum:
            with h5py.File(filename, "r") as h5handle:
                self._hash = h5handle["md5sum"][()]
        else:
            self_hash_md5 = hashlib.md5()
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    self_hash_md5.update(chunk)
            self._hash = self_hash_md5.hexdigest()
            with h5py.File(filename, "r+") as h5handle:
                h5handle.create_dataset(name="md5sum", data=self._hash)

        # if index_dict is not None, then load indices and the hash from it
        if index_dict is not None:
            try:
                self._indices = index_dict["index_list"]
                index_dict_hash = index_dict["h5file_hash"]
            except KeyError:
                raise ImageHandlerException(
                    "'index_dict' must contain the keys 'index_list' and "
                    "'h5file_hash'")

            # Compare index list hash to data file hash
            if index_dict_hash != self._hash:
                raise ImageHandlerException(
                    "Hashes for training data file and data split file do not "
                    "match")
        else:
            if data_split is None:
                data_split = {"train": 0.8, "val": 0.1, "test": 0.1}
            else:
                data_split = {
                    "train": float(data_split[0]),
                    "val": float(data_split[1]),
                    "test": float(data_split[2])}
                factor = sum(data_split.values())
                for key in data_split.keys():
                    data_split[key] /= factor

            # Generate image indices for each data set
            index_list = np.arange(image_dims[0])
            np.random.shuffle(index_list)
            # The numpy split function doesn't take the size of the segments
            # but their breakpoints
            lower_bound = 0.0
            upper_bound = 0.0
            self._indices = {}
            for key in data_split.keys():
                upper_bound += data_split[key] * len(index_list)
                self._indices[key] = np.array(
                    index_list[int(lower_bound):int(upper_bound)])
                lower_bound = upper_bound

    def get_images(self, list_name, index_low=None, index_high=None):
        """
        This method loads all images from the corresponding list between the
        indices index_low and index_high (inclusive!)

        :param list_name: The name of the list to use
        :param index_low: The first image to retrieve. If 'None' then set to 0
        :param index_high: The last image to retrieve (inclusive, not like
            python's slicing rules). If 'None' then set to last image of list
        :return: A dictionary containing the images and the corresponding
            labels in the keys 'images' and 'labels', respectively
        """
        if list_name not in self._indices.keys():
            raise ValueError(
                "'list_name' must be one of " + str(self._indices.keys()))

        if len(self._indices[list_name]) == 0:
            raise ValueError("Index list '%s' is empty" % list_name)

        if index_low is None:
            index_low = 0

        if index_high is None:
            index_high = len(self._indices[list_name])-1

        if index_low < 0 or index_low > len(self._indices[list_name])-1:
            raise ValueError(
                "'index_low' must be between 0 and %s" %
                (len(self._indices[list_name])-1))

        if not (index_low <= index_high <= len(self._indices[list_name]) - 1):
            raise ValueError(
                "'index_low <= index_high <= %s is not fulfilled" %
                (len(self._indices[list_name])-1))

        # h5py requires index lists be sorted. _sort_args is used to sort the
        # sub_index_list and _unsort_args can then be used to unsort it back
        # to the original order
        sub_index_list = self._indices[list_name][index_low:(index_high + 1)]
        sub_index_list_sort_args = np.argsort(sub_index_list)
        sub_index_list_unsort_args = np.argsort(sub_index_list_sort_args)
        sub_index_list_sorted = sub_index_list[sub_index_list_sort_args]

        with h5py.File(self._h5file, "r") as h5f:
            # The HDF5 format becomes incredibly slow when attempting to
            # slice > 1000 non-consecutive entries. Experience has shown that
            # if a large number of images must be retrieved, it is much faster
            # to retrieve them in multiple, smaller batches.
            n_images = len(sub_index_list_sorted)
            max_batchsize = 128
            if n_images <= max_batchsize:
                batchsize = n_images
                n_batches = 1
            else:
                batchsize = max_batchsize
                n_batches = (n_images // batchsize) + 1
            imgs = []
            labels = []
            for i in range(n_batches):
                low = i * batchsize
                high = min((i + 1) * batchsize, n_images)
                if low >= high:
                    continue
                image_indices = sub_index_list_sorted[low:high].tolist()
                imgs.append(h5f[self._image_key][image_indices, :, :, :])
                labels.append(h5f[self._label_key][image_indices, :])

        imgs = np.concatenate(imgs)
        imgs = imgs[sub_index_list_unsort_args]
        imgs = np.transpose(imgs, (0, 2, 3, 1))
        labels = np.concatenate(labels)
        labels = labels[sub_index_list_unsort_args]

        # Translate the labels into unit vectors
        label_matrix = np.identity(max(self._image_categories.values()) + 1)
        label_vectors = []
        for lab in labels:
            key_ind = self._image_categories[lab[0]]
            label_vectors.append(label_matrix[key_ind])
        label_vectors = np.stack(label_vectors)

        return {"images": imgs, "labels": label_vectors}

    def scramble_dataset(self, list_name):
        """
        Randomize the order of one of the data sets.

        :param list_name: The name of the data set to scramble
        :return:
        """

        if list_name not in self._indices.keys():
            raise ValueError(
                "'list_name' must be one of " + str(self._indices.keys()))

        if len(self._indices[list_name]) == 0:
            raise ValueError("Dataset '%s' is empty" % list_name)

        new_i = np.random.permutation(len(self._indices[list_name]))
        self._indices[list_name] = self._indices[list_name][new_i]

    @DeprecationWarning
    def get_image_groups(self):
        """
        Retrieves the image groups (e.g. "edges", "foreground", "background").

        DEPRECATION WARNING: This function is probably useless as ImageHandler
        is given the categories as arguments during creation, meaning there
        will never be a use case in which the categories must be retrieved
        from here.

        :return: A dictionary of all the image groups and their integer values
        """

        return self._image_categories

    def get_list_names(self):
        """
        Retrieves the names of all lists
        :return:
        """

        return self._indices.keys()

    def get_list_length(self, list_name):
        """
        A wrapper function, which returns the length of a given list
        :param list_name:
        :return:
        """

        return len(self._indices[list_name])

    def get_image_dims(self):
        """
        A wrapper function, which returns the dimensions of the images in
        the shape required by the DNN: (spatial, spatial, num_channels)
        :return:
        """
        return self._image_dims

    def save_lists(self, filename):
        """
        Saves the index lists (with index source) for later recovery.
        :param filename: Filename under which to save the index list
        :return:
        """

        out_dat = dict()
        out_dat["h5file_hash"] = self._hash
        out_dat["index_list"] = self._indices

        with open(filename, "wb") as f:
            pickle.dump(out_dat, f, pickle.HIGHEST_PROTOCOL)

    @DeprecationWarning
    def save_categories(self, filename):
        """
        Saves the categories. The categories are passed as a dictionary,
        meaning that they are reorganized alphabetically by python. The saved
        file will make translating numeric labels to their annotation easier.

        DEPRECATION WARNING: This function is probably useless as ImageHandler
        is given the categories as arguments during creation, meaning there
        will never be a use case in which the categories must be retrieved
        from here.

        :param filename:
        :return:
        """

        out_dat = dict()
        out_dat["h5file_hash"] = self._hash
        out_dat["categories"] = self._image_categories

        with open(filename, "wb") as f:
            pickle.dump(obj=out_dat, file=f, protocol=pickle.HIGHEST_PROTOCOL)
