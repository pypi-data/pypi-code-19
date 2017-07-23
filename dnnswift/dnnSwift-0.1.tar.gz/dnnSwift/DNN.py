# TODO: Implement batch normalization
#       (http://r2rt.com/implementing-batch-normalization-in-tensorflow.html)
#       Add population mean/variance as instance variables -> reset at the
#           beginning of each training run and calculate only during one epoch
#       Assign to a tf.Variable at the end of the epoch
#       Add batch-normalization layer
from __future__ import division
import tensorflow as tf
import time
import os
import sys
import numpy as np
import pickle
import pygraphviz as pgv
from Validator import Validator


class DNN(object):
    """
    A deep CNN to train the edge detector.
    """
    # Static members

    # Careful when changing this, it must have one and only one '%s'
    # element and no other replacements. There is no consistency check for
    # this and unsupported formats may lead to errors
    __WEIGHTS_FILENAME_SCHEME__ = "weights_%s.pkl"
    __VALIDATION_FILENAME_SCHEME__ = "val_%s.pkl"

    def __setattr__(self, key, value):
        """
        This custom method exists only as a development tool to ensure that
        all members of DNN are declared at the beginning of
        __init__ because let's face it, python is a total mess regarding 
        class members.
        :param key: 
        :param value: 
        :return: 
        """
        if "locked" in self.__dict__.keys() and key \
                not in self.__dict__.keys():
            raise NameError("Class is locked. Cannot add/modify attributes")
        self.__dict__[key] = value

    def __init__(self, img_dims, categories, layer_params, learning_rate=1e-3,
                 weights=None, basedir="."):
        """
        If weights=None then the weights are initialized to random values
        (using a Glorot uniform initialization scheme:
        StackExchange explanation: http://stats.stackexchange.com/questions/200513/how-to-choose-train-matrix-values-of-convolution-kernel-in-neural-networks
        Glorot: http://jmlr.org/proceedings/papers/v9/glorot10a/glorot10a.pdf
        He Normal: http://arxiv.org/abs/1502.018525

        If 'weights' has a value, it must be a dictionary with keys named
        'layer_name/w' and 'layer_name/b'. All layer names listed in
        'layer_params' must have both a '/w' and a '/b' in the dictionary.
        The network is set up with these values.
        
        Custom node creation functions can be added to the 'node_dispatcher' 
        dictionary. These functions must return a tuple with the structure:
        ([list of tensorflow nodes], {dictionary of weights})

        :param img_dims: The dimensions of the image (x, y, z)
        :param categories: A dictionary mapping category names to the label values
        :param layer_params: The layer parameters
        :param learning_rate: The learning rate of the neural net optimizer
        function
        :param weights: A dictionary of weights with keys corresponding to the
        node names in layer_params
        :param basedir: The directory in which to store all files. Defaults to
        the current directory
        """

        # Check that base directory exists
        if not os.path.isdir(basedir):
            raise ValueError("'basedir' directory must exist and cannot be "
                             "created by this class.")

        # Check layer_params
        layer_names = [entry["name"] for entry in layer_params]
        if len(layer_names) != len(set(layer_names)):
            raise ValueError("The names of each 'layer_params' entry must be "
                             "unique.")

        # Set up or declare class members
        self._basedir = basedir
        self._training_data_split = os.path.join(
            self._basedir, "DNN_TrainingDataSplit.pkl")
        self._layer_params = layer_params
        self._graph = tf.Graph()
        # self._accuracy_list = []
        self._labels = None
        self._layers = {}
        self._inputs = {}
        self._variables = {}
        self._output_layer = None
        self._y_sm = None
        self._session = None
        self._summary_writer = None
        self._optimizer = None
        self._cost_function_set = False
        self._learning_rate = learning_rate
        self._input_dims = img_dims
        self._categories = categories
        self._unpooling_indices = {}

        # Lock the class and permit no new members
        self.locked = True

        # Define node dispatcher
        node_dispatcher = {
            "input": self.add_input,
            "conv": self.add_conv,
            "maxpool": self.add_maxpool,
            "maxpool_with_argmax": self.add_maxpool_with_argmax,
            "fc": self.add_fc,
            "concat": self.add_concat,
            "inception": self.add_inception,
            "cross_entropy": self.add_optimizer,
            "rmse": self.add_optimizer
        }

        # Build network
        with self._graph.as_default():
            self._labels = tf.placeholder(dtype=tf.float32,
                                          shape=[None, len(categories)])
            for layer_i in range(len(layer_params)):
                param_list = layer_params[layer_i]
                param_list["weights"] = weights
                layer_name = param_list["name"]
                layer_type = param_list["type"]

                try:
                    node_func = node_dispatcher[layer_type]
                except KeyError:
                    raise Exception("Unsupported node type (%s | %s)"
                                    % (layer_name, layer_type))

                node_func(params=param_list)

            if self._output_layer is None:
                raise ValueError("There needs to be exactly one cost function "
                                 "node (this node is ignored if the network "
                                 "is not being trained but is still required "
                                 "by the code).")

            self._y_sm = tf.nn.softmax(logits=self._output_layer,
                                       name="y_pred")

            # Initiate the session
            self._session = tf.Session()
            self._session.run(tf.global_variables_initializer())

    @DeprecationWarning
    def get_accuracy_list(self):
        """
        Get self._accuracy_list
        :return:
        """
        # return self._accuracy_list
        return None

    @staticmethod
    def get_weights_filename_scheme():
        """
        Get self._weights_filename_scheme
        :return: 
        """
        return DNN.__WEIGHTS_FILENAME_SCHEME__

    @staticmethod
    def get_validation_filename_scheme():
        """
        Get self._weights_filename_scheme
        :return: 
        """
        return DNN.__VALIDATION_FILENAME_SCHEME__

    @staticmethod
    def get_weights_filename_scheme_regex():
        """
        Get self._weights_filename_scheme as as regular expression
        :return: 
        """
        reg_string = DNN.__WEIGHTS_FILENAME_SCHEME__.replace(
            "%s", "(.*)")
        return reg_string

    @staticmethod
    def get_validation_filename_scheme_regex():
        """
        Get self._weights_filename_scheme as as regular expression
        :return: 
        """
        reg_string = DNN.__VALIDATION_FILENAME_SCHEME__.replace(
            "%s", "(.*)")
        return reg_string

    def train_network(self, batch_size, num_epochs, image_handler,
                      verbose=True, subdir=".", logfile=None, start_epoch=0):
        """
        Trains the network. Currently requires training and validation data.
        :param image_handler: An object of type ImageHandler containing
        the data
        :param batch_size: The size of the training batches for the stochastic
        gradient descent
        :param num_epochs: The number of times to iterate over the entire
        training data set
        :param verbose: 'True' for giving full status
        :param subdir: The subdirectory of 'self._basedir' in which to save
        the weights and accuracies after each epoch. Defaults to ".", i.e.
        basedir directly.
        :param logfile: If this file exists, then all output is written there
        instead of stdout
        :param start_epoch: This function saves weights after each epoch in
        the format "weights_EPOCH.pkl". If desired,
        the starting epoch can be set to any given integer to avoid filename
        conflicts (e.g. if training is being
        continued after an interruption). This is automatically truncated to
        an integer (e.g. 2.9 -> 2)
        :return:
        """
        # Create the subdir
        if not os.path.isdir(os.path.join(self._basedir, subdir)):
            os.makedirs(os.path.join(self._basedir, subdir))

        # Load validation data
        image_handler.scramble_dataset("val")
        img_val = image_handler.get_images(list_name="val")

        # The validation data feed dict only needs to be defined once
        feed_dict_val = {
            self._layers[key]: img_val["images"][:, :, :, self._inputs[key]]
            for key in self._inputs.keys()}
        feed_dict_val[self._labels] = img_val["labels"]

        # Save initial weights
        self.save_weights(os.path.join(
            self._basedir, subdir,
            DNN.__WEIGHTS_FILENAME_SCHEME__ % "start"))

        num_batches = \
            image_handler.get_list_length("train") // batch_size

        for epoch_i in range(int(start_epoch), num_epochs):
            start_time = time.time()
            # Randomly resort the training data to create new batches each
            # epoch
            image_handler.scramble_dataset("train")

            # Go through each batch and train the network
            for batch_i in range(num_batches):
                low = batch_i * batch_size
                high = min(
                    ((batch_i + 1) * batch_size) - 1,
                    image_handler.get_list_length("train") - 1)
                if low > high:
                    continue
                img_data = image_handler.get_images(
                    list_name="train", index_low=low,
                    index_high=high)
                feed_dict_train = {
                    self._layers[key]:
                        img_data["images"][:, :, :, self._inputs[key]] for
                    key in self._inputs.keys()}
                feed_dict_train[self._labels] = img_data["labels"]
                self._session.run(self._optimizer, feed_dict=feed_dict_train)

                if verbose:
                    if batch_i % max((num_batches // 100), 1) == 0:
                        cur_time = time.time()
                        elapsed_time = cur_time - start_time
                        elapsed_percentage = \
                            1.0 * (batch_i + 1) / (num_batches + 1)
                        total_time = elapsed_time / elapsed_percentage
                        remaining_time = total_time - elapsed_time
                        rt_m, rt_s = divmod(remaining_time, 60)
                        rt_h, rt_m = divmod(rt_m, 60)
                        if logfile is not None:
                            with open(logfile, "a") as f:
                                f.write("Epoch %s Batch %s of %s (%s%%) | "
                                        "Remaining time until end of epoch: "
                                        "%02d:%02d:%02d\n" %
                                        (epoch_i, batch_i, num_batches,
                                         (100. * batch_i / num_batches),
                                         rt_h, rt_m, rt_s))
                        else:
                            sys.stdout.write(
                                "Epoch %s Batch %s of %s (%s%%) | Remaining "
                                "time until end of epoch: %02d:%02d:%02d\n" %
                                (epoch_i, batch_i, num_batches,
                                 (100. * batch_i / num_batches),
                                 rt_h, rt_m, rt_s))
                            sys.stdout.flush()

            # Determine validation accuracy
            val_output = self.run_network(input_images=img_val["images"])
            val_output = np.squeeze(val_output, (1, 2))

            validation = Validator(network_output=val_output,
                                   labels=img_val["labels"],
                                   image_groups=self._categories)
            val_file = os.path.join(
                self._basedir, subdir,
                DNN.__VALIDATION_FILENAME_SCHEME__ % str(epoch_i))
            validation.save_results(filename=val_file)

            val_acc = validation.get_top_1_acc()
            # self._accuracy_list.append(val_acc)

            if logfile is not None:
                with open(logfile, "a") as f:
                    f.write("Epoch %s: Accuracy: %s\n" % (epoch_i, val_acc))
            else:
                print("Epoch %s: Accuracy: %s" % (epoch_i, val_acc))
            self.save_weights(os.path.join(
                self._basedir, subdir,
                DNN.__WEIGHTS_FILENAME_SCHEME__ % str(epoch_i)))

    def run_network(self, input_images, batch_size=1024):
        """
        Run input through the network as it currently is. Run it in batches to
        avoid memory problems.
        :param input_images: A 4D numpy array with the shape 
        (num_images, spatial, spatial, channels)
        :param batch_size: Running in batches significantly decreases the time
        required.
        :return:
        """
        n_batches = (input_images.shape[0] // batch_size) + 1
        val_data = []
        for batch in range(n_batches):
            low = batch * batch_size
            high = min((batch + 1) * batch_size, input_images.shape[0])
            feed_dict_run = {
                self._layers[key]:
                    input_images[low:high, :, :, self._inputs[key]] for
                key in self._inputs.keys()}
            val_data.append(self._session.run(self._output_layer,
                                              feed_dict=feed_dict_run))
        out = np.concatenate(val_data)
        return out

    def save_weights(self, filename):
        """
        Saves the weights currently associated with all nodes
        :param filename:
        :return:
        """
        save_vars = {}
        for cat in self._variables.keys():
            save_vars[cat] = self._session.run(self._variables[cat])

        with open(filename, "wb") as f:
            pickle.dump(save_vars, f, pickle.HIGHEST_PROTOCOL)

    def get_weights(self):
        """
        Returns the weights
        :return:
        """
        save_vars = {}
        for cat in self._variables.keys():
            save_vars[cat] = self._session.run(self._variables[cat])
        return save_vars

    def get_image_dims(self):
        return self._input_dims

    def print_structure(self, filename):
        """
        Saves the tensorflow network structure in a human readable format.
        The output filename must be of a type supported by the PyGraphViz package
        (it detects type based on filename extension)
        :param filename:
        :return:
        """

        # Create network connectivity list
        con = []
        for entry in self._layer_params:
            n = entry["name"]
            if "input" in entry:
                i = entry["input"]
            else:
                i = None
            # If the input is a list, i.e. has multiple inputs, then split it up into
            # separate entries
            if hasattr(i, "__iter__"):
                for ii in i:
                    con.append((n, ii))
            else:
                con.append((n, i))

        # Go through the layout and identify the depth of each node
        node_layers = {}

        # Find root nodes, i.e. the node without any parent
        layer_id = 0
        root_nodes = [s[0] for s in con if s[1] is None]
        for rn in root_nodes:
            node_layers[rn] = layer_id
        prev_layer = root_nodes
        remaining_nodes = [s for s in con if s[0] not in prev_layer]

        # Identify all subsequent layers
        while len(remaining_nodes) > 0:
            layer_id += 1
            cur_layer = [s[0] for s in remaining_nodes if s[1] in prev_layer]
            for cl in cur_layer:
                node_layers[cl] = layer_id
            prev_layer = cur_layer
            remaining_nodes = [s for s in remaining_nodes if s[0] not in prev_layer]

        # Set coordinates of the nodes
        # y: based on layer
        # x: based on the number of nodes in the layer and inherited from the parent
        num_layers = max(node_layers.values())
        y_scaling = 100
        x_scaling = 200
        y_vals = {}
        x_vals = {}
        for nl in range(num_layers + 1):
            nodes = [key for key in node_layers.keys() if node_layers[key] == nl]
            nodes = [s for s in con if s[0] in nodes]
            parents = [s[1] for s in nodes]

            # Go through nodes and inherit the x of the parent. If multiple children
            # exist then stagger the x value
            for parent in set(parents):
                subnodes = [s[0] for s in nodes if s[1] == parent]
                # Staggering
                low_bound = ((len(subnodes) * -0.5) + 0.5) * x_scaling
                high_bound = -1 * low_bound
                stagger_vals = range(int(low_bound), int(high_bound) + 1, x_scaling)
                if parent is None:
                    x_base = 0
                else:
                    x_base = x_vals[parent]
                subnodes_x = [s + x_base for s in stagger_vals]
                x_vals.update({k: v for k, v in zip(subnodes, subnodes_x)})

            for node in nodes:
                y_vals[node[0]] = -1 * y_scaling * nl

        # Sanity check
        if set(x_vals.keys()) != set(y_vals.keys()):
            print("The function 'print_structure' has caused an error with "
                  "this network structure")
            # return None

        # Initialize graph and set properties
        graph = pgv.AGraph()
        graph.layout()
        for edge in con:
            if edge[1] is None:
                continue
            graph.add_edge(edge[0], edge[1])

        for node in graph.nodes():
            n = graph.get_node(node)
            n.attr["pos"] = "%f,%f)" % (float(x_vals[node]), float(y_vals[node]))
            n.attr["shape"] = "box"

        graph.draw(os.path.join(self._basedir, filename), args="-n2")

    def add_input(self, params):
        """
        Creates an input layer.
        :param params: A dictionary of parameters. Requires the key "name". 
        Optionally also takes "data_z_index". "data_z_index" indicates which 
        channels of the input images are handled by this layer. E.g. 
        data_z_index = (0, 2) means that channels 0 and 2 are handled by this 
        input layer and channel 1 by another layer. If "data_z_index" is 
        missing, then it defaults to using all input channels.
        :return: A tuple: ([new node], None)
        """
        layer_name = params["name"]
        if "data_z_index" in params.keys():
            z_indices = params["data_z_index"]
        else:
            z_indices = range(self._input_dims[2])

        try:
            z_indices_len = len(z_indices)
        except TypeError:
            z_indices_len = 1

        input_ph = tf.placeholder(
            dtype=tf.float32,
            shape=[None, self._input_dims[0], self._input_dims[1],
                   z_indices_len])
        self._inputs[layer_name] = z_indices
        self._layers[layer_name] = input_ph
        self._output_layer = input_ph

    def add_conv(self, params):
        """
        Add a convolutional layer
        :param params: A dictionary of parameters. Requires the keys ("name",
        "input", "size", "n_kernels", "stride", "padding", "weights")
        :return: A tuple: (new node, weights)
        :return: 
        """

        input_tensor = self._layers[params["input"]]
        node, weights = DNN.static_create_conv(
            input_tensor=input_tensor, layer_name=params["name"],
            size_x=params["size"][0], size_y=params["size"][1],
            num_kernels=params["n_kernels"], stride_x=params["stride"][0],
            stride_y=params["stride"][1], padding=params["padding"],
            weights=params["weights"])

        self._variables.update(weights)
        self._layers[params["name"]] = node
        self._output_layer = node

    def add_maxpool(self, params):
        """
        Create a maximum pooling layer
        :param params: A dictionary of parameters. Requires the keys ("name",
        "input", "size", "stride", "padding")
        :return: 
        """
        input_tensor = self._layers[params["input"]]
        node = DNN.static_create_maxpool(
            input_tensor=input_tensor, layer_name=params["name"],
            size_x=params["size"][0], size_y=params["size"][1],
            stride_x=params["stride"][0], stride_y=params["stride"][1],
            padding=params["padding"])

        self._layers[params["name"]] = node
        self._output_layer = node

    def add_maxpool_with_argmax(self, params):
        """
        Create a maximum pooling layer with argmax tensor
        :param params: A dictionary of parameters. Requires the keys ("name",
        "input", "size", "stride", "padding")
        :return: 
        """
        input_tensor = self._layers[params["input"]]
        node = DNN.static_create_maxpool_with_argmax(
            input_tensor=input_tensor, layer_name=params["name"],
            size_x=params["size"][0], size_y=params["size"][1],
            stride_x=params["stride"][0], stride_y=params["stride"][1],
            padding=params["padding"])

        self._layers[params["name"]] = node[0]
        self._output_layer = node[0]
        self._unpooling_indices[node[0]] = node[1]

    def add_fc(self, params):
        """
        Create a fully connected layer. Functionally, these are just 
        convolutional layers with the exact size of their input and a "VALID" 
        padding, resulting in an output with the shape (?, 1, 1, N).
         
        FC-layers are used in classification but not segmentation. When 
        applying the network, i.e. segmenting an image, the FC-functionality 
        should be replaced with a convolution. For this, the optional 'params' 
        key 'padding' can be passed to this function. If it is present, 
        padding is set to its value. If not, padding is set to "VALID", as it 
        should be for a FC operation. Consequently, the program calling the 
        DNN object should make sure to change this parameter.
        :param params: A dictionary of parameters. Requires the keys 
        ("name", "weights"). Optionally also takes the keys ("n_kernels",
        "padding").
        :return: A tuple: ([new node], weights)
        """
        input_tensor = self._layers[params["input"]]
        filter_size = tuple(input_tensor.get_shape().as_list()[1:3])

        if "n_kernels" in params.keys():
            num_kernels = params["n_kernels"]
        else:
            num_kernels = self._labels.get_shape().as_list()[1]

        if "padding" in params.keys():
            padding = params["padding"]
        else:
            padding = "VALID"

        node, weights = DNN.static_create_conv(
            input_tensor=input_tensor, layer_name=params["name"],
            size_x=filter_size[0], size_y=filter_size[1],
            num_kernels=num_kernels, stride_x=1, stride_y=1,
            padding=padding, weights=params["weights"])

        self._variables.update(weights)
        self._layers[params["name"]] = node
        self._output_layer = node

    def add_inception_v1(self, params):
        """
        Creates an inception-style module. This module has 4 branches:
        - 1) 1by1
        - 2) 1by1 + 3by3
        - 3) 1by1 + 3by3 + 3by3
        - 4) max_pool + 1by1
        
        :param params: Must have the keys ("name", "input", "n_kernels"). Note 
        that 'n_kernels' is the number of kernels of each branch, i.e. the 
        final output of the module will have n_branches * n_kernels layers
        :return: A tuple: ([new nodes], weights)
        """
        layer_name = params["name"]
        input_tensor = self._layers[params["input"]]
        num_kernels = params["n_kernels"]

        # 1by1
        sub_name = layer_name + "_1by1"
        node_b1_n1, weights_b1_n1 = DNN.static_create_conv(
            input_tensor=input_tensor, layer_name=sub_name,
            size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b1_n1)
        self._layers[sub_name] = node_b1_n1

        # 3by3
        sub_name = layer_name + "_3by3_1by1"
        node_b2_n1, weights_b2_n1 = DNN.static_create_conv(
            input_tensor=input_tensor, layer_name=sub_name,
            size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b2_n1)
        self._layers[sub_name] = node_b2_n1

        sub_name = layer_name + "_3by3_3by3"
        node_b2_n2, weights_b2_n2 = DNN.static_create_conv(
            input_tensor=node_b2_n1, layer_name=sub_name,
            size_x=3, size_y=3, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b2_n2)
        self._layers[sub_name] = node_b2_n2

        # 3by3 + 3by3
        sub_name = layer_name + "_3by3x2_1by1"
        node_b3_n1, weights_b3_n1 = DNN.static_create_conv(
            input_tensor=input_tensor, layer_name=sub_name,
            size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b3_n1)
        self._layers[sub_name] = node_b3_n1

        sub_name = layer_name + "_3by3x2_3by3a"
        node_b3_n2, weights_b3_n2 = DNN.static_create_conv(
            input_tensor=node_b3_n1, layer_name=sub_name,
            size_x=3, size_y=3, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b3_n2)
        self._layers[sub_name] = node_b3_n2

        sub_name = layer_name + "_3by3x2_3by3b"
        node_b3_n3, weights_b3_n3 = DNN.static_create_conv(
            input_tensor=node_b3_n2, layer_name=sub_name,
            size_x=3, size_y=3, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b3_n3)
        self._layers[sub_name] = node_b3_n3

        # max_pool + 1by1
        sub_name = layer_name + "_maxpool_maxpool"
        node_b4_n1 = DNN.static_create_maxpool(
            input_tensor=input_tensor, layer_name=sub_name, size_x=3,
            size_y=3, stride_x=1, stride_y=1, padding="SAME")
        self._layers[sub_name] = node_b4_n1

        sub_name = layer_name + "_maxpool_1by1"
        node_b4_n2, weights_b4_n2 = DNN.static_create_conv(
            input_tensor=node_b4_n1, layer_name=sub_name,
            size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_b4_n2)
        self._layers[sub_name] = node_b4_n2

        # Concatenating layer
        sub_name = layer_name
        node_concat = DNN.static_create_concat(
            input_tensors=(node_b1_n1, node_b2_n2, node_b3_n3, node_b4_n2),
            layer_name=sub_name)
        self._layers[sub_name] = node_concat
        self._output_layer = node_concat

    def add_inception(self, params):
        """
        Creates an inception-style module with a variable number of branches. 
        The convolutions are flattened so that a single NxN convolution 
        becomes two convolutions (1xN + Nx1)
        
        It always creates the following branches
        - 1) 1x1-conv
        - 2) max_pool + 1x1-conv
        
        It creates a custom number of branches with the structure
        - i) 1x1-conv + Nx1-conv + 1xN-conv
        
        where N is a tuple given by params['branches']. As duplicate 
        branches make no sense (this would be equivalent to increasing the 
        number of kernels), duplicated entries are removed. A 1x1 branch 
        exists by default, so that is also removed.

        :param params: Must have the keys ("name", "input", "n_kernels", 
        "branches"). Note that 'n_kernels' is the number of kernels of each 
        branch, i.e. the final output of the module will have 
        n_branches * n_kernels layers. 'branches' can be either a tuple or 
        a single integer. All values must be unique
        :return: A tuple: ([new nodes], weights)
        """
        layer_name = params["name"]
        input_tensor = self._layers[params["input"]]
        num_kernels = params["n_kernels"]
        branches = params["branches"]

        # Make 'branches' iterable if it isn't
        if not hasattr(branches, "__iter__"):
            branches = [int(branches)]
        else:
            branches = [int(s) for s in branches]

        # Adjust all branches to next higher odd number and leave only unique
        # values (1 is removed because a 1x1 branch exists by default)
        branches = set([s for s in branches if s != 1])

        # The ends of branches, for the concatenation at the end
        branch_ends = []

        # Consistent nodes
        # 1x1
        sub_name = layer_name + "_1by1"
        node_1by1, weights_1by1 = DNN.static_create_conv(
            input_tensor=input_tensor, layer_name=sub_name,
            size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_1by1)
        self._layers[sub_name] = node_1by1
        branch_ends.append(node_1by1)

        # max_pool + 1x1
        sub_name = layer_name + "_maxpool_maxpool"
        node_mp = DNN.static_create_maxpool(
            input_tensor=input_tensor, layer_name=sub_name, size_x=3,
            size_y=3, stride_x=1, stride_y=1, padding="SAME")
        self._layers[sub_name] = node_mp

        sub_name = layer_name + "_maxpool_1by1"
        node_mp_1by1, weights_mp_1by1 = DNN.static_create_conv(
            input_tensor=node_mp, layer_name=sub_name,
            size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
            stride_y=1, padding="SAME", weights=params["weights"])
        self._variables.update(weights_mp_1by1)
        self._layers[sub_name] = node_mp_1by1
        branch_ends.append(node_mp_1by1)

        # Loop through 'branches'
        for N in branches:
            sub_name = layer_name + "_%sby%s_1by1" % (N, N)
            node_n1, weights_n1 = DNN.static_create_conv(
                input_tensor=input_tensor, layer_name=sub_name,
                size_x=1, size_y=1, num_kernels=num_kernels, stride_x=1,
                stride_y=1, padding="SAME", weights=params["weights"])
            self._variables.update(weights_n1)
            self._layers[sub_name] = node_n1

            sub_name = layer_name + "_%sby%s_%sby1" % (N, N, N)
            node_n2, weights_n2 = DNN.static_create_conv(
                input_tensor=node_n1, layer_name=sub_name,
                size_x=N, size_y=1, num_kernels=num_kernels, stride_x=1,
                stride_y=1, padding="SAME", weights=params["weights"])
            self._variables.update(weights_n2)
            self._layers[sub_name] = node_n2

            sub_name = layer_name + "_%sby%s_1by%s" % (N, N, N)
            node_n3, weights_n3 = DNN.static_create_conv(
                input_tensor=node_n2, layer_name=sub_name,
                size_x=1, size_y=N, num_kernels=num_kernels, stride_x=1,
                stride_y=1, padding="SAME", weights=params["weights"])
            self._variables.update(weights_n3)
            self._layers[sub_name] = node_n3
            branch_ends.append(node_n3)

        # Concatenating layer
        sub_name = layer_name
        node_concat = DNN.static_create_concat(
            input_tensors=branch_ends, layer_name=sub_name)
        self._layers[sub_name] = node_concat
        self._output_layer = node_concat

    def add_concat(self, params):
        """
        Creates a concatenating layer of different inputs
        :param params: A dictionary of parameters. Requires the keys 
        ("name", "input"). 
        :return: A tuple: ([new node], None)
        """
        inputs = [self._layers[input_i] for input_i in params["input"]]
        layer_name = params["name"]
        node = DNN.static_create_concat(
            input_tensors=inputs, layer_name=layer_name)
        self._layers[params["name"]] = node
        self._output_layer = node

    def add_optimizer(self, params):
        """
        Adds an optimizer layer to the currently set output layer
        :param params: A dictionary of parameters. Requires the keys ("type", 
        "name"). Currently supported 'type' values are "cross_entropy" and 
        "rmse" (root mean squared error). Optionally also takes the key
        "optimizer_type", which must be a tensorflow-supported optimizer. This 
        defaults to tf.train.AdamOptimizer
        :return:
        """
        layer_name = params["name"]
        layer_type = params["type"]

        if self._cost_function_set:
            print("Cost function already set")
            return False

        # Cost functions and optimizers only make sense if this is
        # a training output, i.e. the shape is (?, 1, 1, N)
        input_tensor = self._output_layer
        if not (input_tensor.get_shape().as_list()[1] == 1
                and input_tensor.get_shape().as_list()[2] == 1):
            return False

        if layer_type == "cross_entropy":
            cost_function = tf.nn.softmax_cross_entropy_with_logits(
                logits=tf.squeeze(input_tensor, (1, 2)), labels=self._labels)
        elif layer_type == "rmse":
            cost_function = tf.nn.l2_loss(
                tf.squeeze(self._output_layer, (1, 2)) - self._labels)
        else:
            raise Exception("Unsupported cost function")

        if "optimizer_type" in params.keys():
            optimizer_func = params["optimizer_type"]
        else:
            optimizer_func = tf.train.AdamOptimizer

        self._optimizer = optimizer_func(
            learning_rate=self._learning_rate).minimize(
            loss=cost_function,
            var_list=self._variables.values(),
            name=layer_name)
        self._cost_function_set = True
        return True

    @staticmethod
    def static_create_conv(
            input_tensor, layer_name, size_x, size_y,
            num_kernels, stride_x, stride_y, padding, weights):
        """
        Creates a convolution layer.
        :param input_tensor: The input tensor of the convolution
        :param layer_name: Name of the layer
        :param size_x: Size of the convolution
        :param size_y: Size of the convolution
        :param num_kernels: Number of kernels
        :param stride_x: The step size of the convolution across the input
        :param stride_y: The step size of the convolution across the input
        :param padding: How to handle the edges of the input (must be either 
        "SAME" or "VALID")
        :param weights: A dictionary of tensorflow variables. Must be None or 
        have entries with the keys "$layer_name/w" and "$layer_name/b" 
        :return: A tuple: (Tensorflow node, dictionary of Tensorflow variables) 
        """
        weight_norm = np.prod(
            input_tensor.get_shape().as_list()[1:])
        in_channels = input_tensor.get_shape().as_list()[3]

        with tf.name_scope(layer_name):
            if weights is None:
                w = tf.Variable(
                    (2 * np.random.rand(
                        size_x, size_y, in_channels,
                        num_kernels) - 1) / np.sqrt(weight_norm),
                    dtype=tf.float32)
                b = tf.Variable(
                    (2 * np.random.rand(num_kernels) - 1) /
                    np.sqrt(weight_norm), dtype=tf.float32)
            else:
                w = tf.Variable(weights[layer_name + "/w"])
                b = tf.Variable(weights[layer_name + "/b"])
            return_weights = {layer_name + "/w": w, layer_name + "/b": b}
            conv = tf.nn.conv2d(
                input=input_tensor, filter=w,
                strides=[1, stride_x, stride_y, 1],
                padding=padding)
            conv = tf.nn.bias_add(value=conv, bias=b)
            conv = DNN.lrelu(conv)
        return conv, return_weights

    @staticmethod
    def static_create_maxpool(input_tensor, layer_name, size_x, size_y,
                              stride_x, stride_y, padding):
        """
        Create a maximum pooling layer.
        :param input_tensor: The input tensor of the pooling
        :param layer_name: Name of the layer
        :param size_x: Size of the max pool window
        :param size_y: Size of the max pool window
        :param stride_x: The step size of the convolution across the input
        :param stride_y: The step size of the convolution across the input
        :param padding: How to handle the edges of the input (must be either 
        "SAME" or "VALID")
        :return: Tensorflow node
        """
        with tf.name_scope(layer_name):
            pool_layer = tf.nn.max_pool(
                value=input_tensor, ksize=[1, size_x, size_y, 1],
                strides=[1, stride_x, stride_y, 1],
                padding=padding, name=layer_name)
        return pool_layer

    @staticmethod
    def static_create_maxpool_with_argmax(input_tensor, layer_name, size_x,
                                          size_y, stride_x, stride_y, padding):
        """
        Create a maximum pooling layer with an argmax tensor.
        :param input_tensor: The input tensor of the pooling
        :param layer_name: Name of the layer
        :param size_x: Size of the max pool window
        :param size_y: Size of the max pool window
        :param stride_x: The step size of the convolution across the input
        :param stride_y: The step size of the convolution across the input
        :param padding: How to handle the edges of the input (must be either 
        "SAME" or "VALID")
        :return: Tensorflow node
        """
        with tf.name_scope(layer_name):
            pool_layer = tf.nn.max_pool_with_argmax(
                input=input_tensor, ksize=[1, size_x, size_y, 1],
                strides=[1, stride_x, stride_y, 1],
                padding=padding, name=layer_name)
        return pool_layer

    @staticmethod
    def static_create_concat(input_tensors, layer_name):
        """
        Creates a concatenating layer of different inputs
        :param input_tensors: A list of tensorflow nodes to concatenate
        :param layer_name: The name of the concatenation
        :return: A tuple: ([new node], None)
        """
        with tf.name_scope(layer_name):
            concat_layer = tf.concat(axis=3, values=input_tensors)
        return concat_layer

    @staticmethod
    def lrelu(x, leak=0.001, name="lrelu"):
        """Leaky rectifier.

        Parameters
        ----------
        x : Tensor
            The tensor to apply the nonlinearity to.
        leak : float, optional
            Leakage parameter.
        name : str, optional
            Variable scope to use.

        Returns
        -------
        x : Tensor
            Output of the nonlinearity.
        """
        with tf.variable_scope(name):
            f1 = 0.5 * (1 + leak)
            f2 = 0.5 * (1 - leak)
            return f1 * x + f2 * abs(x)
