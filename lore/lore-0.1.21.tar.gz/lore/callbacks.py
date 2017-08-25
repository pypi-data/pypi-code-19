import logging
from datetime import datetime

import keras.callbacks
from sklearn.metrics import mean_absolute_error

from lore.util import timer


logger = logging.getLogger(__name__)


class ReloadBest(keras.callbacks.ModelCheckpoint):
    def __init__(
        self,
        benchmark_loss,
        train,
        validate,
        test,
        filepath,
        monitor='val_loss',
        mode='auto',
    ):
        super(ReloadBest, self).__init__(
            filepath=filepath,
            monitor=monitor,
            verbose=0,
            mode=mode,
            save_best_only=False,
            save_weights_only=True,
            period=1
        )
        self.benchmark_loss = benchmark_loss
        self.train = train
        self.validate = validate
        self.test = test
        self.epochs = 0
        self.test_loss = None
        self.train_loss = None
        self.validate_loss = None
        self.gain = None
        self.best_epoch = None
        self.train_begin = None

    def on_train_begin(self, logs=None):
        super(ReloadBest, self).on_train_begin(logs)

        self.train_begin = datetime.utcnow()
        logger.info('========================================================')
        logger.info('|    epoch |     time |    train | validate |     gain |')
        logger.info('--------------------------------------------------------')
    
    def on_train_end(self, logs=None):
        super(ReloadBest, self).on_train_end(logs)
        logger.info('========================================================')
        time = datetime.utcnow() - self.train_begin
        if self.best_epoch is not None:
            with timer('load best epoch (%i):' % self.best_epoch):
                self.model.load_weights(
                    self.filepath.format(epoch=self.best_epoch)
                )
        with timer('predict all test:'):
            prediction = self.model.predict(self.test.x)
        with timer('calculate test loss:'):
            # TODO use same loss function not just MAE
            self.test_loss = mean_absolute_error(
                self.test.y,
                prediction
            )
        self.gain = (100 * -(1 - (self.benchmark_loss / self.test_loss)))
        logger.info('========================================================')
        logger.info('|          | train    | validate | test     |          |')
        logger.info('|     time | loss     | loss     | loss     |     gain |')
        logger.info('--------------------------------------------------------')
        logger.info('| %8s | %8.2f | %8.2f | %8.2f | %7.2f%% |' % (
            str(time).split('.', 2)[0],
            self.train_loss,
            self.validate_loss,
            self.test_loss,
            self.gain
        ))
        logger.info('========================================================')
    
    def on_epoch_end(self, epoch, logs=None):
        super(ReloadBest, self).on_epoch_end(epoch, logs)
        self.epochs += 1
        time = datetime.utcnow() - self.train_begin
        train_loss = logs.get('loss')
        validate_loss = logs.get('val_loss')
        gain = (100 * -(1 - (self.benchmark_loss / validate_loss)))
        if self.gain is None or gain > self.gain:
            self.gain = gain
            self.best_epoch = epoch
            self.train_loss = train_loss
            self.validate_loss = validate_loss
        logger.info('| %8i | %8s | %8.2f | %8.2f | %7.2f%% |' % (
            epoch, str(time).split('.', 2)[0], train_loss, validate_loss, gain)
        )

    def stats(self):
        return {
            'epochs': self.epochs,
            'benchmark': self.benchmark_loss,
            'train': self.train_loss,
            'validate': self.validate_loss,
            'test': self.test_loss,
            'gain': self.gain
        }
