from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import *
import numpy as np


class Model:
    """Wound velocity model.

    The model is based on Gaussian Process Regression (GPR)
    and numerical differentiation. The GPR uses scikit-learn GPR class   
    ``sklearn.gaussian_process.GaussianProcessRegressor``.
    
    Parameters
    ----------
    area_kwargs : dictionary
        The keyword arguments to the area GPR model.
    perimeter_kwargs : dictionary
        The keyword arguments to the perimeter GPR model.

    Attributes
    -----------
    area : area model
        Instances of GaussianProcessRegressor from scikit-learn.
    perimeter : perimeter model
        Instances of GaussianProcessRegressor from scikit-learn.
    time : sequence
        Sequence of the input time points. Defined when fitted.

    Notes
    -----
    The keyword argument ``kernel`` is specifying the covariance function
    of the GPR models handling the area and perimeter. The default kernel 
    is a sum of a linear and squared dotproduct kernel.
    See `scikit-learn
    <http://www.scikit-learn.org/stable/modules/gaussian_process.html>`_
    for the different kernels that can be used. Note that the kernel
    hyperparameters are optimized during fitting.

    """
    def __init__(self, area_kwargs = None, perimeter_kwargs = None):
        kernel = ConstantKernel() + 1*DotProduct()**2
        kwargs = {'kernel': kernel,
                  'n_restarts_optimizer': 5,   
                  'normalize_y': True} 
        if area_kwargs is None:
            area_kwargs = kwargs
        if perimeter_kwargs is None:
            perimeter_kwargs = kwargs 

        self.area = GaussianProcessRegressor(**area_kwargs)
        self.perimeter = GaussianProcessRegressor(**perimeter_kwargs)
        self.time = None

    def fit(self, wounds):
        """Fitting the velocity model to wound data.
       
        Parameters
        ----------
        wounds : sequence of dictionaries
            A sequence of wound dictionaries representing an experimental
            time series of the wound healing assay, as returned
            by :func:`detect`.
            The area, perimeter and time point of each wound is used to 
            fit the overall velocity model. All these attributes should
            be positive scalars.

        Returns
        -------
        self : Model
            The velocity model in a fitted state.

        """
        wounds = sorted(wounds, key=lambda x: x['time'])
        self.time = np.array([x['time'] for x in wounds])
        time = self.time.reshape(-1,1)
        self.area.alpha = np.array([x['area_variance'] for x in wounds])
        self.area.fit(time, np.array([x['area'] for x in wounds]))
        self.perimeter.alpha = np.array([x['perimeter_variance']
                                         for x in wounds])
        self.perimeter.fit(time, np.array([x['perimeter']
                                           for x in wounds]))
        return self

    def predict(self, time, dt=.1, return_std=False):
        """Predicting a velocity curve of a wound healing experiment.

        In addition to the mean of the predictive distribution, also its
        standard deviation (return_std=True) can be requested.

        Parameters
        -----------
        time : sequence
            Desired time points of the velocity prediction. Should be
            positive.
        dt : scalar
            The time interval for calculating velocity.
        return_std : bool
            Whether to include the standard deviation of the prediction   
            or not.
        
        Returns
        -------
        velocity, [vel_std] : 1d arrays
            Velocity and (optionally) it's standard deviation.
            Returned either one array or (if return_std=True) as a tuple
            (velocity, vel_std).

        """
        time = np.asarray(time, dtype=float).round(4)
        linear_time = np.arange(time.min(), time.max(), dt, dtype=float).round(4)
        if len(linear_time) < 10:
            raise ValueError('choose a smaller dt for numeric stability')
        ptime = np.union1d(time, linear_time)
        area, a_std = self.area.predict(ptime.reshape(-1,1), return_std=True)
        peri, p_std = self.perimeter.predict(ptime.reshape(-1,1), return_std=True)
        da = np.gradient(area) / np.gradient(ptime)
        resolution = np.mean(np.gradient(self.time))
        da_std = np.sqrt(2)*a_std / resolution
        vel = -da / peri
        frac_q = (da_std/da)**2 + (p_std/peri)**2
        vel_std = np.abs(vel) * np.sqrt(frac_q)
        mask = np.in1d(ptime, time)
        velocity = vel[mask][np.argsort(time)]
        v_std = vel_std[mask][np.argsort(time)]
        if return_std:
            return velocity, v_std
        return velocity
