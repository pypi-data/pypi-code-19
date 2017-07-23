import numpy as np
import pickle


class Validator(object):
    """
    This class validates the output of a tensorflow network with ground-truth labels. If the network output isn't
    normalized, a softmax normalization is performed prior to processing.
    """

    def __init__(self, network_output, labels, image_groups, perform_softmax=True, collapse_pairs=None):
        """
        This class validates the output of a tensorflow network with ground-truth labels. If the network output isn't
        normalized, a softmax normalization is performed prior to processing.

        :param network_output: Numpy array. Output of a tensorflow network. Should have the shape
                               (num_samples, num_labels)
        :param labels: Numpy array. The ground truth of the network output being validated. Should have the shape
                       (num_samples, num_labels)
        :param image_groups: A dictionary indicating which one-hot vector belongs to which category,
                             e.g. {"Category_1": 0, "Category_2": 1, ...}
        :param perform_softmax: A boolean value indicating if the network output should be normalized
        :param collapse_pairs: A list of tuples. Pairs of categories may be considered identical and an accuracy can be
                               calculated, which takes this into account.
        """

        if len(image_groups) != labels.shape[1]:
            raise ValueError("The label vectors should have the same dimension (%s) as the number of image groups (%s)" % (labels.shape[1], len(image_groups)))

        if network_output.shape != labels.shape:
            raise ValueError("'network_output' and 'labels' must have the same shape")

        self._network_output = network_output
        self._labels = labels
        self._image_groups = image_groups

        # Perform softmax if desired
        # The softmax function is invariant against additive shifts in the input vectors, i.e.
        #     exp(x) / sum(exp(x)) == exp(x + C) / sum(exp(x + C))
        # So we shift each entry of the network output to be centered around zero, thereby minimizing any numberical
        # instabilities
        if perform_softmax:
            network_output = network_output.astype(np.float128)
            # mean_output_val = np.mean(network_output, axis=1, keepdims=True)
            max_output_val = np.max(network_output, axis=1, keepdims=True)
            self._network_output = np.exp(network_output - max_output_val) / np.sum(np.exp(network_output - max_output_val), 1, keepdims=True)

        # Determine all values
        self._top_1_acc = Validator.calc_top_1_accuracy(logits=self._network_output, labels=self._labels)
        self._cat_collapse_acc = Validator.calc_category_collapse_accuracy(logits=self._network_output, labels=self._labels, collapse_pairs=collapse_pairs)
        pr = Validator.calc_precision_recall(logits=self._network_output, labels=self._labels, categories=self._image_groups)
        self._precision = pr["precision"]
        self._recall = pr["recall"]
        self._counts = pr["counts"]
        self._thresholds = pr["thresholds"]
        loss = Validator.calc_loss(logits=self._network_output, labels=self._labels)
        self._ce_loss = loss["cross_entropy"]
        self._rmse_loss = loss["RMSE"]

    def get_top_1_acc(self):
        return self._top_1_acc

    def get_ce_loss(self):
        return self._ce_loss

    def get_rmse_loss(self):
        return self._rmse_loss

    def get_cat_collapse_acc(self):
        return self._cat_collapse_acc

    def get_precision(self):
        return self._precision

    def get_recall(self):
        return self._recall

    def get_counts(self):
        return self._counts

    def get_thresholds(self):
        return self._thresholds

    def save_results(self, filename):
        with open(filename, "wb") as f:
            val_dict = {"precision": self._precision, "recall": self._recall,
                        "counts": self._counts, "top_1_acc": self._top_1_acc,
                        "cat_collapse_acc": self._cat_collapse_acc,
                        "cross_entropy_loss": self._ce_loss,
                        "rmse_loss": self._rmse_loss}
            pickle.dump(val_dict, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def calc_top_1_accuracy(logits, labels):
        """
        Calculate the absolute, top-1 accuracy of the output
        :return:
        """
        network_output_binary = np.argmax(logits, 1)
        labels_binary = np.argmax(labels, 1)
        accuracy = 1.0 * sum(np.abs(network_output_binary - labels_binary) == 0) / len(labels_binary)
        return accuracy

    @staticmethod
    def calc_category_collapse_accuracy(logits, labels, collapse_pairs):
        """
        Some categories may be similar enough to permit confusion. This function takes a list of category pairs
        and calculates the accuracy under the assumption that the listed pairs are the same category. E.g. if
        collapse_pairs = [(1,2), (7,3)] then any samples with either a network output or a ground truth of category '2'
        are set to category '1' and all category '3' entries are considered to belong to category '7'
        :param collapse_pairs: A list of integer pairs. Entries must be less than the number of categories.
        :return:
        """

        if collapse_pairs is None:
            return None

        if logits.shape != labels.shape:
            raise ValueError("'logits' and 'labels' must have the same shape")

        if np.max(collapse_pairs) >= logits.shape[1]:
            raise ValueError("Entries in 'collapse_pairs' must be smaller than the number of categories (%s)" % logits.shape[1])

        network_output_binary = np.argmax(logits, 1)
        labels_binary = np.argmax(labels, 1)
        for pair in collapse_pairs:
            network_output_binary[network_output_binary == pair[1]] = pair[0]
            labels_binary[labels_binary == pair[1]] = pair[0]

        accuracy = 1.0 * sum(np.abs(network_output_binary - labels_binary) == 0) / len(labels_binary)
        return accuracy

    @staticmethod
    def calc_precision_recall(logits, labels, categories):
        """
        Determines precision-recall statistics based on the probability threshold used to determine the categories.
        :return:
        """

        network_output_binary = np.argmax(logits, 1)
        network_output_max_prob = np.max(logits, 1)
        labels_binary = np.argmax(labels, 1)

        # Define thresholds. The minimum is the 'relative majority', so 1/n_categories and the maximum is 1
        thresholds = np.linspace(1.0 / labels.shape[1], 1, 20)

        all_precisions = {}
        all_recalls = {}
        all_counts = {}
        for cat in categories.keys():
            value = categories[cat]
            precision = {}
            recall = {}
            counts = {}
            for t in thresholds:
                # Set all outputs with a probability lower than 't' to -1
                nob_copy = np.copy(network_output_binary)
                nob_copy[network_output_max_prob < t] = -1
                if sum(nob_copy == value) == 0:
                    precision[str(t)] = float("nan")
                else:
                    precision[str(t)] = 1.0 * sum((labels_binary == value) * (nob_copy == value)) / sum(nob_copy == value)

                if sum(labels_binary == value) == 0:
                    recall[str(t)] = float("nan")
                else:
                    recall[str(t)] = 1.0 * sum((labels_binary == value) * (nob_copy == value)) / sum(labels_binary == value)

                counts[str(t)] = sum(nob_copy == value)

            all_precisions[cat] = precision
            all_recalls[cat] = recall
            all_counts[cat] = counts

        return {"precision": all_precisions, "recall": all_recalls, "counts": all_counts, "thresholds": thresholds}

    @staticmethod
    def calc_loss(logits, labels):
        """
        Calculates the cross entropy and RMSE loss
        :param logits: 
        :param labels: 
        :return: 
        """

        ce_loss = np.mean(-1 * np.sum(np.log2(logits) * labels, axis=1))
        rmse_loss = np.sqrt(np.mean(np.square(logits - labels)[0:3, ...]))
        return {"cross_entropy": ce_loss, "RMSE": rmse_loss}
