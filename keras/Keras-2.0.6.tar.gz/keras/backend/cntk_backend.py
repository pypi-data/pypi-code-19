from __future__ import print_function
import cntk as C
import numpy as np
from .common import _FLOATX, _EPSILON, image_dim_ordering, image_data_format
from collections import defaultdict
from contextlib import contextmanager
import warnings


C.set_global_option('align_axis', 1)


b_any = any


dev = C.device.use_default_device()
if dev.type() == 0:
    warnings.warn(
        'CNTK backend warning: GPU is not detected. '
        'CNTK\'s CPU version is not fully optimized,'
        'please run with GPU to get better performance.')

# A learning phase is a bool tensor used to run Keras models in
# either train mode (learning_phase == 1) or test mode (learning_phase == 0).
_LEARNING_PHASE = C.constant(shape=(), dtype=np.float32, value=1.0, name="_keras_learning_phase")
_UID_PREFIXES = defaultdict(int)

# cntk doesn't support gradient as symbolic op, to hook up with keras model,
# we will create gradient as a constant placeholder, here use this global
# map to keep the mapping from grad placeholder to parameter
grad_parameter_dict = {}

NAME_SCOPE_STACK = []


@contextmanager
def name_scope(name):
    global NAME_SCOPE_STACK
    NAME_SCOPE_STACK.append(name)
    yield
    NAME_SCOPE_STACK.pop()


def get_uid(prefix=''):
    _UID_PREFIXES[prefix] += 1
    return _UID_PREFIXES[prefix]


def learning_phase():
    # False = test, True = train
    return _LEARNING_PHASE


def set_learning_phase(value):
    global _LEARNING_PHASE
    if value not in {0, 1}:
        raise ValueError('CNTK Backend: Set learning phase '
                         'with value %s is not supported, '
                         'expected 0 or 1.' % value)
    v = np.float32([value])
    _LEARNING_PHASE.value = v


def in_train_phase(x, alt, training=None):
    global _LEARNING_PHASE
    if training is None:
        training = learning_phase()
        uses_learning_phase = True
    else:
        uses_learning_phase = False

    # CNTK currently don't support cond op, so here we use
    # element_select approach as workaround. It may have
    # perf issue, will resolve it later with cntk cond op.
    if callable(x) and isinstance(x, C.cntk_py.Function) is False:
        x = x()
    if callable(alt) and isinstance(alt, C.cntk_py.Function) is False:
        alt = alt()

    if training is True:
        x._uses_learning_phase = uses_learning_phase
        return x
    else:
        result = C.element_select(training, x, alt)
        result._uses_learning_phase = uses_learning_phase
        return result


def in_test_phase(x, alt):
    global _LEARNING_PHASE
    # Similiar as in_train_phase, use element_select as workaround.
    if callable(x) and isinstance(x, C.cntk_py.Function) is False:
        x = x()
    if callable(alt) and isinstance(alt, C.cntk_py.Function) is False:
        alt = alt()

    return C.element_select(learning_phase(), x, alt)


def _convert_string_dtype(dtype):
    # cntk only support float32 and float64
    if dtype == 'float32':
        return np.float32
    elif dtype == 'float64':
        return np.float64
    else:
        # cntk only running with float,
        # try to cast to float to run the model
        return np.float32


def _convert_dtype_string(dtype):
    if dtype == np.float32:
        return 'float32'
    elif dtype == np.float64:
        return 'float64'
    else:
        raise ValueError('CNTK Backend: Unsupported dtype: %s. '
                         'CNTK only supports float32 and '
                         'float64.' % dtype)


def variable(value, dtype=_FLOATX, name=None):
    if name is None:
        name = ''

    if isinstance(
            value,
            C.variables.Constant) or isinstance(
            value,
            C.variables.Parameter):
        value = value.value

    # we don't support init parameter with symbolic op, so eval it first as
    # workaround
    if isinstance(value, C.cntk_py.Function):
        value = eval(value)

    shape = value.shape if hasattr(value, 'shape') else ()
    if hasattr(value, 'dtype') and value.dtype != dtype and len(shape) > 0:
        value = value.astype(dtype)
    # cntk will init type based on the value type
    v = C.parameter(shape=shape,
                    init=value,
                    name=_prepare_name(name, 'variable'))
    v._keras_shape = v.shape
    v._uses_learning_phase = False
    return v


def bias_add(x, bias, data_format=None):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    dims = len(x.shape)
    if dims > 0 and x.shape[0] == C.InferredDimension:
        dims -= 1

    bias_dims = len(bias.shape)
    if bias_dims != 1 and bias_dims != dims:
        raise ValueError('Unexpected bias dimensions %d, '
                         'expected 1 or %d dimensions' % (bias_dims, dims))

    if dims == 4:
        if data_format == 'channels_first':
            if bias_dims == 1:
                shape = (bias.shape[0], 1, 1, 1)
            else:
                shape = (bias.shape[3],) + bias.shape[:3]
        elif data_format == 'channels_last':
            if bias_dims == 1:
                shape = (1, 1, 1, bias.shape[0])
            else:
                shape = bias.shape
    elif dims == 3:
        if data_format == 'channels_first':
            if bias_dims == 1:
                shape = (bias.shape[0], 1, 1)
            else:
                shape = (bias.shape[2],) + bias.shape[:2]
        elif data_format == 'channels_last':
            if bias_dims == 1:
                shape = (1, 1, bias.shape[0])
            else:
                shape = bias.shape
    elif dims == 2:
        if data_format == 'channels_first':
            if bias_dims == 1:
                shape = (bias.shape[0], 1)
            else:
                shape = (bias.shape[1],) + bias.shape[:1]
        elif data_format == 'channels_last':
            if bias_dims == 1:
                shape = (1, bias.shape[0])
            else:
                shape = bias.shape
    else:
        shape = bias.shape
    return x + reshape(bias, shape)


def eval(x):
    if isinstance(x, C.cntk_py.Function):
        return x.eval()
    elif isinstance(x, C.variables.Constant) or isinstance(x, C.variables.Parameter):
        return x.value
    else:
        raise ValueError('CNTK Backend: `eval` method on '
                         '`%s` type is not supported. '
                         'CNTK only supports `eval` with '
                         '`Function`, `Constant` or '
                         '`Parameter`.' % type(x))


def placeholder(
        shape=None,
        ndim=None,
        dtype=_FLOATX,
        sparse=False,
        name=None,
        dynamic_axis_num=1):
    if not shape:
        if ndim:
            shape = tuple([None for _ in range(ndim)])

    cntk_shape = [C.InferredDimension if s is None else s for s in shape]
    cntk_shape = tuple(cntk_shape)

    if dynamic_axis_num > len(cntk_shape):
        raise ValueError('CNTK backend: creating placeholder with '
                         '%d dimension is not supported, at least '
                         '%d dimensions are needed.'
                         % (len(cntk_shape, dynamic_axis_num)))

    if name is None:
        name = ''

    cntk_shape = cntk_shape[dynamic_axis_num:]

    x = C.input(
        shape=cntk_shape,
        dtype=_convert_string_dtype(dtype),
        is_sparse=sparse,
        name=name)
    x._keras_shape = shape
    x._uses_learning_phase = False
    return x


def is_keras_tensor(x):
    return hasattr(x, '_keras_history')


def shape(x):
    shape = list(int_shape(x))
    num_dynamic = _get_dynamic_axis_num(x)
    non_dyn_shape = []
    for i in range(len(x.shape)):
        if shape[i + num_dynamic] is None:
            non_dyn_shape.append(x.shape[i])
        else:
            non_dyn_shape.append(shape[i + num_dynamic])
    return shape[:num_dynamic] + non_dyn_shape


def is_sparse(tensor):
    return tensor.is_sparse


