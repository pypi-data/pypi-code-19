import numpy as np


def hello():
    return "Hello motherfuckers"


def predict(x, F, B, u, Q, P):
    x = np.dot(F, x) + np.dot(B, u)
    P = np.dot(np.dot(F, P), F.T) + Q

    return x, P


def update(x, z, H, R, P):
    y = z - np.dot(H, x)
    S = R + np.dot(np.dot(H, P), H.T)
    K = np.dot(np.dot(P, H.T), np.linalg.inv(S))
    x = x + np.dot(K, y)
    P = np.dot((np.eye(4) - np.dot(K, H)), P)

    return x, P


def kalman(x, F, B, u, Q, z, H, R, P):
    x1, P1 = predict(x, F, B, u, Q, P)
    x, P = update(x1, z, H, R, P1)