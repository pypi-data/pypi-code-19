def affine():
    pass


def backprop_affine():
    pass


def reshape():
    pass


def Linear(allocate, nO, nI, nP):
    (W, b), (dW, db) = allocate((nO, nI), (nO,), dtype='f', gradient=True)

    def linear_forward(X, out=None):
        Y = out or allocate('f', (X.shape[0], nO))

        def linear_backward(dY, out=None):
            dY = out or allocate('f', (dX.shape[0], nI))
            backprop_affine(dX,
                dW, db, dY, X)
            return dX
        affine(Y,
            W, b, X)
        return Y, linear_backward
    return Model(linear_forward)


def Linear3d(allocate, nI, nO, nP):
    (W, b), (dW, db) = allocate((nO * nP, nI), (nO * nP,), dtype='f', gradient=True)

    def linear_forward(X, out=None):
        Y = out or allocate('f', (X.shape[0], nO * nP))

        def linear_backward(dY, out=None):
            dY = reshape(dY, (dY.shape[0], nO, nP))
            dX = out or allocate('f', (dX.shape[0], nI))
            backprop_affine(dX,
                dW, db, dY, X)
            return dX
        affine(Y,
            W, b, X)
        Y = reshape(Y, (Y.shape[0], nO, nP))
        return Y, linear_backward
    return Model(linear_forward)