def int_shape(x):
    if hasattr(x, '_keras_shape'):
        return x._keras_shape

    shape = x.shape
    if hasattr(x, 'dynamic_axes'):
        dynamic_shape = [None for a in x.dynamic_axes]
        shape = tuple(dynamic_shape) + shape
    return shape


def ndim(x):
    shape = int_shape(x)
    return len(shape)


def _prepare_name(name, default):
    prefix = '_'.join(NAME_SCOPE_STACK)
    if name is None or name == '':
        return prefix + '/' + default
    return prefix + '/' + name


def constant(value, dtype=None, shape=None, name=None):
    if dtype is None:
        dtype = _FLOATX
    if shape is None:
        shape = ()
    np_value = value * np.ones(shape)
    const = C.constant(np_value,
                       dtype=dtype,
                       name=_prepare_name(name, 'constant'))
    const._keras_shape = shape
    const._uses_learning_phase = False
    return const


def random_binomial(shape, p=0.0, dtype=None, seed=None):
    # use numpy workaround now
    if seed is None:
        # ensure that randomness is conditioned by the Numpy RNG
        seed = np.random.randint(10e7)
        np.random.seed(seed)
    if dtype is None:
        dtype = np.float32
    else:
        dtype = _convert_string_dtype(dtype)

    size = 1
    for _ in shape:
        if _ is None:
            raise ValueError('CNTK Backend: randomness op with '
                             'dynamic shape is not supported now. '
                             'Please provide fixed dimension '
                             'instead of `None`.')
        size *= _

    binomial = np.random.binomial(1, p, size).astype(dtype).reshape(shape)
    return variable(value=binomial, dtype=dtype)


def random_uniform(shape, minval=0.0, maxval=1.0, dtype=None, seed=None):
    for _ in shape:
        if _ is None:
            raise ValueError('CNTK Backend: randomness op with '
                             'dynamic shape is not supported now. '
                             'Please provide fixed dimension '
                             'instead of `None`.')

    return random_uniform_variable(shape, minval, maxval, dtype, seed)


def random_uniform_variable(shape, low, high, dtype=_FLOATX,
                            name=None, seed=None):
    if seed is None:
        # ensure that randomness is conditioned by the Numpy RNG
        seed = np.random.randint(10e3)

    if dtype is None:
        dtype = np.float32
    else:
        dtype = _convert_string_dtype(dtype)

    if name is None:
        name = ''

    scale = (high - low) / 2
    p = C.parameter(
        shape,
        init=C.initializer.uniform(
            scale,
            seed=seed),
        dtype=dtype,
        name=name)
    return variable(value=p.value + low + scale)


def random_normal_variable(
        shape,
        mean,
        scale,
        dtype=_FLOATX,
        name=None,
        seed=None):
    if seed is None:
        # ensure that randomness is conditioned by the Numpy RNG
        seed = np.random.randint(10e7)
    if dtype is None:
        dtype = np.float32
    else:
        dtype = _convert_string_dtype(dtype)

    if name is None:
        name = ''

    return C.parameter(
        shape=shape,
        init=C.initializer.normal(
            scale=scale,
            seed=seed),
        dtype=dtype,
        name=name)


def random_normal(shape, mean=0.0, stddev=1.0, dtype=_FLOATX, seed=None):
    for _ in shape:
        if _ is None:
            raise ValueError('CNTK Backend: randomness op with '
                             'dynamic shape is not supported now. '
                             'Please provide fixed dimension '
                             'instead of `None`.')
    # how to apply mean and stddev
    return random_normal_variable(shape=shape, mean=mean, scale=1.0)


def truncated_normal(shape, mean=0.0, stddev=1.0, dtype=None, seed=None):
    if seed is None:
        seed = np.random.randint(1, 10e6)
    if dtype is None:
        dtype = np.float32
    else:
        dtype = _convert_string_dtype(dtype)

    return C.parameter(
        shape, init=C.initializer.truncated_normal(
            stddev, seed=seed), dtype=dtype)


def zeros_like(x, dtype=None, name=None):
    return x * 0


def dtype(x):
    return _convert_dtype_string(x.dtype)


def zeros(shape, dtype=_FLOATX, name=None):
    ctype = _convert_string_dtype(dtype)
    return variable(value=np.zeros(shape, ctype), dtype=dtype, name=name)


def ones(shape, dtype=_FLOATX, name=None):
    ctype = _convert_string_dtype(dtype)
    return variable(value=np.ones(shape, ctype), dtype=dtype, name=name)


def eye(size, dtype=_FLOATX, name=None):
    return variable(np.eye(size), dtype, name)


def ones_like(x, name=None):
    return zeros_like(x) + 1


def count_params(x):
    for _ in x.shape:
        if _ == C.InferredDimension or _ == C.FreeDimension:
            raise ValueError('CNTK backend: `count_params` with dynamic '
                             'shape is not supported. Please provide '
                             'fixed dimension instead of `None`.')

    return np.prod([x.shape[i] for i in range(len(x.shape))])


def cast(x, dtype):
    # cntk calculate everything in float, so don't need case from bool / int
    return x


def dot(x, y):
    if len(x.shape) > 2 or len(y.shape) > 2:
        y_shape = int_shape(y)
        if len(y_shape) > 2:
            permutation = [len(y_shape) - 2]
            permutation += list(range(0, len(y_shape) - 2))
            permutation += [len(y_shape) - 1]
            y = C.transpose(y, perm=permutation)
        return C.times(x, y, len(y_shape) - 1)
    else:
        return C.times(x, y)


def batch_dot(x, y, axes=None):
    x_shape = int_shape(x)
    y_shape = int_shape(y)

    if isinstance(axes, int):
        axes = (axes, axes)
    if axes is None:
        # behaves like tf.batch_matmul as default
        axes = [len(x_shape) - 1, len(y_shape) - 2]

    if len(x_shape) == 2 and len(y_shape) == 2:
        return sum(x * y, axis=1, keepdims=True)
    else:
        if len(y_shape) == 2:
            y = expand_dims(y)

        normalized_axis = []
        normalized_axis.append(_normalize_axis(axes[0], x)[0])
        normalized_axis.append(_normalize_axis(axes[1], y)[0])
        # transpose
        i = normalized_axis[0]
        while i < len(x.shape) - 1:
            x = C.swapaxes(x, i, i + 1)
            i += 1
        i = normalized_axis[1]
        while i > 0:
            y = C.swapaxes(y, i, i - 1)
            i -= 1
        result = C.times(x, y, output_rank=(len(y.shape) - 1)
                         if len(y.shape) > 1 else 1)
        if len(y_shape) == 2:
            result = squeeze(result, -1)
        return result


def transpose(x):
    return C.swapaxes(x, 0, 1)


def gather(reference, indices):
    return C.ops.gather(reference, indices)


def _remove_dims(x, axis, keepdims=False):
    if keepdims is False and isinstance(axis, list):
        # sequence axis is removed by default, so don't need reshape on it
        reduce_axes = []
        for a in axis:
            if isinstance(a, C.Axis) is False:
                reduce_axes.append(a)
        return _reshape_dummy_dim(x, reduce_axes)
    else:
        if isinstance(axis, list):
            has_seq = False
            for a in axis:
                if isinstance(a, C.Axis):
                    has_seq = True
                    break
            if has_seq:
                nones = _get_dynamic_axis_num(x)
                x = expand_dims(x, nones)
        return x


def max(x, axis=None, keepdims=False):
    axis = _normalize_axis(axis, x)
    output = _reduce_on_axis(x, axis, 'reduce_max')

    return _remove_dims(output, axis, keepdims)


def min(x, axis=None, keepdims=False):
    axis = _normalize_axis(axis, x)
    output = _reduce_on_axis(x, axis, 'reduce_min')

    return _remove_dims(output, axis, keepdims)


