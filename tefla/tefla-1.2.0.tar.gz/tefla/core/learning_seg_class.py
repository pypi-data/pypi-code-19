# -------------------------------------------------------------------#
# Written by Mrinal Haloi
# Contact: mrinal.haloi11@gmail.com
# Copyright 2016, Mrinal Haloi
# -------------------------------------------------------------------#
from __future__ import division, print_function, absolute_import

import os
import time
import cv2

import numpy as np
import tensorflow as tf
from tensorflow.python.ops import control_flow_ops

from . import logger as log
from . import summary as summary
from ..dataset.pascal_voc import PascalVoc
from .base import Base
from ..utils import util


TRAINING_BATCH_SUMMARIES = 'training_batch_summaries'
TRAINING_EPOCH_SUMMARIES = 'training_epoch_summaries'
VALIDATION_BATCH_SUMMARIES = 'validation_batch_summaries'
VALIDATION_EPOCH_SUMMARIES = 'validation_epoch_summaries'


class SegClfLearner(Base):
    """
    Semi Supervised Trainer


    Args:
        model: model definition
        cnf: dict, training configs
        training_iterator: iterator to use for training data access, processing and augmentations
        validation_iterator: iterator to use for validation data access, processing and augmentations
        start_epoch: int, training start epoch; for resuming training provide the last
        epoch number to resume training from, its a required parameter for training data balancing
        resume_lr: float, learning rate to use for new training
        classification: bool, classificattion or regression
        clip_norm: bool, to clip gradient using gradient norm, stabilizes the training
        n_iters_per_epoch: int,  number of iteratiosn for each epoch;
            e.g: total_training_samples/batch_size
        gpu_memory_fraction: amount of gpu memory to use
        is_summary: bool, to write summary or not
    """

    def __init__(self, model, cnf, clip_by_global_norm=True, **kwargs):
        self.clip_by_global_norm = clip_by_global_norm
        super(SefClfLearner, self).__init__(model, cnf, **kwargs)

    def fit(self, data_set, num_classes=6, weights_from=None, start_epoch=1, summary_every=199, model_name='multiclass_ss', weights_dir='weights'):
        """
        Train the model on the specified dataset

        Args:
            data_set: dataset instance to use to access data for training/validation
            weights_from: str, if not None, initializes model from exisiting weights
            start_epoch: int,  epoch number to start training from
                e.g. for retarining set the epoch number you want to resume training from
            summary_every: int, epoch interval to write summary; higher value means lower frequency
                of summary writing
        """
        with tf.Graph().as_default(), tf.device('/gpu:0'):
            self._data_ops(
                data_set, standardizer=self.cnf.get('standardizertf'))
            self._setup_model_loss(num_classes=num_classes)
            if self.is_summary:
                self._setup_summaries(self.capped_c_grads, self.capped_s_grads)
            self._setup_misc()
            self._print_info(data_set)
            self._train_seg_clg(
                data_set, start_epoch, weights_from, summary_every, model_name, weights_dir)

    def _data_ops(self, data_dir, data_dir_val=None, standardizer=None, dataset_name='datarandom'):
        self.data_voc = PascalVoc(name='pascal_voc', data_dir=data_dir, standardizer=standardizer, is_label_filename=True, is_train=True, batch_size=1,
                                  extension='.jpg', capacity=2048, min_queue_examples=512, num_preprocess_threads=4)
        if data_dir_val is None:
            self.data_voc_val = None

    def _train_seg_clf(self, dataset, start_epoch, weights_from, summary_every, model_name, weights_dir):
        training_X, training_y, validation_X, validation_y = \
            dataset.training_X, dataset.training_y, dataset.validation_X, dataset.validation_y
        if not os.path.exists(weights_dir):
            os.mkdir(weights_dir)
        if not os.path.exists(weights_dir + '/best_models'):
            os.mkdir(weights_dir + '/best_models')

        # Create a saver.
        saver = tf.train.Saver(max_to_keep=None)
        if not os.path.exists(weights_dir):
            os.mkdir(weights_dir)
        if self.is_summary:
            training_batch_summary_op = tf.merge_all_summaries(
                key=TRAINING_BATCH_SUMMARIES)
            training_epoch_summary_op = tf.merge_all_summaries(
                key=TRAINING_EPOCH_SUMMARIES)
            validation_batch_summary_op = tf.merge_all_summaries(
                key=VALIDATION_BATCH_SUMMARIES)
            validation_epoch_summary_op = tf.merge_all_summaries(
                key=VALIDATION_EPOCH_SUMMARIES)

        # Build an initialization operation to run below.
        init = tf.global_variables_initializer()

        gpu_options = tf.GPUOptions(
            per_process_gpu_memory_fraction=self.cnf.get('gpu_memory_fraction', 0.9))
        sess = tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True, gpu_options=gpu_options))
        sess.run(init)
        if start_epoch > 1:
            weights_from = "weights/model-epoch-%d.ckpt" % (
                start_epoch - 1)

        if weights_from:
            _load_variables(sess, saver, weights_from)
            # self._load_weights(sess, weights_from)

        learning_rate_value = self.lr_policy.initial_lr
        log.info("Initial learning rate: %f " % learning_rate_value)
        if self.is_summary:
            train_writer, validation_writer = summary.create_summary_writer(
                self.cnf.get('summary_dir', '/tmp/tefla-summary'), sess)
        # keep track of maximum accuracy and auroc and save corresponding
        # weights
        training_history = []
        seed_delta = 100
        batch_iter_idx = 1
        n_iters_per_epoch = len(
            dataset.training_X) // self.training_iterator.batch_size
        self.lr_policy.n_iters_per_epoch = n_iters_per_epoch
        for epoch in xrange(start_epoch, self.cnf.get('mum_epochs', 550) + 1):
            np.random.seed(epoch + seed_delta)
            tf.set_random_seed(epoch + seed_delta)
            tic = time.time()
            c_train_losses = []
            s_train_losses = []
            batch_train_sizes = []
            for batch_num, (Xb, yb) in enumerate(self.training_iterator(training_X, training_y)):
                if Xb.shape[0] < self.cnf['batch_size_train']:
                    continue
                feed_dict_train = {self.inputs: Xb,
                                   self.labels: yb, self.learning_rate_c: learning_rate_value, self.learning_rate_s: learning_rate_value}
                log.debug('1. Loading batch %d data done.' % batch_num)
                if epoch % summary_every == 0 and self.is_summary:
                    log.debug('2. Running training steps with summary...')
                    _, _c_loss_, summary_str_train = sess.run(
                        [self.train_op_c, self.clf_loss, training_batch_summary_op], feed_dict=feed_dict_train)
                    _, _s_loss = sess.run(
                        [self.train_op_s, self.seg_loss], feed_dict=feed_dict_train)
                    train_writer.add_summary(summary_str_train, epoch)
                    train_writer.flush()
                    log.debug(
                        '2. Running training steps with summary done.')
                    log.debug("Epoch %d, CLf_loss: %s, Seg_loss: %s" %
                              (epoch, _c_loss, _s_loss))
                else:
                    log.debug(
                        '2. Running training steps without summary...')
                    _, _c_loss_ = sess.run(
                        [self.train_op_c, self.clf_loss], feed_dict=feed_dict_train)
                    _, _s_loss = sess.run(
                        [self.train_op_s, self.seg_loss], feed_dict=feed_dict_train)
                    log.debug(
                        '2. Running training steps without summary done.')

                c_train_losses.append(_c_loss)
                s_train_losses.append(_s_loss)
                batch_train_sizes.append(len(Xb))
                learning_rate_value = self.lr_policy.batch_update(
                    learning_rate_value, batch_iter_idx)
                batch_iter_idx += 1
                log.debug('4. Training batch %d done.' % batch_num)
            c_avg_loss = np.average(
                c_train_losses, weights=batch_train_sizes)
            s_avg_loss = np.average(
                s_train_losses, weights=batch_train_sizes)
            log.info("Epoch %d, Clf_avg_loss: %s, Seg_avg_loss %s" %
                     (epoch, c_avg_loss, s_avg_loss))
            # Plot training loss every epoch
            log.debug('5. Writing epoch summary...')
            if self.is_summary:
                summary_str_train = sess.run(training_epoch_summary_op, feed_dict={
                                             self.epoch_loss: d_avg_loss, self.epoch_loss_g: g_avg_loss, self.learning_rate_d: learning_rate_value, self.learning_rate_g: learning_rate_value})
                train_writer.add_summary(summary_str_train, epoch)
                train_writer.flush()
            log.debug('5. Writing epoch summary done.')
            # Validation prediction and metrics
            validation_losses = []
            batch_validation_metrics = [[]
                                        for _, _ in self.validation_metrics_def]
            epoch_validation_metrics = []
            batch_validation_sizes = []
            for batch_num, (validation_Xb, validation_y_true) in enumerate(self.validation_iterator(validation_X, validation_y)):
                feed_dict_val = {self.inputs: validation_Xb,
                                 self.labels: validation_y_true}
                log.debug(
                    '6. Loading batch %d validation data done.' % batch_num)
                if (epoch - 1) % summary_every == 0 and self.is_summary:
                    log.debug(
                        '7. Running validation steps with summary...')
                    validation_y_pred, _val_loss, summary_str_validation = sess.run(
                        [self.predictions, self.clf_loss_val, validation_batch_summary_op], feed_dict=feed_dict_val)

                    validation_writer.add_summary(
                        summary_str_validation, epoch)
                    validation_writer.flush()
                    log.debug(
                        '7. Running validation steps with summary done.')
                    log.debug(
                        "Epoch %d, Batch %d validation loss: %s" % (epoch, batch_num, _val_loss))
                    log.debug("Epoch %d, Batch %d validation predictions: %s" % (
                        epoch, batch_num, validation_y_pred))
                else:
                    log.debug(
                        '7. Running validation steps without summary...')
                    validation_y_pred, _val_loss = sess.run(
                        [self.predictions, self.clf_loss_val], feed_dict=feed_dict_val)

                    log.debug(
                        '7. Running validation steps without summary done.')
                validation_losses.append(_val_loss)
                batch_validation_sizes.append(len(validation_Xb))
                for i, (_, metric_function) in enumerate(self.validation_metrics_def):
                    metric_score = metric_function(
                        validation_y_true, validation_y_pred)
                    batch_validation_metrics[i].append(metric_score)
                log.debug('8. Validation batch %d done' % batch_num)

            epoch_validation_loss = np.average(
                validation_losses, weights=batch_validation_sizes)
            for i, (_, _) in enumerate(self.validation_metrics_def):
                epoch_validation_metrics.append(
                    np.average(batch_validation_metrics[i], weights=batch_validation_sizes))
            log.debug('9. Writing epoch validation summary...')
            if self.is_summary:
                summary_str_validate = sess.run(validation_epoch_summary_op, feed_dict={
                                                self.epoch_loss: epoch_validation_loss, self.validation_metric_placeholders: epoch_validation_metrics})
                validation_writer.add_summary(summary_str_validate, epoch)
                validation_writer.flush()
            log.debug('9. Writing epoch validation summary done.')

            custom_metrics_string = [', %s: %.3f' % (name, epoch_validation_metrics[i]) for i, (name, _) in
                                     enumerate(self.validation_metrics_def)]
            custom_metrics_string = ''.join(custom_metrics_string)

            log.info(
                "Epoch %d [(%s, %s) images, %6.1fs]: t-loss: %.3f, v-loss: %.3f%s" %
                (epoch, np.sum(batch_train_sizes), np.sum(batch_validation_sizes), time.time() - tic,
                 d_avg_loss,
                 epoch_validation_loss,
                 custom_metrics_string)
            )
            print(
                "Epoch %d [(%s, %s) images, %6.1fs]: t-loss: %.3f, v-loss: %.3f%s" %
                (epoch, np.sum(batch_train_sizes), np.sum(batch_validation_sizes), time.time() - tic,
                 d_avg_loss,
                 epoch_validation_loss,
                 custom_metrics_string)
            )
            epoch_info = dict(
                epoch=epoch,
                training_loss=d_avg_loss,
                validation_loss=epoch_validation_loss
            )

            training_history.append(epoch_info)
            saver.save(sess, "%s/model-epoch-%d.ckpt" % (weights_dir, epoch))

            learning_rate_value = self.lr_policy.epoch_update(
                learning_rate_value, training_history)
            end_points_G_val = self.model.generator(
                [self.cnf['batch_size_test'], 100], False, True, batch_size=self.cnf['batch_size_test'])

            util.save_images('generated_images.jpg',
                             sess.run(end_points_G_val['softmax']), width=128, height=128)

            G = sess.run(end_points_G_val['softmax'])
            cv2.imwrite('generated_image.jpg', G[0, :, :, :] * 50 + 128)

            # Learning rate step decay
        if self.is_summary:
            train_writer.close()
            validation_writer.close()

    def _tower_loss_clf_seg(self, images, labels, gpu_idx=0, num_classes=11, is_training=True):
        with tf.variable_scope("train_specific"):
            avg_error_rate = tf.get_variable(
                'avg_error_rate', [], initializer=tf.constant_initializer(0.), trainable=False)
            num_error_rate = tf.get_variable(
                'num_error_rate', [], initializer=tf.constant_initializer(0.), trainable=False)

        batch_size_train = self.cnf['batch_size_train']
        batch_size_val = self.cnf['batch_size_test']

        joint = tf.concat([self.inputs, images], 0)
        print(joint.get_shape())
        self.end_points = self.model(
            joint, True, None, num_classes=num_classes, batch_size=batch_size_train)
        self.end_points_val = self.model(
            joint, False, True, num_classes=num_classes, batch_size=batch_size_train)

        # For printing layers shape
        self.training_end_points = self.end_points

        self.clf_loss = _loss_softmax(
            self.end_points['clf_logits'], self.labels, is_training)
        self.seg_loss = _loss_softmax(
            self.end_points['seg_logits'], labels, is_training)
        self.clf_loss_val = _loss_softmax(
            self.end_points_val['clf_logits'], self.labels, False)
        self.predictions = self.end_points_val['clf_predictions']

    def _loss_softmax(self, logits, labels, is_training):
        log.info('Using softmax loss')
        labels = tf.cast(labels, tf.int64)
        ce_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=labels, logits=logits, name='cross_entropy_loss')
        ce_loss_mean = tf.reduce_mean(ce_loss, name='cross_entropy')
        if is_training:
            tf.add_to_collection('losses', ce_loss_mean)

            l2_loss = tf.add_n(tf.get_collection(
                tf.GraphKeys.REGULARIZATION_LOSSES))
            l2_loss = l2_loss * self.cnf.get('l2_reg', 0.0)
            tf.add_to_collection('losses', l2_loss)

            return tf.add_n(tf.get_collection('losses'), name='total_loss')
        else:
            return ce_loss_mean

    def _get_vars_clf_seg(self):
        t_vars = tf.trainable_variables()
        c_vars = [var for var in t_vars if var.name.startswith('c_')]
        s_vars = [var for var in t_vars if var.name.startswith('s_')]
        for x in c_vars:
            assert x not in s_vars
        for x in s_vars:
            assert x not in c_vars
        for x in t_vars:
            assert x in c_vars or x in s_vars

        return {'c_vars': c_vars, 's_vars': s_vars}

    def _setup_model_loss(self, update_ops=None, num_classes=6):
        self.learning_rate_c = tf.placeholder(
            tf.float32, shape=[], name="learning_rate_placeholder")
        self.learning_rate_s = tf.placeholder(
            tf.float32, shape=[], name="learning_rate_placeholder")

        c_optimizer = self._optimizer(self.learning_rate_c, optname=self.cnf.get(
            'optname', 'momentum'), **self.cnf.get('opt_kwargs', {'decay': 0.9}))
        s_optimizer = self._optimizer(self.learning_rate_s, optname=self.cnf.get(
            'optname', 'momentum'), **self.cnf.get('opt_kwargs', {'decay': 0.9}))
        # Get images and labels for ImageNet and split the batch across GPUs.
        assert self.cnf['batch_size_train'] % self.cnf.get(
            'num_gpus', 1) == 0, ('Batch size must be divisible by number of GPUs')

        self.inputs = tf.placeholder(tf.float32, shape=(
            None, self.model.image_size[0], self.model.image_size[0], 3), name="input")
        self.labels = tf.placeholder(tf.int32, shape=(None,))
        images, labels = self.data_voc.get_batch(batch_size=self.cnf['batch_size_train'], height=self.cnf.get('im_height', 256), width=self.cnf.get(
            'im_width', 256), output_height=self.cnf.get('output_height', 224), output_width=self.cnf.get('output_width', 224))
        labels = tf.reshape(labels, shape=(-1,))

        self._tower_loss_clf_seg(
            images, labels, num_classes=num_classes, is_training=is_training)

        # global_update_ops = set(tf.get_collection(tf.GraphKeys.UPDATE_OPS))
        global_update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        if update_ops is None:
            update_ops = global_update_ops
        else:
            update_ops = set(update_ops)
        # Make sure update_ops are computed before total_loss.
        if update_ops:
            with tf.control_dependencies(update_ops):
                barrier = tf.no_op(name='update_barrier')
                self.clf_loss = control_flow_ops.with_dependencies(
                    [barrier], self.clf_loss)
                self.seg_loss = control_flow_ops.with_dependencies(
                    [barrier], self.seg_loss)
        t_vars = self._get_vars_clf_seg()
        if self.clip_by_global_norm:
            self.capped_c_grads = self._clip_grad_global_norms(
                t_vars['c_vars'], self.clf_loss, c_optimizer, gradient_noise_scale=0.0)
            self.capped_s_grads = self._clip_grad_global_norms(
                t_vars['s_vars'], self.seg_loss, s_optimizer, gradient_noise_scale=0.0)
        else:
            self.capped_c_grads = c_optimizer.compute_gradients(
                self.clf_loss, t_vars['c_vars'])
            self.capped_s_grads = s_optimizer.compute_gradients(
                self.seg_loss, t_vars['s_vars'])
        global_step = tf.get_variable(
            'global_step', [], initializer=tf.constant_initializer(0), trainable=False)
        if self.gradient_multipliers is not None:
            with tf.name_scope('multiply_grads'):
                self.capped_d_grads = self._multiply_gradients(
                    self.capped_d_grads, self.gradient_multipliers)
        apply_c_gradient_op = c_optimizer.apply_gradients(
            self.capped_c_grads, global_step=global_step)
        apply_s_gradient_op = s_optimizer.apply_gradients(
            self.capped_s_grads, global_step=global_step)
        self.train_op_c = control_flow_ops.with_dependencies(
            [apply_c_gradient_op], self.clf_loss)
        self.train_op_s = control_flow_ops.with_dependencies(
            [apply_s_gradient_op], self.seg_loss)


def _load_variables(sess, saver, weights_from):
    print("---Loading session/weights from %s..." % weights_from)
    try:
        saver.restore(sess, weights_from)
    except Exception as e:
        log.info(
            "Unable to restore entire session from checkpoint. Error: %s." % e.message)
        log.info("Doing selective restore.")
        try:
            reader = tf.train.NewCheckpointReader(weights_from)
            names_to_restore = set(reader.get_variable_to_shape_map().keys())
            variables_to_restore = [v for v in tf.global_variables() if v.name[
                :-2] in names_to_restore]
            log.info("Loading %d variables: " % len(variables_to_restore))
            for var in variables_to_restore:
                logger.info("Loading: %s %s)" % (var.name, var.get_shape()))
                restorer = tf.train.Saver([var])
                try:
                    restorer.restore(sess, weights_from)
                except Exception as e:
                    logger.info("Problem loading: %s -- %s" %
                                (var.name, e.message))
                    continue
            log.info("Loaded session/weights from %s" % weights_from)
        except Exception:
            log.info(
                "Couldn't load session/weights from %s; starting from scratch" % weights_from)
            sess.run(tf.global_variables_initilizer())
