# coding=utf-8
from __future__ import absolute_import

import copy
import logging
from collections import defaultdict
from contextlib import contextmanager
from six import string_types

from missinglink_kernel.callback.base_callback import BaseCallback, WEIGHTS_HASH_PREFIX
from missinglink_kernel.callback.exceptions import MissingLinkException
from missinglink_kernel.callback.settings import HyperParamTypes, CUSTOM_METRICS_FORMAT
from missinglink_kernel.callback.interfaces import ModelHashInterface
from missinglink_kernel.callback.utils import hasharray, hashcombine, hash_value


class TensorFlowProject(BaseCallback):
    """A class for communicating with MissingLinkAI backend.

    A TensorFlowProject instance corresponds to a project created in the backend. This instance
    is used to create new experiments and send the data to the backend.
    """

    def __init__(self, owner_id, project_token, host=None):
        """Construct an new instance.

        # Arguments:
            owner_id: The owner's ID which can be obtained from the web dashboard
            project_token: The project's token which can be obtained from the web dashboard
            host: (Optional.) The backend endpoint
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise MissingLinkException('Please install TensorFlow library')

        super(self.__class__, self).__init__(owner_id, project_token, host=host, framework='tensorflow')

    @contextmanager
    def create_experiment(self,
                          display_name=None,
                          description=None,
                          class_mapping=None,
                          optimizer=None,
                          hyperparams=None,
                          monitored_metrics=None,
                          custom_metrics=None):
        """Create an experiment context.

        This context defines a new experiment and allows the SDK to monitor the progress of the experiment.

        ```python
            # Setup the model

            # Add the optimizer op
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
            train_op = optimizer.minimize(loss)

            project = TensorFlowProject(owner_id='owner_id', project_token='project_token')

            with project.create_experiment(
                display_name='MNIST multilayer perception',
                description='Two fully connected hidden layers',
                class_mapping={0: 'zero', 1: 'one', 2: 'two'},
                optimizer=optimizer,
                hyperparams={'batch_size': 100},
                monitored_metrics={'loss': loss},
                custom_metrics={'custom_loss': custom_loss_func}) as experiment:

                # Run the training loop
        ```

        # Arguments:
            display_name: (Optional.) The display name of the experiment
            description: (Optional.) The description of the experiment
            class_mapping: (Optional.) The class mapping of the experiment
            optimizer: (Optional.) The optimizer used to train the model. This should be an instance of
                `tf.Optimizer` or its subclasses.
            hyperparams: (Optional.) A dictionary of hyper-parameters whose keys are the parameter names. The
                values are the parameter's values.
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            An experiment context manager
        """
        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)

        if optimizer is not None:
            self._set_optimizer(optimizer)

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)

        try:
            experiment = Experiment(self,
                                    monitored_metrics=monitored_metrics,
                                    custom_metrics=custom_metrics,
                                    logger=self.logger)
            experiment._context_validator.enter(Context.EXPERIMENT)

            yield experiment

            experiment._context_validator.exit(Context.EXPERIMENT)
        except Exception as ex:
            self.logger.exception('Training has failed: %s', ex)
            raise ex

    def _set_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'AdadeltaOptimizer': ['_lr', '_rho', '_epsilon'],
            'AdagradOptimizer': ['_learning_rate', '_initial_accumulator_value'],
            'AdagradDAOptimizer': ['_learning_rate', '_initial_gradient_squared_accumulator_value',
                                   '_l1_regularization_strength', '_l2_regularization_strength'],
            'AdamOptimizer': ['_lr', '_beta1', '_beta2', '_epsilon'],
            'FtrlOptimizer': ['_learning_rate', '_learning_rate_power', '_initial_accumulator_value',
                              '_l1_regularization_strength', '_l2_regularization_strength'],
            'GradientDescentOptimizer': ['_learning_rate'],
            'MomentumOptimizer': ['_learning_rate', '_momentum', '_use_nesterov'],
            'ProximalAdagradOptimizer': ['_learning_rate', '_initial_accumulator_value',
                                         '_l1_regularization_strength', '_l2_regularization_strength'],
            'ProximalGradientDescentOptimizer': ['_learning_rate', '_l1_regularization_strength',
                                                 '_l2_regularization_strength'],
            'RMSPropOptimizer': ['_learning_rate', '_decay', '_momentum', '_epsilon']
        }
        attr_to_hyperparams = {
            '_lr': 'learning_rate',
            '_decay': 'learning_rate_decay'
        }

        for attrs in optimizer_to_attrs.values():
            for attr in attrs:
                if attr not in attr_to_hyperparams and attr.startswith('_'):
                    hyperparam = attr[1:]
                    attr_to_hyperparams[attr] = hyperparam

        self.set_hyperparams(optimizer_algorithm=optimizer.get_name())
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_to_attrs, attr_to_hyperparams)


_TF_SESSION_RUN = None


class Experiment(ModelHashInterface):
    """Context manager for an experiment."""

    def __init__(self, project, monitored_metrics=None, custom_metrics=None, logger=None):
        """Create the context manager for an experiment.

        This context manager should be created by a TensorFlowProject instance. Please see
        `TensorFlowProject.create_experiment()` for details.
        """
        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        self.callback = project
        self.logger = logger or logging.getLogger(__name__)
        self._monitored_fetches = monitored_metrics or {}
        self._custom_metrics = custom_metrics or {}
        self._context_validator = ContextValidator(self.logger)
        self._max_iterations = None
        self._epoch_size = None
        self._has_started = False
        self._iteration = 0
        self._epochs = None
        self._epoch = 0
        self._train_session = None
        self._latest_metrics = None
        self._validation_metrics = []
        self._should_keep_iteration = False  # is used to protect points with validation data

    def loop(self, max_iterations=None, condition=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```

        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition`
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run. Cannot be provided together with `max_iterations`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index
        """
        if max_iterations and condition:
            raise MissingLinkException('Cannot provide both max_iteration and condition.')

        if not max_iterations and not condition:
            self.logger.error('Provide max_iteration or condition')
            raise MissingLinkException('Provide max_iteration or condition.')

        self._context_validator.enter(Context.LOOP)

        self._epoch_size = epoch_size
        self.callback.set_hyperparams(max_iterations=max_iterations, epoch_size=epoch_size,
                                      total_epochs=self._total_epochs(max_iterations, epoch_size))

        if max_iterations:
            self._max_iterations = max_iterations

            def condition(step):
                return step < max_iterations

        i = 0
        should_increment_epoch = True
        while condition(i):
            self._iteration += 1
            if should_increment_epoch:
                self._epoch += 1
                should_increment_epoch = False
            self._should_keep_iteration = False
            yield i

            self.callback.batch_end(self._iteration, self._epoch, self._latest_metrics,
                                    iteration=self._iteration, is_test=self._should_keep_iteration)
            if self._is_epoch_iteration:
                weights_hash = self.get_weights_hash(self._train_session)
                self.callback.epoch_end(self._epoch, self._latest_metrics, weights_hash=weights_hash)
                should_increment_epoch = True

            i += 1

        self.callback._train_end(iterations=self._iteration, metricData=self._latest_metrics)
        self._context_validator.exit(Context.LOOP)

    def epoch_loop(self, epochs):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        # Arguments:
            epochs: The total number of epochs
        # Yields:
            A 0-based index
        """
        self._context_validator.enter(Context.EPOCH_LOOP)

        self._epochs = epochs
        self.callback.set_hyperparams(total_epochs=epochs)

        for epoch in range(epochs):
            self._epoch += 1

            yield epoch

            self.callback.batch_end(self._iteration, self._epoch, self._latest_metrics,
                                    iteration=self._iteration, is_test=self._should_keep_iteration)
            weights_hash = self.get_weights_hash(self._train_session)
            self.callback.epoch_end(self._epoch, self._latest_metrics, weights_hash=weights_hash)

        self.callback._train_end(iterations=self._iteration, metricData=self._latest_metrics)
        self._context_validator.exit(Context.EPOCH_LOOP)

    def batch_loop(self, batches):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        # Arguments:
            batches: The total number of batches
        # Yields:
            A 0-based index
        """
        self._context_validator.enter(Context.BATCH_LOOP)

        self.callback.set_hyperparams(epoch_size=batches, max_iterations=self._epochs * batches)

        for batch in range(batches):
            self._should_keep_iteration = False
            self._iteration += 1

            yield batch

            if batch < batches - 1:
                # Last batch's batch_end will be call in `epoch_loop`
                self.callback.batch_end(self._iteration, self._epoch, self._latest_metrics,
                                        iteration=self._iteration, is_test=self._should_keep_iteration)

        self._context_validator.exit(Context.BATCH_LOOP)

    @contextmanager
    def train(self, monitored_metrics=None, custom_metrics=None):
        """Marks a training context.

        This context allows the SDK to patch the `tf.Session.run` and calculate training metrics if needed.
        As such, there must be only 1 `tf.Session.run` call within this context. Otherwise, the training
        iteration might be incorrectly incremented.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        self._context_validator.enter(Context.TRAIN)

        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        monitored_fetches = monitored_metrics or {}
        monitored_fetches.update(self._monitored_fetches)
        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        self._patch_tf_session_for_train(monitored_fetches, custom_metrics)
        yield
        self._reset_tf_session()

        self._context_validator.exit(Context.TRAIN)

    @contextmanager
    def validation(self, monitored_metrics=None, custom_metrics=None):
        """Marks a validation context.

        This context allows the SDK to patch the `tf.Session.run` to calculate validation metrics.
        Unlike the `train` scope, you can include multiple runs e.g. by using a for-loop looping over a
        validation dataset by batches. The SDK will average out the validation metrics across these runs
        and collect the averaged value.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        self._context_validator.enter(Context.VALIDATION)

        # Validate but do not throw exceptions so the experiment is not suddenly interrupted.
        self._validate_monitored_fetches(monitored_metrics, raise_exception=False)
        self._validate_custom_metrics(custom_metrics, raise_exception=False)

        monitored_fetches = monitored_metrics or {}
        monitored_fetches.update(self._monitored_fetches)
        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        self._patch_tf_session_for_validation(monitored_fetches, custom_metrics)
        yield
        self._on_validation_end()
        self._reset_tf_session()
        self._should_keep_iteration = True

        self._context_validator.exit(Context.VALIDATION)

    @property
    def _is_epoch_iteration(self):
        if self._epoch_size is None:
            return False

        return self._iteration % self._epoch_size == 0

    def _patch_tf_session_for_validation(self, monitored_fetches, custom_metrics):
        def patched_run(session, fetches, feed_dict=None, options=None, run_metadata=None):
            monitored_results, unmonitored_results = self._internal_session_run(
                monitored_fetches, custom_metrics, session, fetches, feed_dict=feed_dict, options=options,
                run_metadata=run_metadata)
            validation_results = self._prepare_validation_metric_data(monitored_results)
            self._validation_metrics.append(validation_results)
            return unmonitored_results

        import tensorflow as tf
        global _TF_SESSION_RUN
        _TF_SESSION_RUN = tf.Session.run
        tf.Session.run = patched_run

    @classmethod
    def _prepare_validation_metric_data(cls, validation_metric_data):
        metric_data = {}
        for key, value in validation_metric_data.items():
            if not key.startswith('val_'):
                metric_data['val_' + key] = value
            else:
                metric_data[key] = value

        return metric_data

    def _patch_tf_session_for_train(self, monitored_fetches, custom_metrics):
        def patched_run(session, fetches, feed_dict=None, options=None, run_metadata=None):
            self._train_session = session
            self._before_train_run(session)
            monitored_results, unmonitored_results = self._internal_session_run(
                monitored_fetches, custom_metrics, session, fetches, feed_dict=feed_dict, options=options,
                run_metadata=run_metadata)
            self._latest_metrics = monitored_results
            return unmonitored_results

        import tensorflow as tf
        global _TF_SESSION_RUN
        _TF_SESSION_RUN = tf.Session.run
        tf.Session.run = patched_run

    def _internal_session_run(self, monitored_fetches, custom_metrics, session, fetches, feed_dict=None, options=None,
                              run_metadata=None):
        all_fetches = copy.copy(monitored_fetches)

        key_for_unmonitored_fetches = self._generate_unique_key(all_fetches.keys())
        all_fetches[key_for_unmonitored_fetches] = fetches

        monitored_results = _TF_SESSION_RUN(session, all_fetches, feed_dict, options, run_metadata)
        unmonitored_results = monitored_results.pop(key_for_unmonitored_fetches)

        for key, metrics_function in custom_metrics.items():
            monitored_results[CUSTOM_METRICS_FORMAT.format(key)] = metrics_function()

        return monitored_results, unmonitored_results

    def _average_validation_metrics(self):
        result = defaultdict(float)
        total = len(self._validation_metrics)
        for el in self._validation_metrics:
            for k, v in el.items():
                result[k] += v
        result = {k: v * 1.0 / total for k, v in result.items()}
        return result

    def _on_validation_end(self):
        averaged = self._average_validation_metrics()
        self._latest_metrics.update(averaged)
        self.logger.debug('Added validation metrics on iteration %s. Metrics are %s', self._iteration,
                          self._latest_metrics)
        self._validation_metrics = []

    def _before_train_run(self, session):
        if not self._has_started:
            self._has_started = True
            structure_hash = self._get_structure_hash(session)
            self.callback.train_begin(structure_hash=structure_hash)

    @staticmethod
    def _reset_tf_session():
        global _TF_SESSION_RUN

        if not _TF_SESSION_RUN:
            return

        import tensorflow as tf
        tf.Session.run = _TF_SESSION_RUN
        _TF_SESSION_RUN = None

    @staticmethod
    def _validate_fetches_dict(fetches_dict):
        if fetches_dict is None:
            return

        if not isinstance(fetches_dict, dict):
            raise ValueError('Fetches %s must be a dictionary.' % fetches_dict)

        import tensorflow as tf
        default_graph = tf.get_default_graph()

        for name, fetch in fetches_dict.items():
            if not isinstance(name, string_types):
                raise ValueError("monitored metrics key %s is not a string" % name)

            try:
                default_graph.as_graph_element(fetch, allow_tensor=True, allow_operation=False)
            except TypeError as e:
                raise TypeError('Fetch %r has invalid type %r, must be a string or Tensor. (%s)'
                                % (fetch, type(fetch), str(e)))
            except ValueError as e:
                raise ValueError('Fetch %r cannot be interpreted as a Tensor. (%s)' % (fetch, str(e)))
            except KeyError as e:
                raise ValueError('Fetch %r cannot be found in the default graph. (%s)' % (fetch, str(e)))

    def _validate_monitored_fetches(self, monitored_fetches, raise_exception=True):
        try:
            self._validate_fetches_dict(monitored_fetches)
        except Exception as ex:
            self.logger.warning(ex)
            if raise_exception:
                raise ex

    @staticmethod
    def _validate_custom_metrics_dict(custom_metrics):
        if custom_metrics is None:
            return

        if not isinstance(custom_metrics, dict):
            raise ValueError('Custom metrics %s must be a dictionary.' % custom_metrics)

        for name, metric_func in custom_metrics.items():
            if not isinstance(name, string_types):
                raise ValueError("Custom metric's key %s is not a string" % name)

            if not callable(metric_func):
                raise ValueError('Custom metric function of %s must be callable' % name)

    def _validate_custom_metrics(self, custom_metrics, raise_exception=True):
        try:
            self._validate_custom_metrics_dict(custom_metrics)
        except Exception as ex:
            self.logger.warning(ex)
            if raise_exception:
                raise ex

    @staticmethod
    def _generate_unique_key(existing_keys):
        while True:
            key = BaseCallback.generate_tag()
            if key not in existing_keys:
                return key

    @staticmethod
    def _total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

    # region - ModelHashInterface

    @classmethod
    def calculate_weights_hash(cls, session):
        weights = cls._get_weights(session)

        weights_hashes = []
        for weight in weights:
            weight_hash = hasharray(weight)
            weights_hashes.append(weight_hash)

        hash_key = hashcombine(*weights_hashes)
        return WEIGHTS_HASH_PREFIX + hash_key

    @classmethod
    def _get_weights(cls, session):
        import tensorflow as tf
        global _TF_SESSION_RUN

        variables = tf.trainable_variables()

        if _TF_SESSION_RUN:
            # `tf.Session.run` is being patched. Use the original method to
            # avoid possible infinite recursion caused by the patched method.
            return _TF_SESSION_RUN(session, variables)

        return session.run(variables)

    def get_weights_hash(self, session):
        return self.calculate_weights_hash(session)

    def _get_structure_hash(self, session):
        import tensorflow as tf
        variables = tf.trainable_variables()
        shapes = tuple([tuple(x.get_shape().as_list()) for x in variables])
        return hash_value(shapes)

    # endregion