def sum(x, axis=None, keepdims=False):
    axis = _normalize_axis(axis, x)
    output = _reduce_on_axis(x, axis, 'reduce_sum')

    return _remove_dims(output, axis, keepdims)


def prod(x, axis=None, keepdims=False):
    axis = _normalize_axis(axis, x)
    output = _reduce_on_axis(x, axis, 'reduce_prod')

    return _remove_dims(output, axis, keepdims)


def logsumexp(x, axis=None, keepdims=False):
    return log(sum(exp(x), axis=axis, keepdims=keepdims))


def var(x, axis=None, keepdims=False):
    m = mean(x, axis, keepdims=True)
    devs_squared = C.square(x - m)
    return mean(devs_squared, axis=axis, keepdims=keepdims)


def std(x, axis=None, keepdims=False):
    return C.sqrt(var(x, axis=axis, keepdims=keepdims))


def expand_dims(x, axis=-1):
    shape = list(int_shape(x))
    nones = _get_dynamic_axis_num(x)

    index = axis if axis >= 0 else len(shape) + 1
    shape.insert(index, 1)
    new_shape = shape[nones:]
    new_shape = tuple(
        [C.InferredDimension if _ is None else _ for _ in new_shape])
    return C.reshape(x, new_shape)


def squeeze(x, axis):
    if isinstance(axis, tuple):
        axis = list(axis)
    if not isinstance(axis, list):
        axis = [axis]

    shape = list(int_shape(x))

    _axis = []
    for _ in axis:
        if isinstance(_, int):
            _axis.append(_ if _ >= 0 else _ + len(shape))

    if len(_axis) == 0:
        return x

    nones = _get_dynamic_axis_num(x)
    for _ in sorted(_axis, reverse=True):
        del shape[_]

    new_shape = tuple(shape[nones:])
    return C.reshape(x, new_shape)


def tile(x, n):
    if isinstance(n, list):
        n = tuple(n)

    shape = int_shape(x)
    num_dynamic_axis = _get_dynamic_axis_num(x)
    # Padding the axis
    if len(n) < len(shape):
        n = tuple([None for _ in range(len(shape) - len(n))]) + n

    if len(n) != len(shape):
        raise NotImplementedError

    i = num_dynamic_axis
    for i, rep in enumerate(n):
        if i >= num_dynamic_axis and shape[i] is not None:
            tmp = [x] * rep
            x = C.splice(*tmp, axis=i - num_dynamic_axis)
        i += 1

    return x


def _normalize_axis(axis, x):
    shape = int_shape(x)
    ndim = len(shape)

    nones = _get_dynamic_axis_num(x)

    if isinstance(axis, tuple):
        _axis = list(axis)
    elif isinstance(axis, int):
        _axis = [axis]
    elif isinstance(axis, list):
        _axis = list(axis)
    else:
        _axis = axis

    if isinstance(_axis, list):
        for i, a in enumerate(_axis):
            if a is not None and a < 0:
                _axis[i] = (a % ndim)
            if _axis[i] is not None:
                if _axis[i] < nones:
                    _axis[i] = x.dynamic_axes[_axis[i]]
                else:
                    _axis[i] -= nones
    else:
        if _axis is None:
            _axis = C.Axis.all_axes()

    return _axis


def _reshape_dummy_dim(x, axis):
    shape = list(x.shape)

    _axis = [_ + len(shape) if _ < 0 else _ for _ in axis]

    if shape.count(C.InferredDimension) > 1:
        result = x
        for index in sorted(_axis, reverse=True):
            result = C.reshape(result,
                               shape=(),
                               begin_axis=index,
                               end_axis=index + 1)
        return result
    else:
        for index in sorted(_axis, reverse=True):
            del shape[index]

        shape = tuple(shape)
        return C.reshape(x, shape)


def mean(x, axis=None, keepdims=False):
    axis = _normalize_axis(axis, x)
    output = _reduce_on_axis(x, axis, 'reduce_mean')

    return _remove_dims(output, axis, keepdims)


def any(x, axis=None, keepdims=False):
    reduce_result = sum(x, axis, keepdims=keepdims)
    any_matrix = C.element_select(
        reduce_result,
        ones_like(reduce_result),
        zeros_like(reduce_result))
    if len(reduce_result.shape) == 0 and _get_dynamic_axis_num(x) == 0:
        return C.reduce_sum(any_matrix)
    else:
        return any_matrix


def all(x, axis=None, keepdims=False):
    reduce_result = prod(x, axis, keepdims=keepdims)
    all_matrix = C.element_select(
        reduce_result,
        ones_like(reduce_result),
        zeros_like(reduce_result))
    if len(reduce_result.shape) == 0 and _get_dynamic_axis_num(x) == 0:
        return C.reduce_sum(all_matrix)
    else:
        return all_matrix


def classification_error(output, target, axis=-1):
    return C.ops.reduce_mean(
        C.equal(
            argmax(
                output,
                axis=-1),
            argmax(
                target,
                axis=-1)),
        axis=C.Axis.all_axes())


def argmax(x, axis=-1):
    axis = [axis]
    axis = _normalize_axis(axis, x)
    output = C.ops.argmax(x, axis=axis[0])
    return _reshape_dummy_dim(output, axis)


def argmin(x, axis=-1):
    axis = [axis]
    axis = _normalize_axis(axis, x)
    output = C.ops.argmin(x, axis=axis[0])
    return _reshape_dummy_dim(output, axis)


def square(x):
    return C.square(x)


def abs(x):
    return C.abs(x)


def sqrt(x):
    return C.sqrt(x)


def exp(x):
    return C.exp(x)


def log(x):
    return C.log(x)


def round(x):
    return C.round(x)


def sigmoid(x):
    return C.sigmoid(x)


def sign(x):
    return x / C.abs(x)


def pow(x, a):
    return C.pow(x, a)


def clip(x, min_value, max_value):
    if max_value is not None and max_value < min_value:
        max_value = min_value
    if max_value is None:
        max_value = np.inf
    if min_value is None:
        min_value = -np.inf
    return C.clip(x, min_value, max_value)


def binary_crossentropy(output, target, from_logits=False):
    if from_logits:
        output = C.sigmoid(output)
    output = C.clip(output, _EPSILON, 1.0 - _EPSILON)
    output = -target * C.log(output) - (1.0 - target) * C.log(1.0 - output)
    return output


def get_variable_shape(x):
    return x.shape


def update(x, new_x):
    return C.assign(x, new_x)


def moving_average_update(variable, value, momentum):
    return C.assign(variable, variable * momentum + value * (1. - momentum))


def update_add(x, increment):
    result = x + increment
    return C.assign(x, result)


def gradients(loss, variables):
    # cntk does not support gradients as symbolic op,
    # to hook up with keras model
    # we will return a constant as place holder, the cntk learner will apply
    # the gradient during training.
    global grad_parameter_dict
    if isinstance(variables, list) is False:
        variables = [variables]
    grads = []
    for v in variables:
        g = C.constant(0, shape=v.shape, name='keras_grad_placeholder')
        grads.append(g)
        grad_parameter_dict[g] = v
    return grads


def equal(x, y):
    return C.equal(x, y)


def not_equal(x, y):
    return C.not_equal(x, y)


def greater(x, y):
    return C.greater(x, y)


def greater_equal(x, y):
    return C.greater_equal(x, y)


def less(x, y):
    return C.less(x, y)


def less_equal(x, y):
    return C.less_equal(x, y)


def maximum(x, y):
    return C.element_max(x, y)


def minimum(x, y):
    return C.element_min(x, y)


def sin(x):
    return C.sin(x)


def cos(x):
    return C.cos(x)


