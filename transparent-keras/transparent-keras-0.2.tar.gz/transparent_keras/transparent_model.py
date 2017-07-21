
from keras import backend as K
from keras.models import Model


class TransparentModel(object):
    """TransparentModel is a Keras model that allows observation of arbitrary
    tensors during training and testing (only with *_on_batch methods).

    Arguments
    ---------
    inputs: list or tensor
            The input(s) of this model
    outputs: list or tensor
             The output(s) of this model
    observed_tensors: list or tensor
                      Tensors that will be returned by the *_on_batch methods
                      together with the losses and metrics
    kwargs: They are forwarded to the Keras Model class
    """
    def __init__(self, inputs, outputs, observed_tensors=None, **kwargs):
        self._model = Model(
            inputs=inputs,
            outputs=outputs,
            **kwargs
        )

        # None, one or many observed tensors
        if observed_tensors is None:
            observed_tensors = []
        elif isinstance(observed_tensors, (list, tuple)):
            observed_tensors = list(observed_tensors)
        else:
            observed_tensors = [observed_tensors]
        self._observed_tensors = observed_tensors
        self._train_function = None
        self._test_function = None

    def compile(self, *args, **kwargs):
        """Delegate to the underlying Keras model but invalidate the training
        and testing functions so that they are recompiled before usage"""
        self._train_function = None
        self._test_function = None
        self._model.compile(*args, **kwargs)

    def _get_train_inputs(self):
        """Return the input tensors for training or testing (with targets and
        sample_weights)"""
        model = self._model

        inputs = []
        inputs += model._feed_inputs
        inputs += model._feed_targets
        inputs += model._feed_sample_weights
        learning_phase = K.learning_phase()
        if model.uses_learning_phase and not isinstance(learning_phase, int):
            inputs += [learning_phase]

        return inputs

    def _get_train_outputs(self):
        """Get the output tensors for training or testing (with metrics and
        observed tensors)"""
        model = self._model

        outputs = [model.total_loss]
        outputs += model.metrics_tensors
        outputs += self._observed_tensors

        return outputs

    def _get_train_updates(self):
        """Get the training updates (with backward pass)"""
        model = self._model

        updates = model.updates
        updates += model.optimizer.get_updates(
            model._collected_trainable_weights,
            model.constraints,
            model.total_loss
        )

        return updates

    def _get_test_updates(self):
        """Get the state updates required for test time (could be pseudo random
        number generator state updates for instance)"""
        model = self._model

        return model.state_updates

    def _make_train_function(self):
        # Also make the train function of the underlying model so that stuff
        # are checked and exceptions raised, also somebody may be expecting
        # compilation to happen now
        self._model._make_train_function()

        # Now we are going to compile the train function with extra outputs, it
        # is a small change from self._model._make_train_function
        if self._train_function is not None:
            return

        # Build the function
        self._train_function = K.function(
            self._get_train_inputs(),
            self._get_train_outputs(),
            updates=self._get_train_updates(),
            name="transparent_train_function",
            **self._model._function_kwargs
        )

    def _make_test_function(self):
        # Also make the test function of the underlying model so that stuff
        # are checked and exceptions raised, also somebody may be expecting
        # compilation to happen now
        self._model._make_test_function()

        # Now we are going to compile the test function with extra outputs, it
        # is a small change from self._model._make_test_function
        if self._test_function is not None:
            return

        # Build the function
        self._test_function = K.function(
            self._get_train_inputs(),
            self._get_train_outputs(),
            updates=self._get_test_updates(),
            name="transparent_test_function",
            **self._model._function_kwargs
        )

    def train_on_batch(self, x, y, sample_weight=None, class_weight=None):
        """Runs a single forward-backward pass on a single batch of data.

        Unlike its Keras counterpart it also returns any output you want
        besides metrics and total loss.

        Arguments
        ---------
        x: Everything you can pass to Keras as input, namely numpy array, list
           of numpy arrays and dictionary
        y: Everything you can pass to Keras as output, namely numpy array, list
           of numpy arrays or dictionary
        sample_weight: Optional array of the same length as x changing the
                       importance of each sample. Other types of weights (for
                       instance temporal) are also possible (see Keras docs)
        class_weight: Optional dictionary of class indices to class weights
                      changing the importance of the classes
        """
        # Run the standard Keras checks
        x, y, sample_weights = self._model._standardize_user_data(
            x, y,
            sample_weight=sample_weight,
            class_weight=class_weight,
            check_batch_axis=True
        )

        # Build the input list
        inputs = x + y + sample_weights
        if (
            self._model.uses_learning_phase and
            not isinstance(K.learning_phase(), int)
        ):
            inputs += [1.]

        # Build the training function and run it
        self._make_train_function()
        outputs = self._train_function(inputs)

        return outputs[0] if len(outputs) == 1 else outputs

    def test_on_batch(self, x, y, sample_weight=None):
        """Run a forward pass on a single batch of data.

        Unlike its Keras counterpart besides the loss and the metrics it also
        returns arbitrary output tensors.
        """
        # Run the standard Keras checks
        x, y, sample_weights = self._model._standardize_user_data(
            x, y,
            sample_weight=sample_weight,
            check_batch_axis=True
        )

        # Build the input list
        inputs = x + y + sample_weights
        if (
            self._model.uses_learning_phase and
            not isinstance(K.learning_phase(), int)
        ):
            inputs += [0.]

        # Build the test function and run it
        self._make_test_function()
        outputs = self._test_function(inputs)

        return outputs[0] if len(outputs) == 1 else outputs

    def __getattr__(self, name):
        """Forward all the methods and attributes to self._model"""
        return getattr(self._model, name)
