
import unittest

from keras.layers import Activation, Dense, Dropout, Input
import numpy as np

from transparent_keras import TransparentModel


class TransparentModelTest(unittest.TestCase):
    def _get_tensors(self):
        x0 = Input(shape=(10,))
        x = Dense(10, activation="relu")(x0)
        x = Dropout(0.5)(x)
        y_extra = x = Dense(10)(x)
        x = Activation("relu")(x)
        x = Dropout(0.5)(x)
        y = Dense(1)(x)

        return x0, y, y_extra

    def test_train_on_batch(self):
        x0, y, y_extra = self._get_tensors()

        m = TransparentModel(
            inputs=x0,
            outputs=y,
            observed_tensors=y_extra
        )

        m.compile("sgd", "mse")

        x = np.random.rand(128, 10)
        y = np.random.rand(128, 1)

        loss1, y_extra = m.train_on_batch(x, y)
        self.assertEqual(y_extra.shape, (128, 10))

        loss2, y_extra = m.train_on_batch(x, y)
        self.assertTrue(loss1 > loss2)

    def test_test_on_batch(self):
        x0, y, y_extra = self._get_tensors()

        m = TransparentModel(
            inputs=x0,
            outputs=y,
            observed_tensors=y_extra
        )

        m.compile("sgd", "mse")

        x = np.random.rand(128, 10)
        y = np.random.rand(128, 1)

        loss1, y_extra1 = m.test_on_batch(x, y)
        self.assertEqual(y_extra1.shape, (128, 10))

        loss2, y_extra2 = m.test_on_batch(x, y)
        self.assertEqual(loss1, loss2)
        self.assertTrue(np.all(y_extra1 == y_extra2))


if __name__ == "__main__":
    unittest.main()