def normalize_batch_in_training(x, gamma, beta,
                                reduction_axes, epsilon=1e-3):
    if gamma is None:
        if beta is None:
            gamma = ones_like(x)
        else:
            gamma = ones_like(beta)
    if beta is None:
        if gamma is None:
            beta = zeros_like(x)
        else:
            beta = zeros_like(gamma)

    mean, variant = _moments(x, _normalize_axis(reduction_axes, x))

    if sorted(reduction_axes) == list(range(ndim(x)))[:-1]:
        normalized = batch_normalization(
            x, mean, variant, beta, gamma, epsilon)
    else:
        # need broadcasting
        target_shape = []
        x_shape = int_shape(x)
        # skip the batch axis
        for axis in range(1, ndim(x)):
            if axis in reduction_axes:
                target_shape.append(1)
            else:
                target_shape.append(x_shape[axis])

        broadcast_mean = C.reshape(mean, target_shape)
        broadcast_var = C.reshape(variant, target_shape)
        broadcast_gamma = C.reshape(gamma, target_shape)
        broadcast_beta = C.reshape(beta, target_shape)
        normalized = batch_normalization(
            x,
            broadcast_mean,
            broadcast_var,
            broadcast_beta,
            broadcast_gamma,
            epsilon)

    return normalized, mean, variant


def _moments(x, axes=None, shift=None, keep_dims=False):
    _axes = tuple(axes)
    if shift is None:
        shift = x
        # Compute true mean while keeping the dims for proper broadcasting.
        for axis in _axes:
            shift = C.reduce_mean(shift, axis=axis)

    shift = C.stop_gradient(shift)
    shifted_mean = C.minus(x, shift)
    for axis in _axes:
        shifted_mean = C.reduce_mean(shifted_mean, axis=axis)

    variance_mean = C.square(C.minus(x, shift))
    for axis in _axes:
        variance_mean = C.reduce_mean(variance_mean, axis=axis)

    variance = C.minus(variance_mean, C.square(shifted_mean))
    mean = C.plus(shifted_mean, shift)

    if not keep_dims:
        mean = squeeze(mean, _axes)
        variance = squeeze(variance, _axes)

    return mean, variance


def batch_normalization(x, mean, var, beta, gamma, epsilon=1e-3):
    # The mean / var / beta / gamma may be processed by broadcast
    # so it may have an extra batch axis with 1, it is not needed
    # in cntk, need to remove those dummy axis.
    if ndim(mean) == ndim(x) and shape(mean)[0] == 1:
        mean = _reshape_dummy_dim(mean, [0])
    if ndim(var) == ndim(x) and shape(var)[0] == 1:
        var = _reshape_dummy_dim(var, [0])

    if gamma is None:
        gamma = ones_like(var)
    elif ndim(gamma) == ndim(x) and shape(gamma)[0] == 1:
        gamma = _reshape_dummy_dim(gamma, [0])

    if beta is None:
        beta = zeros_like(mean)
    elif ndim(beta) == ndim(x) and shape(beta)[0] == 1:
        beta = _reshape_dummy_dim(beta, [0])

    return gamma * ((x - mean) / C.sqrt(var + epsilon)) + beta


def concatenate(tensors, axis=-1):
    if len(tensors) == 0:
        return None

    axis = [axis]
    axis = _normalize_axis(axis, tensors[0])
    return C.splice(*tensors, axis=axis[0])


def flatten(x):
    return reshape(x, (-1,))


def reshape(x, shape):
    if isinstance(x, C.variables.Parameter):
        return C.reshape(x, shape)
    else:
        num_dynamic_axis = _get_dynamic_axis_num(x)

        if num_dynamic_axis == 1 and len(shape) > 0 and shape[0] == -1:
            # collapse axis with batch axis
            if b_any(_ == C.InferredDimension for _ in x.shape) or b_any(
                    _ == C.FreeDimension for _ in x.shape):
                warnings.warn(
                    'Warning: CNTK backend does not support '
                    'collapse of batch axis with inferred dimension. '
                    'The reshape did not take place.')
                return x
            return C.user_function(ReshapeBatch(x, shape[1:]))
        else:
            # no collaps, then first need to padding the shape
            if num_dynamic_axis >= len(shape):
                i = 0
                while i < len(shape):
                    if shape[i] is None or shape[i] == -1:
                        i += 1
                    else:
                        break
                shape = tuple([-1 for _ in range(num_dynamic_axis - i)]) + shape

            new_shape = list(shape)
            new_shape = new_shape[num_dynamic_axis:]
            new_shape = [C.InferredDimension if _ is None else _ for _ in new_shape]
            return C.reshape(x, new_shape)


def permute_dimensions(x, pattern):
    dims = len(int_shape(x))
    num_dynamic_axis = _get_dynamic_axis_num(x)
    current_layout = tuple([i for i in range(dims)])

    if num_dynamic_axis > 0 and pattern[:num_dynamic_axis] != current_layout[:num_dynamic_axis]:
        raise ValueError('CNTK backend: the permute pattern %s '
                         'requested permute on dynamic axis, '
                         'which is not supported. Please do permute '
                         'on static axis.' % pattern)

    axis = list(pattern)
    axis = axis[num_dynamic_axis:]
    axis = _normalize_axis(axis, x)
    return C.transpose(x, axis)


def resize_images(X, height_factor, width_factor, data_format):
    if data_format == 'channels_first':
        output = repeat_elements(X, height_factor, axis=2)
        output = repeat_elements(output, width_factor, axis=3)
        return output
    elif data_format == 'channels_last':
        output = repeat_elements(X, height_factor, axis=1)
        output = repeat_elements(output, width_factor, axis=2)
        return output
    else:
        raise ValueError('CNTK Backend: Invalid dim_ordering:', data_format)


def repeat_elements(x, rep, axis):
    axis = _normalize_axis(axis, x)
    axis = axis[0]
    slices = []
    shape = x.shape
    i = 0
    while i < shape[axis]:
        tmp = C.ops.slice(x, axis, i, i + 1)
        for _ in range(rep):
            slices.append(tmp)
        i += 1
    return C.splice(*slices, axis=axis)


def repeat(x, n):
    # this is a workaround for recurrent layer
    # if n is inferred dimension,
    # we can't figure out how to repeat it in cntk now
    # return the same x to take cntk broadcast feature
    # to make the recurrent layer work.
    # need to be fixed in GA.
    if n is C.InferredDimension:
        return x
    index = 1 - _get_dynamic_axis_num(x)
    if index < 0 or index > 1:
        raise NotImplementedError

    new_shape = list(x.shape)
    new_shape.insert(index, 1)
    new_shape = tuple(new_shape)
    x = C.reshape(x, new_shape)
    temp = [x] * n
    return C.splice(*temp, axis=index)


def tanh(x):
    return C.tanh(x)