class Context(object):
    EXPERIMENT = 'experiment'
    LOOP = 'loop'
    EPOCH_LOOP = 'epoch_loop'
    BATCH_LOOP = 'batch_loop'
    TRAIN = 'train'
    VALIDATION = 'validation'


class ContextValidator(object):
    """This class validates if we can enter or exit a context.
    """
    def __init__(self, logger):
        self._contexts = []
        self._logger = logger

    def enter(self, context):
        if context == Context.EXPERIMENT:
            self._validate_experiment_context()
        elif context == Context.LOOP:
            self._validate_loop_context()
        elif context == Context.EPOCH_LOOP:
            self._validate_epoch_loop_context()
        elif context == Context.BATCH_LOOP:
            self._validate_batch_loop_context()
        elif context == Context.TRAIN:
            self._validate_train_context()
        elif context == Context.VALIDATION:
            self._validate_validation_context()
        else:
            # This should never happen unless we mess up
            raise MissingLinkException('Unknown scope %s' % context)

        self._contexts.append(context)

    def exit(self, context):
        last_context = self._contexts.pop()

        if last_context != context:
            # This should never happen unless we mess up
            raise MissingLinkException('Cannot exit %s scope because the current scope is %s' % (context, last_context))

    @property
    def _last_context(self):
        return self._contexts[len(self._contexts) - 1]

    def _validate_experiment_context(self):
        if self._contexts:
            raise MissingLinkException('Experiment context must be outermost')

    def _validate_loop_context(self):
        if not self._contexts or self._last_context != Context.EXPERIMENT:
            raise MissingLinkException('`loop` must be nested immediately in an `experiment` context.')

    def _validate_epoch_loop_context(self):
        if not self._contexts or self._last_context != Context.EXPERIMENT:
            raise MissingLinkException('`epoch_loop` must be nested immediately in an `experiment` context.')

    def _validate_batch_loop_context(self):
        if not self._contexts or self._last_context != Context.EPOCH_LOOP:
            raise MissingLinkException('`batch_loop` must be nested immediately in an `epoch_loop` generator.')

    def _validate_train_context(self):
        if not self._contexts or self._last_context not in [Context.LOOP, Context.BATCH_LOOP]:
            raise MissingLinkException('`train` context must be nested immediately in an `loop` '
                                       'or `batch_loop` generator.')

    def _validate_validation_context(self):
        if not self._contexts or self._last_context not in [Context.LOOP, Context.EPOCH_LOOP, Context.BATCH_LOOP]:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error('`validation` context must be nested immediately in a `loop` '
                               'or `epoch_loop` or `batch_loop` generator. This context is ignored')
