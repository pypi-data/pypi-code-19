from nn.Activation import ReLU
import numpy as np

relu = ReLU()
arr = np.array([[2, -1], [-3, 6]])
arr2 = np.array([[-2, -1], [4, 6]])
ones = np.ones((2, 2))

test2 = relu.forward(arr)
print(arr)

test3 = relu.backward(ones)
print(test3)

test4 = relu.forward(arr2)
print(test4)

test5 = relu.backward(ones)
print(test5)