def _static_rnn(step_function, inputs, initial_states,
                go_backwards=False, mask=None, constants=None,
                unroll=False, input_length=None):

    shape = int_shape(inputs)
    dims = len(shape)

    if dims < 3:
        raise ValueError('Input should be at least 3D.')

    # if the second axis is static axis, CNTK will do unroll by default
    if shape[1] is None:
        raise ValueError('CNTK Backend: the input of static rnn '
                         'has shape `%s`, the second axis '
                         'is not static. If you want to run '
                         'rnn with non-static axis, plesae try '
                         'dynamic rnn with sequence axis.' % shape)
    if constants is None:
        constants = []

    if mask is not None:
        mask_shape = int_shape(mask)
        if len(mask_shape) == dims - 1:
            mask = expand_dims(mask)

    nones = _get_dynamic_axis_num(inputs)

    states = tuple(initial_states)

    outputs = []

    time_axis = 1 - nones if nones > 0 else 1

    if go_backwards:
        i = shape[1] - 1
        while i >= 0:
            current = C.ops.slice(inputs, time_axis, i, i + 1)
            # remove dummy dimension
            current = squeeze(current, time_axis)

            output, new_states = step_function(
                current, tuple(states) + tuple(constants))

            if mask is not None:
                mask_slice = C.ops.slice(mask, time_axis, i, i + 1)
                mask_slice = squeeze(mask_slice, time_axis)
                if len(outputs) == 0:
                    prev_output = zeros_like(output)
                else:
                    prev_output = outputs[-1]
                output = C.ops.element_select(mask_slice, output, prev_output)

                return_states = []
                for s, n_s in zip(states, new_states):
                    return_states.append(
                        C.ops.element_select(
                            mask_slice, n_s, s))
                new_states = return_states
            outputs.append(output)
            states = new_states
            i -= 1
    else:
        i = 0
        while i < shape[1]:
            current = C.ops.slice(inputs, time_axis, i, i + 1)
            # remove dummy dimension
            current = squeeze(current, 1)

            output, new_states = step_function(
                current, tuple(states) + tuple(constants))

            if mask is not None:
                mask_slice = C.ops.slice(mask, time_axis, i, i + 1)
                mask_slice = squeeze(mask_slice, 1)
                if len(outputs) == 0:
                    prev_output = zeros_like(output)
                else:
                    prev_output = outputs[-1]
                output = C.ops.element_select(mask_slice, output, prev_output)

                return_states = []
                for s, n_s in zip(states, new_states):
                    return_states.append(
                        C.ops.element_select(
                            mask_slice, n_s, s))
                new_states = return_states
            outputs.append(output)
            states = new_states[:len(states)]
            i += 1

    i = 1
    # add the time_step axis back
    final_output = expand_dims(outputs[0], 1)
    last_output = outputs[0]
    while i < len(outputs):
        # add the time_step axis back
        output_slice = expand_dims(outputs[i], 1)
        final_output = C.splice(final_output, output_slice, axis=time_axis)
        last_output = outputs[i]
        i += 1

    return last_output, final_output, states


def rnn(step_function, inputs, initial_states,
        go_backwards=False, mask=None, constants=None,
        unroll=False, input_length=None):

    shape = int_shape(inputs)
    dims = len(shape)

    if dims < 3:
        raise ValueError('CNTK Backend: the input of rnn has only rank %d '
                         'Need at least rank 3 to run RNN.' % dims)

    if _get_dynamic_axis_num(inputs) == 0 or unroll:
        return _static_rnn(
            step_function,
            inputs,
            initial_states,
            go_backwards,
            mask,
            constants,
            unroll,
            input_length)

    if mask is not None:
        raise ValueError('RNN with mask is not support in CNTK currently.')

    if constants is None:
        constants = []

    num_time_step = shape[1]
    if num_time_step is None and not has_seq_axis(inputs):
        num_time_step = inputs.shape[0]

    need_convert = not has_seq_axis(inputs)
    if need_convert:
        inputs = C.to_sequence(inputs)

        j = 0
        while j < len(constants):
            if isinstance(constants[j], list):
                i = 0
                while i < len(constants[j]):
                    if _get_dynamic_axis_num(constants[j][i]) == 1:
                        constants[j][i] = C.sequence.broadcast_as(constants[j][i], inputs)
                    i += 1
            else:
                if _get_dynamic_axis_num(constants[j]) == 1:
                    constants[j] = C.sequence.broadcast_as(constants[j], inputs)
            j += 1

    states = tuple(initial_states)

    with C.default_options(axis_offset=1):
        def _recurrence(x, states):
            # create place holder
            place_holders = [C.placeholder() for _ in states]
            past_values = []
            for s, p in zip(states, place_holders):
                past_values.append(
                    C.sequence.past_value(
                        p, s) if go_backwards is False else C.sequence.future_value(
                        p, s))
            new_output, new_states = step_function(
                x, tuple(past_values) + tuple(constants))
            n_s = []
            for o, p in zip(new_states, place_holders):
                n_s.append(o.replace_placeholders({p: o.output}))
            if len(n_s) > 0:
                new_output = n_s[0]
            return new_output, n_s

        final_output, final_states = _recurrence(inputs, states)
        last_output = C.sequence.last(final_output)
        last_states = final_states

    if need_convert:
        final_output = C.sequence.unpack(final_output, 0, no_mask_output=True)
        last_states = [
            C.sequence.unpack(
                s, 0, no_mask_output=True) for s in last_states]
        if num_time_step is not None and num_time_step is not C.FreeDimension:
            final_output = _reshape_sequence(final_output, num_time_step)
            last_states = [
                _reshape_sequence(
                    _, num_time_step) for _ in last_states]

    return last_output, final_output, last_states


def has_seq_axis(x):
    return hasattr(x, 'dynamic_axes') and len(x.dynamic_axes) > 1


def l2_normalize(x, axis):
    axis = [axis]
    axis = _normalize_axis(axis, x)
    norm = C.sqrt(C.reduce_sum(C.square(x), axis=axis[0]))
    return x / norm


def hard_sigmoid(x):
    x = (0.2 * x) + 0.5
    x = C.clip(x, 0.0, 1.0)
    return x


def conv1d(x, kernel, strides=1, padding='valid',
           data_format=None, dilation_rate=1):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    if padding == 'causal':
        # causal (dilated) convolution:
        left_pad = dilation_rate * (kernel.shape[0] - 1)
        x = temporal_padding(x, (left_pad, 0))
        padding = 'valid'

    if data_format == 'channels_last':
        x = C.swapaxes(x, 0, 1)
        kernel = C.swapaxes(kernel, 0, 2)

    padding = _preprocess_border_mode(padding)
    strides = [strides]
    x = C.convolution(
        kernel,
        x,
        strides=tuple(strides),
        auto_padding=[
            False,
            padding])

    if data_format == 'channels_last':
        x = C.swapaxes(x, 0, 1)
    return x


def conv2d(x, kernel, strides=(1, 1), padding='valid',
           data_format=None, dilation_rate=(1, 1)):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    x = _preprocess_conv2d_input(x, data_format)
    kernel = _preprocess_conv2d_kernel(kernel, data_format)
    padding = _preprocess_border_mode(padding)
    if dilation_rate == (1, 1):
        strides = (1,) + strides
        x = C.convolution(
            kernel,
            x,
            strides,
            auto_padding=[
                False,
                padding,
                padding])
    else:
        assert dilation_rate[0] == dilation_rate[1]
        assert strides == (1, 1), 'Invalid strides for dilated convolution'
        x = C.convolution(
            kernel,
            x,
            strides=dilation_rate[0],
            auto_padding=[
                False,
                padding,
                padding])
    return _postprocess_conv2d_output(x, data_format)


def separable_conv2d(x, depthwise_kernel, pointwise_kernel, strides=(1, 1),
                     padding='valid', data_format=None, dilation_rate=(1, 1)):
    raise NotImplementedError


def depthwise_conv2d(x, depthwise_kernel, strides=(1, 1), padding='valid',
                     data_format=None, dilation_rate=(1, 1)):
    raise NotImplementedError


def conv3d(x, kernel, strides=(1, 1, 1), padding='valid',
           data_format=None, dilation_rate=(1, 1, 1)):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    x = _preprocess_conv3d_input(x, data_format)
    kernel = _preprocess_conv3d_kernel(kernel, data_format)
    padding = _preprocess_border_mode(padding)
    strides = strides + (strides[0],)

    x = C.convolution(
        kernel,
        x,
        strides,
        auto_padding=[
            False,
            padding,
            padding,
            padding])
    return _postprocess_conv3d_output(x, data_format)


def conv3d_transpose(x, kernel, output_shape, strides=(1, 1, 1),
                     padding='valid', data_format=None):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    x = _preprocess_conv3d_input(x, data_format)
    kernel = _preprocess_conv3d_kernel(kernel, data_format)
    padding = _preprocess_border_mode(padding)
    strides = (1,) + strides
    # cntk output_shape does not include batch axis
    output_shape = output_shape[1:]
    # in keras2, need handle output shape in different format
    if data_format == 'channels_last':
        shape = list(output_shape)
        shape[0] = output_shape[3]
        shape[1] = output_shape[0]
        shape[2] = output_shape[1]
        shape[3] = output_shape[2]
        output_shape = tuple(shape)

    x = C.convolution_transpose(
        kernel,
        x,
        strides,
        auto_padding=[
            False,
            padding,
            padding,
            padding],
        output_shape=output_shape)
    return _postprocess_conv3d_output(x, data_format)


def pool2d(x, pool_size, strides=(1, 1),
           padding='valid', data_format=None,
           pool_mode='max'):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    padding = _preprocess_border_mode(padding)
    strides = strides
    pool_size = pool_size
    x = _preprocess_conv2d_input(x, data_format)
    if pool_mode == 'max':
        x = C.pooling(
            x,
            C.MAX_POOLING,
            pool_size,
            strides,
            auto_padding=[padding])
    elif pool_mode == 'avg':
        x = C.pooling(
            x,
            C.AVG_POOLING,
            pool_size,
            strides,
            auto_padding=[padding])
    else:
        raise ValueError('Invalid pooling mode: ' + str(pool_mode))
    return _postprocess_conv2d_output(x, data_format)


def pool3d(x, pool_size, strides=(1, 1, 1), padding='valid',
           data_format=None, pool_mode='max'):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    padding = _preprocess_border_mode(padding)

    x = _preprocess_conv3d_input(x, data_format)

    if pool_mode == 'max':
        x = C.pooling(
            x,
            C.MAX_POOLING,
            pool_size,
            strides,
            auto_padding=[padding])
    elif pool_mode == 'avg':
        x = C.pooling(
            x,
            C.AVG_POOLING,
            pool_size,
            strides,
            auto_padding=[padding])
    else:
        raise ValueError('Invalid pooling mode: ' + str(pool_mode))

    return _postprocess_conv3d_output(x, data_format)


def relu(x, alpha=0., max_value=None):
    if alpha != 0.:
        negative_part = C.relu(-x)
    x = C.relu(x)
    if max_value is not None:
        x = C.clip(x, 0.0, max_value)
    if alpha != 0.:
        x -= alpha * negative_part
    return x


def dropout(x, level, noise_shape=None, seed=None):
    if level < 0. or level >= 1:
        raise ValueError('CNTK Backend: Invalid dropout level %s, '
                         'must be in interval [0, 1].' % level)
    return C.dropout(x, level)


def batch_flatten(x):
    # cntk's batch axis is not in shape,
    # so just flatten all the dim in x.shape
    dim = np.prod(x.shape)
    x = C.reshape(x, (-1,))
    x._keras_shape = (None, dim)
    return x


def softmax(x):
    return C.softmax(x)


def softplus(x):
    return C.softplus(x)


def softsign(x):
    return x / (1 + C.abs(x))


def categorical_crossentropy(output, target, from_logits=False):
    if from_logits:
        result = C.cross_entropy_with_softmax(output, target)
        # cntk's result shape is (batch, 1), while keras expect (batch, )
        return C.reshape(result, ())
    else:
        # scale preds so that the class probas of each sample sum to 1
        output /= C.reduce_sum(output, axis=-1)
        # avoid numerical instability with _EPSILON clipping
        output = C.clip(output, _EPSILON, 1.0 - _EPSILON)
        return -sum(target * C.log(output), axis=-1)


def sparse_categorical_crossentropy(output, target, from_logits=False):
    target = C.one_hot(target, output.shape[-1])
    target = C.reshape(target, output.shape)
    return categorical_crossentropy(output, target, from_logits)


class Function(object):
    def __init__(self, inputs, outputs, updates=[], **kwargs):
        self.placeholders = inputs
        self.trainer = None
        self.unrelated_updates = None
        self.updates = updates
        if len(updates) > 0:
            assert len(outputs) > 0
            self.loss = outputs[0]
            # need group update by gradient place holder
            u_ops = []
            unrelated_updates = []
            for update in updates:
                if isinstance(update, tuple):
                    if len(update) != 2:
                        raise NotImplementedError
                    else:
                        u = C.assign(update[0], update[1])
                else:
                    u = update

                if len(u.arguments) == 0:
                    u_ops.append(u)
                else:
                    unrelated_updates.append(u)

            update_func = C.combine([u.output for u in u_ops])

            grads = update_func.find_all_with_name('keras_grad_placeholder')

            u_list = []
            p_list = []
            for g in grads:
                if g in grad_parameter_dict:
                    p_list.append(grad_parameter_dict[g])
                    u_list.append(g)
                else:
                    raise ValueError('CNTK backend: when constructing trainer, '
                                     'found gradient node `%s` which is not '
                                     'related to any parameters in the model. '
                                     'Please double check how the gradient node '
                                     'is constructed.' % g)

            if len(u_list) > 0:
                learner = C.cntk_py.universal_learner(p_list, u_list, update_func)

                criterion = (
                    outputs[0],
                    outputs[1]) if len(outputs) > 1 else (
                    outputs[0],
                )
                self.trainer = C.trainer.Trainer(
                    outputs[0], criterion, [learner])
                self.trainer_output = tuple([f.output for f in criterion])
            elif len(u_ops) > 0:
                unrelated_updates.extend(u_ops)

            if len(unrelated_updates) > 0:
                self.unrelated_updates = C.combine([_.output for _ in unrelated_updates])

        if self.trainer is None:
            self.metrics_outputs = [f.output for f in outputs]
            self.metrics_func = C.combine(self.metrics_outputs)
        # cntk only could handle loss and 1 metric in trainer, for metrics more
        # than 2, need manual eval
        elif len(outputs) > 2:
            self.metrics_outputs = [f.output for f in outputs[2:]]
            self.metrics_func = C.combine(self.metrics_outputs)
        else:
            self.metrics_func = None

    @staticmethod
    def _is_input_shape_compatible(input, placeholder):
        if hasattr(input, 'shape') and hasattr(placeholder, 'shape'):
            num_dynamic = get_num_dynamic_axis(placeholder)
            input_shape = input.shape[num_dynamic:]
            placeholder_shape = placeholder.shape
            for i, p in zip(input_shape, placeholder_shape):
                if i != p and p != C.InferredDimension:
                    return False
        return True

    def __call__(self, inputs):
        global _LEARNING_PHASE
        assert type(inputs) in {list, tuple}
        feed_dict = {}
        for tensor, value in zip(self.placeholders, inputs):
            # cntk only support calculate on float, do auto cast here
            if (hasattr(value, 'dtype') and
               value.dtype != np.float32 and
               value.dtype != np.float64):
                value = value.astype(np.float32)
            if tensor == _LEARNING_PHASE:
                _LEARNING_PHASE.value = np.asarray(value)
            else:
                # in current version cntk can't support input with variable
                # length. Will support it in next release.
                if not self._is_input_shape_compatible(value, tensor):
                    raise ValueError('CNTK backend: The placeholder has been resolved '
                                     'to shape `%s`, but input shape is `%s`. Currently '
                                     'CNTK can not take variable length inputs. Please '
                                     'pass inputs that have a static shape.'
                                     % (tensor.shape, value.shape))
            feed_dict[tensor] = value

        updated = []
        if self.trainer is not None:
            input_dict = {}
            for argument in self.loss.arguments:
                if argument in feed_dict:
                    input_dict[argument] = feed_dict[argument]
                else:
                    raise ValueError('CNTK backend: argument %s is not found in inputs. '
                                     'Please double check the model and inputs in '
                                     '`train_function`.' % argument.name)

            result = self.trainer.train_minibatch(
                input_dict, self.trainer_output)

            assert(len(result) == 2)
            outputs = result[1]
            for o in self.trainer_output:
                updated.append(outputs[o])

        if self.metrics_func is not None:
            input_dict = {}
            for argument in self.metrics_func.arguments:
                if argument in feed_dict:
                    input_dict[argument] = feed_dict[argument]
                else:
                    raise ValueError('CNTK backend: metrics argument %s '
                                     'is not found in inputs. Please double '
                                     'check the model and inputs.' % argument.name)
            # Some ops (like dropout) won't be applied during "eval" in cntk.
            # They only evaluated in training phase. To make it work, call
            # "forward" method to let cntk know we want to evaluate them.from
            # But the assign ops won't be executed under this mode, that's why
            # we need this check.
            if self.unrelated_updates is None and _LEARNING_PHASE.value == 1.0:
                _, output_values = self.metrics_func.forward(
                    input_dict,
                    self.metrics_func.outputs,
                    (self.metrics_func.outputs[0],),
                    as_numpy=False)
            else:
                output_values = self.metrics_func.eval(input_dict, as_numpy=False)
            if isinstance(output_values, dict):
                for o in self.metrics_outputs:
                    value = output_values[o]
                    v = value.asarray()
                    updated.append(v)
            else:
                v = output_values.asarray()
                for o in self.metrics_outputs:
                    updated.append(v)

        if self.unrelated_updates is not None:
            input_dict = {}
            for argument in self.unrelated_updates.arguments:
                if argument in feed_dict:
                    input_dict[argument] = feed_dict[argument]
                else:
                    raise ValueError('CNTK backend: assign ops argument %s '
                                     'is not found in inputs. Please double '
                                     'check the model and inputs.' % argument.name)
            self.unrelated_updates.eval(input_dict, as_numpy=False)
        return updated


def function(inputs, outputs, updates=[], **kwargs):
    return Function(inputs, outputs, updates=updates, **kwargs)


def temporal_padding(x, padding=(1, 1)):
    assert len(padding) == 2
    num_dynamic_axis = _get_dynamic_axis_num(x)
    base_shape = x.shape
    if num_dynamic_axis > 0:
        assert len(base_shape) == 2
        x = _padding(x, padding, 0)
    else:
        assert len(base_shape) == 3
        x = _padding(x, padding, 1)
    return x


def _padding(x, pattern, axis):
    base_shape = x.shape
    if b_any([dim < 0 for dim in base_shape]):
        raise ValueError('CNTK Backend: padding input tensor with '
                         'shape `%s` contains non-specified dimension, '
                         'which is not supported. Please give fixed '
                         'dimension to enable padding.' % base_shape)
    if pattern[0] > 0:
        prefix_shape = list(base_shape)
        prefix_shape[axis] = pattern[0]
        prefix_shape = tuple(prefix_shape)
        x = C.splice(C.constant(value=0, shape=prefix_shape), x, axis=axis)
        base_shape = x.shape

    if pattern[1] > 0:
        postfix_shape = list(base_shape)
        postfix_shape[axis] = pattern[1]
        postfix_shape = tuple(postfix_shape)
        x = C.splice(x, C.constant(value=0, shape=postfix_shape), axis=axis)

    return x


def spatial_2d_padding(x, padding=((1, 1), (1, 1)), data_format=None):
    assert len(padding) == 2
    assert len(padding[0]) == 2
    assert len(padding[1]) == 2
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    num_dynamic_axis = _get_dynamic_axis_num(x)
    base_shape = x.shape
    if data_format == 'channels_first':
        if num_dynamic_axis > 0:
            assert len(base_shape) == 3
            x = _padding(x, padding[0], 1)
            x = _padding(x, padding[1], 2)
        else:
            assert len(base_shape) == 4
            x = _padding(x, padding[0], 2)
            x = _padding(x, padding[1], 3)
    else:
        if num_dynamic_axis > 0:
            assert len(base_shape) == 3
            x = _padding(x, padding[0], 0)
            x = _padding(x, padding[1], 1)
        else:
            assert len(base_shape) == 4
            x = _padding(x, padding[0], 1)
            x = _padding(x, padding[1], 2)
    return x


def spatial_3d_padding(x, padding=((1, 1), (1, 1), (1, 1)), data_format=None):
    assert len(padding) == 3
    assert len(padding[0]) == 2
    assert len(padding[1]) == 2
    assert len(padding[2]) == 2
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    num_dynamic_axis = _get_dynamic_axis_num(x)
    base_shape = x.shape
    if data_format == 'channels_first':
        if num_dynamic_axis > 0:
            assert len(base_shape) == 4
            x = _padding(x, padding[0], 1)
            x = _padding(x, padding[1], 2)
            x = _padding(x, padding[2], 3)
        else:
            assert len(base_shape) == 5
            x = _padding(x, padding[0], 2)
            x = _padding(x, padding[1], 3)
            x = _padding(x, padding[2], 4)
    else:
        if num_dynamic_axis > 0:
            assert len(base_shape) == 4
            x = _padding(x, padding[0], 0)
            x = _padding(x, padding[1], 1)
            x = _padding(x, padding[2], 2)
        else:
            assert len(base_shape) == 5
            x = _padding(x, padding[0], 1)
            x = _padding(x, padding[1], 2)
            x = _padding(x, padding[2], 3)
    return x


def one_hot(indices, nb_classes):
    return C.one_hot(indices, nb_classes)


def get_value(x):
    if isinstance(
            x,
            C.variables.Parameter) or isinstance(
            x,
            C.variables.Constant):
        return x.value
    else:
        return eval(x)


def batch_get_value(xs):
    result = []
    for x in xs:
        if (isinstance(x, C.variables.Parameter) or
           isinstance(x, C.variables.Constant)):
            result.append(x.value)
        else:
            result.append(eval(x))
    return result


def set_value(x, value):
    if (isinstance(x, C.variables.Parameter) or
       isinstance(x, C.variables.Constant)):
        if isinstance(value, float):
            value = np.full(x.shape, value)
        x.value = value
    else:
        raise NotImplementedError


def print_tensor(x, message=''):
    return C.user_function(
        LambdaFunc(x,
                   when=lambda x: True,
                   execute=lambda x: print(message)))


def batch_set_value(tuples):
    for t in tuples:
        x = t[0]
        value = t[1]
        if isinstance(value, np.ndarray) is False:
            value = np.asarray(value)
        if isinstance(x, C.variables.Parameter):
            x.value = value
        else:
            raise NotImplementedError


def stop_gradient(variables):
    return C.stop_gradient(C.combine(variables))


def switch(condition, then_expression, else_expression):
    return C.element_select(condition,
                            then_expression,
                            else_expression)


def elu(x, alpha=1.):
    res = C.elu(x)
    if alpha == 1:
        return res
    else:
        return C.element_select(C.greater(x, 0), res, alpha * res)


def in_top_k(predictions, targets, k):
    _targets = C.one_hot(targets, predictions.shape[-1])
    result = C.classification_error(predictions, _targets, topN=k)
    return 1 - C.reshape(result, shape=())


def conv2d_transpose(x, kernel, output_shape, strides=(1, 1),
                     padding='valid', data_format=None):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    x = _preprocess_conv2d_input(x, data_format)
    kernel = _preprocess_conv2d_kernel(kernel, data_format)
    padding = _preprocess_border_mode(padding)
    strides = (1,) + strides
    # cntk output_shape does not include batch axis
    output_shape = output_shape[1:]
    # in keras2, need handle output shape in different format
    if data_format == 'channels_last':
        shape = list(output_shape)
        shape[0] = output_shape[2]
        shape[1] = output_shape[0]
        shape[2] = output_shape[1]
        output_shape = tuple(shape)

    x = C.convolution_transpose(
        kernel,
        x,
        strides,
        auto_padding=[
            False,
            padding,
            padding],
        output_shape=output_shape)
    return _postprocess_conv2d_output(x, data_format)


def identity(x):
    return C.alias(x, name=('%s_alias' % (x.name)))


def _preprocess_conv2d_input(x, data_format):
    if data_format == 'channels_last':
        # TF uses the last dimension as channel dimension,
        # instead of the 2nd one.
        # TH input shape: (samples, input_depth, rows, cols)
        # TF input shape: (samples, rows, cols, input_depth)
        x = C.transpose(x, (2, 0, 1))
    return x


def _preprocess_conv2d_kernel(kernel, data_format):
    # As of Keras 2.0.0, all kernels are normalized
    # on the format `(rows, cols, input_depth, depth)`,
    # independently of `data_format`.
    # CNTK expects `(depth, input_depth, rows, cols)`.
    kernel = C.transpose(kernel, (3, 2, 0, 1))
    return kernel


def _preprocess_border_mode(padding):
    if padding == 'same':
        padding = True
    elif padding == 'valid':
        padding = False
    else:
        raise ValueError('Invalid border mode: ' + str(padding))
    return padding


def _postprocess_conv2d_output(x, data_format):
    if data_format == 'channels_last':
        x = C.transpose(x, (1, 2, 0))
    return x


def _preprocess_conv3d_input(x, data_format):
    if data_format == 'channels_last':
        # TF uses the last dimension as channel dimension,
        # instead of the 2nd one.
        # TH input shape: (samples, input_depth, conv_dim1, conv_dim2, conv_dim3)
        # TF input shape: (samples, conv_dim1, conv_dim2, conv_dim3,
        # input_depth)
        x = C.transpose(x, (3, 0, 1, 2))
    return x


def _preprocess_conv3d_kernel(kernel, dim_ordering):
    kernel = C.transpose(kernel, (4, 3, 0, 1, 2))
    return kernel


def _postprocess_conv3d_output(x, dim_ordering):
    if dim_ordering == 'channels_last':
        x = C.transpose(x, (1, 2, 3, 0))
    return x


def _get_dynamic_axis_num(x):
    if hasattr(x, 'dynamic_axes'):
        return len(x.dynamic_axes)
    else:
        return 0


def _contain_seqence_axis(x):
    if _get_dynamic_axis_num(x) > 1:
        return x.dynamic_axes[1] == C.Axis.default_dynamic_axis()
    else:
        return False


def get_num_dynamic_axis(x):
    return _get_dynamic_axis_num(x)


def _reduce_on_axis(x, axis, reduce_fun_name):
    if isinstance(axis, list):
        for a in axis:
            if isinstance(a, C.Axis) and a != C.Axis.default_batch_axis():
                x = getattr(C.sequence, reduce_fun_name)(x, a)
            else:
                x = getattr(C, reduce_fun_name)(x, a)
    else:
        x = getattr(C, reduce_fun_name)(x, axis)
    return x


def _reshape_sequence(x, time_step):
    tmp_shape = list(int_shape(x))
    tmp_shape[1] = time_step
    return reshape(x, tmp_shape)


def local_conv1d(inputs, kernel, kernel_size, strides, data_format=None):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    stride = strides[0]
    kernel_shape = int_shape(kernel)
    output_length, feature_dim, filters = kernel_shape

    xs = []
    for i in range(output_length):
        slice_length = slice(i * stride,
                             i * stride + kernel_size[0])
        xs.append(reshape(inputs[:, slice_length, :],
                          (-1, 1, feature_dim)))
    x_aggregate = concatenate(xs, axis=1)
    # transpose kernel to output_filters first, to apply broadcast
    weight = permute_dimensions(kernel, (2, 0, 1))
    # Shape: (batch, filters, output_length, input_length * kernel_size)
    output = x_aggregate * weight
    # Shape: (batch, filters, output_length)
    output = sum(output, axis=3)
    # Shape: (batch, output_length, filters)
    return permute_dimensions(output, (0, 2, 1))


def local_conv2d(inputs,
                 kernel,
                 kernel_size,
                 strides,
                 output_shape,
                 data_format=None):
    if data_format is None:
        data_format = image_data_format()
    if data_format not in {'channels_first', 'channels_last'}:
        raise ValueError('Unknown data_format ' + str(data_format))

    stride_row, stride_col = strides
    output_row, output_col = output_shape
    kernel_shape = int_shape(kernel)
    _, feature_dim, filters = kernel_shape
    xs = []

    for i in range(output_row):
        for j in range(output_col):
            slice_row = slice(i * stride_row,
                              i * stride_row + kernel_size[0])
            slice_col = slice(j * stride_col,
                              j * stride_col + kernel_size[1])
            if data_format == 'channels_first':
                xs.append(reshape(inputs[:, :, slice_row, slice_col],
                                  (-1, 1, feature_dim)))
            else:
                xs.append(reshape(inputs[:, slice_row, slice_col, :],
                                  (-1, 1, feature_dim)))
    x_aggregate = concatenate(xs, axis=1)
    # transpose kernel to put filters first
    weight = permute_dimensions(kernel, (2, 0, 1))
    # shape: batch, filters, output_length, input_length * kernel_size
    output = x_aggregate * weight
    # shape: batch, filters, output_length
    output = sum(output, axis=3)
    # shape: batch, filters, row, col
    output = reshape(output,
                     (-1, filters, output_row, output_col))

    if data_format == 'channels_last':
        # shape: batch, row, col, filters
        output = permute_dimensions(output, (0, 2, 3, 1))

    return output


class ReshapeBatch(C.ops.functions.UserFunction):
    def __init__(self, input, shape, name='reshape_with_batch'):
        super(ReshapeBatch, self).__init__([input], as_numpy=False, name=name)
        self.from_shape = input.shape
        self.target_shape = shape

    def infer_outputs(self):
        batch_axis = C.Axis.default_batch_axis()
        return [
            C.output_variable(
                self.target_shape,
                self.inputs[0].dtype,
                [batch_axis])]

    def forward(self, arguments, device=None, outputs_to_retain=None):
        num_element = arguments.shape()[0] * np.prod(np.asarray(self.from_shape))
        num_static_element = np.prod(np.asarray(self.target_shape))
        num_batch = int(num_element / num_static_element)
        result = arguments.data().as_shape((num_batch,) + self.target_shape)
        return None, C.cntk_py.Value(result)

    def backward(self, state, root_gradients):
        grad_array_view = root_gradients.data()
        num_element = root_gradients.shape()[0] * np.prod(np.asarray(self.target_shape))
        num_static_element = np.prod(np.asarray(self.from_shape))
        num_old_batch = int(num_element / num_static_element)
        return C.cntk_py.Value(
            grad_array_view.as_shape(
                (num_old_batch,) + self.from_shape))


class LambdaFunc(C.ops.functions.UserFunction):
    def __init__(self,
                 arg,
                 when=lambda arg: True,
                 execute=lambda arg: print(arg),
                 name=''):
        self.when = when
        self.execute = execute

        super(LambdaFunc, self).__init__([arg], name=name)

    def infer_outputs(self):
        return [
            C.output_variable(
                self.inputs[0].shape,
                self.inputs[0].dtype,
                self.inputs[0].dynamic_axes)]

    def forward(self, argument, device=None, outputs_to_retain=None):
        if self.when(argument):
            self.execute(argument)

        return None, argument

    def backward(self, state, root_gradients):
        return root_gradients
