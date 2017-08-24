'''
Imported Methods and Function for MCMC
'''

import numpy as np
from scipy.spatial import distance
from scipy import special
from scipy import sparse
import matplotlib.cm as cm
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import *
from plotly import tools
from scipy import integrate
import itertools
import scipy.linalg as LA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import collections as mc
from scipy.spatial import SphericalVoronoi
import networkx as nx
from scipy.interpolate import griddata
from matplotlib import colors as c
import sys


def design(theta, phi):
    '''
    Initial condition to project on surface of sphere:
    inputs: theta = [0, 2*pi], phi = [0, pi]
    output: values of heat-map at that point
    use: input into harmonic analysis function for finding fourier coefficients
    '''
    region1 = 5*np.pi/6<theta<7*np.pi/6
    if (region1):
        return 1
    else:
        return -1

'''Parameters'''
mode_limit = 9
s_param = 5
n = 1000
p = 200
beta = 0.06
alpha = 1
t = .1
gamma = .1 #noise factor for observation map
epsilon = 2/(n**(1/4))
truncation_point = int(70/2000 * n) #limits the number of modes in the discrete case for MCMC 
initial_function = design


'''Coordinate System'''
theta = np.linspace(0, 2*np.pi, 300)
phi = np.linspace(0, np.pi, 300) 
phi, theta = np.meshgrid(phi, theta)

'''Cartesian coordinates of the meshgrid above'''
X = np.sin(phi) * np.cos(theta)
Y = np.sin(phi) * np.sin(theta)
Z = np.cos(phi)

def to_integrate(theta, phi, k,l, version, projected_design):
    '''
    Function combining correctly normalized spherical harmonics with
    the projected design so that inner products can be computed:
    inputs: theta = [0, 2*pi], phi = [0, pi], k = order of s-harm, l = degree of s-harm
            version= cos or sin to distinguish from real/imag versions
            projected_design = function to take inner product with
    output: a combination of functions
    use: used in harmonic analysis
    '''
    if (k==0):
        coefficient_to_int = np.sqrt(4*np.pi)
    else:
        coefficient_to_int = np.sqrt(8*np.pi)
    if version == 'cos':
        harmonic = special.sph_harm(k,l,theta,phi).real * np.sin(phi)
    elif version == 'sin':
        harmonic = special.sph_harm(k,l,theta,phi).imag * np.sin(phi)
    return (coefficient_to_int * harmonic * projected_design(theta, phi))

def harmonic_analysis(projected_design):
    '''
    Function which iterates through degrees and orders of spherical harmonics, taking
    inner products with a given function to produce a fourier decomposition:
    inputs: projected_design = function for which the coefficients are desired
    output: 3D numpy array of fourier coefficients 
    use: coefficients allow the creation of a structured function on the sphere
    '''
    to_return  = np.empty((mode_limit, mode_limit, 2))
    for l in range(mode_limit):
        for k in range(l+1):
            def wrapper_cos(theta, phi):
                return to_integrate(theta, phi, k, l, 'cos', projected_design)
            def wrapper_sin(theta, phi):
                return to_integrate(theta, phi, k, l, 'sin', projected_design)
            fourier_coefficient_cos = integrate.nquad(wrapper_cos,[[0, 2* np.pi], [0, np.pi]])[0]
            fourier_coefficient_sin = integrate.nquad(wrapper_sin,[[0, 2* np.pi], [0, np.pi]])[0] 
            to_return[k,l, 0] = fourier_coefficient_cos
            to_return[k,l, 1] = fourier_coefficient_sin
    return to_return
    
def function_harm(theta, phi, k, l, version):
    '''
    Normalization function for the vectorization of the sphereical harmonics:
    inputs: theta = [0, 2*pi], phi = [0, pi], k = order of s-harm, l = degree of s-harm
            version= cos or sin to distinguish from real/imag versions
    output: normalized spherical harmonic functions
    use: construction of fourier series representation of a function
    '''
    if version == 'cos':
        harmonic = special.sph_harm(k, l, theta, phi).real
    elif version == 'sin':
        harmonic = special.sph_harm(k, l, theta, phi).imag
    if (k == 0):
        coefficient = np.sqrt(4*np.pi)
    else:
        coefficient = np.sqrt(8*np.pi)
    return (coefficient * harmonic)
    
def composition(time, coefficients):
    '''
    Making a fourier series representation from given coefficients, and pushing it through
    the heat equation to time T = t
    inputs: time = how long to run heat equation, coefficients = list of fourier coefficients
    outputs: (300,300) map of values on surface of sphere
    use: used to visualize output of continuous MCMC 
    '''
    to_return = []
    for l in range(mode_limit):
        lambda_lap = l*(l+1)
        decay = np.exp(-(lambda_lap) * time)
        to_return.append(coefficients[0,l, 0] * function_harm(theta, phi, 0, l, 'cos') * decay)
        for k in range(1, (l + 1)):
            term_one = (coefficients[k,l,0] * function_harm(theta, phi, k, l, 'cos') * decay)
            term_two = (coefficients[k,l,1] * function_harm(theta, phi, k, l, 'sin') * decay)
            to_return.append(term_one)
            to_return.append(term_two)
    return np.sum(to_return, axis = 0)

def n_dim_uniform(num_points, dim):
    '''
    Sampling uniform points on surface of sphere in R^n
    inputs: num_points = points to sample, dim = dimension of sphere
    output: set of sampled point in cartesian coordinates
    use: gettin samples!
    '''
    indicies = range(num_points)
    unnormalized_points = np.random.normal(0,1,(num_points, dim))
    normalization_factor = np.reshape((np.sqrt(np.sum(unnormalized_points**2, axis = 1))), (num_points,1))
    to_return = np.divide(unnormalized_points,normalization_factor)
    return to_return

def observation(draw, num):
    draw += np.random.normal(0,gamma**2,draw.shape)
    cart_uniform = n_dim_uniform(num, 3)
    phi_samples = np.arccos(cart_uniform[:,2])
    theta_samples = np.arctan2(cart_uniform[:,1], cart_uniform[:,0])
    def tan_fix(angle):
        if angle < 0:
            return 2*np.pi + angle
        else:
            return angle 
    theta_samples = np.array([tan_fix(x) for x in theta_samples])
    theta_index = np.array([int(x) for x in ((theta_samples/(2*np.pi)) * 300)])
    phi_index = np.array([int(x) for x in ((phi_samples/np.pi) * 300)])
    y_vals = np.array([draw[th, ph] for th, ph in zip(theta_index, phi_index)])
    to_return_cart = np.concatenate((np.reshape(cart_uniform[:,0], (num, 1)),
                                     np.reshape(cart_uniform[:,1], (num, 1)),
                                     np.reshape(cart_uniform[:,2], (num, 1)),
                                     np.reshape(y_vals, (num, 1))), axis  = 1)
    to_return_sphere = np.concatenate((np.reshape(theta_samples, (num, 1)),
                                       np.reshape(phi_samples, (num, 1)),
                                       np.reshape(y_vals, (num, 1))), axis = 1)
    return (to_return_cart, to_return_sphere)

def make_graph_laplacian(n, s, dim, point_cloud, eps):
    '''
    Used to construct L=D-W matrix for discrete approximations for graph 
    laplacian eigenvalues and eigenvectors
    inputs: n = number of sample points, s = smoothing parameter
            dim = dimension of sphere to sample on, point_cloud = points to structure
            eps = epsilon for making graph edges
    output: graph laplacian matrix 
    use: eveything!!
    '''
    points = point_cloud[:,0:3]
    relative_distances = (distance.cdist(points,points, metric = 'euclidean')) 
    W = np.zeros((n,n))
    epsilon = eps
    row = 0
    col = 1
    weight = (4/(np.pi*(n)*(epsilon**4))) # removed square on n here...
    #the following code iterates through the upper triangular matrix
    while (row < (n - 1)):
        while (col < n):
            r = relative_distances[row, col]
            if (r <= epsilon):
                W[row,col] = weight
            col += 1
        row += 1
        col = row + 1
    W += W.T + (weight*np.eye(n))
    D = np.diag(np.sum(W, axis = 1))
    num_connections = np.sum((W/weight), axis = 0)
    #print('log(n) = ', np.log(n))
    #print('each node has at least ', np.min(num_connections), ' connections')
    #print('each node has on average ', np.mean(num_connections), ' connections')
    to_return = D-W
    return to_return

def L_2_norm(point):
    '''L^2 Norm for Points, self explanitory'''
    return np.sqrt(np.sum(point**2))

def produce_eigenvalues(number_of_val):
    '''
    Function to return set of eigenvalues from the spherical continuous laplacian
    inputs: number_of_vals = degree of eigenvalues to output
    output: set of eigenvalues 
    use: for plotting continuous vs discrete eigenvalues
    '''
    to_return = []
    for eigen in range(number_of_val):
        multiplicity = (2*eigen) + 1
        for multi in range(multiplicity):
            to_return.append(eigen*(eigen+1))
    return to_return

def compose (coefficients):
    basis_length = np.sum([2*(x)+1 for x in range(0,mode_limit)])
    basis = np.empty((basis_length, len(theta), len(phi)))
    counter = 0
    for l in range(mode_limit):
        basis[counter,:,:] = np.sqrt(4*np.pi)*special.sph_harm(0, l, theta, phi).real
        counter += 1
        for k in range(1, l+1):
            to_add = np.sqrt(8*np.pi)*special.sph_harm(k, l, theta, phi) 
            basis[counter,:, :] = to_add.real
            counter+=1 
            basis[counter,:, :] = to_add.imag
            counter+=1
    return np.sum(np.array([coefficients[x]*basis[x,:,:] for x in range(basis.shape[0])]), axis = 0)


s_points = np.empty((90000,2))
counter = 0
for i in range(300):
    for j in range(300):
        s_points[counter,0],s_points[counter,1] = theta[i,0], phi[0,j]
        counter += 1

cart = np.empty((90000,3))
for i,row in enumerate(s_points):
    x = np.sin(row[1]) * np.cos(row[0])
    y = np.sin(row[0]) * np.sin(row[1])
    z = np.cos(row[1])
    cart[i,0],cart[i,1],cart[i,2] = x,y,z
    
def k_nearest_neighbors(discreteMCMC,k,coords):
    to_return = np.empty((300,300))
    distances = (distance.cdist(coords, cart, metric = 'euclidean')).T 
    order = np.argsort(distances)[:,0:k]
    counter = 0
    for index, cell in np.ndenumerate(to_return):
        closest = np.array(order[counter,:])
        distance_norm = np.sum(distances[counter,closest])
        avg_val = np.empty(len(closest))
        for i,ind in enumerate(closest):
            weight = distances[counter, ind]/distance_norm
            avg_val[i] = weight * discreteMCMC[ind]
        to_return[index] = np.sum(avg_val)
        counter += 1
    return to_return

def continuum_pCN(alpha, beta, s_param, y, cycles, burn_in):
    to_avg = []
    y_vals = y[:,2]
    obs_theta = y[:,0]
    obs_phi = y[:,1]
    basis_length = np.sum([2*(x)+1 for x in range(0,mode_limit)])
    basis = np.empty((basis_length, y.shape[0]))
    lambda_C = np.array(list(itertools.chain.from_iterable([(2*(x)+1)*[(alpha + x*(x+1))**(-s_param/4)] 
                         for x in range(mode_limit)])))
    counter = 0
    for l in range(mode_limit):
        basis[counter,:] = np.sqrt(4*np.pi)*special.sph_harm(0, l, obs_theta, obs_phi).real
        counter += 1
        for k in range(1, l+1):
            to_add = np.sqrt(8*np.pi)*special.sph_harm(k,l,obs_theta,obs_phi) 
            basis[counter,:] = to_add.real
            counter+=1 
            basis[counter,:] = to_add.imag
            counter+=1
    forward_map_vec = np.array(list(itertools.chain.from_iterable([(2*(i) + 1)*[np.exp(-1*float(i)*(float(i)+1)*t)]
                                                          for i in range(mode_limit)])))
    current_coefficients = np.random.normal(0,1,basis_length)
    current_values = np.dot((forward_map_vec * current_coefficients), basis)
    current_phi = (1/(2*gamma**2)) * L_2_norm(y_vals-current_values)**2
    acceptance_rate = 0
    for i in range(burn_in): 
        Xi = np.random.normal(0,1,basis_length) * lambda_C
        proposed_coefficients = (np.sqrt((1-beta**2)) * current_coefficients + beta * Xi)
        proposal = np.dot((proposed_coefficients * forward_map_vec), basis)
        proposed_phi = (1/(2*gamma**2)) * L_2_norm(y_vals - proposal)**2
        distance = np.exp(current_phi - proposed_phi)
        if (np.random.uniform(0,1) <= np.min(np.array([1, distance]))):
            current_coefficients = proposed_coefficients
            current_phi = proposed_phi
    for i in range(cycles - burn_in):
        Xi = np.random.normal(0,1,basis_length) * lambda_C
        proposed_coefficients = (np.sqrt((1-beta**2)) * current_coefficients + beta * Xi)
        proposal = np.dot((proposed_coefficients * forward_map_vec), basis)
        proposed_phi = (1/(2*gamma**2)) * L_2_norm(y_vals - proposal)**2
        distance = np.exp(current_phi - proposed_phi)
        if (np.random.uniform(0,1) <= np.min(np.array([1, distance]))):
            current_coefficients = proposed_coefficients
            current_phi = proposed_phi
            acceptance_rate += 1
        if (i%100 == 0):
            #to_avg[int(i/100)] = (np.dot(current_coefficients, basis))
            to_avg.append(current_coefficients)
    print(acceptance_rate/(cycles - burn_in))
    return compose(np.sum(to_avg, axis = 0)/(len(to_avg)))
   
def graph_pCN(alpha, beta, s_param, y, cycles, e_vals, e_vecs, burn_in):
    '''
    graph pCN algorithm
    inputs: alpha = 1 here, beta = step size, s_param = smoothing parameter 
            y = observed data to condition on, cycles = markov chain length,
            e_vals = eigenvalues of graph laplacian, e_vecs = eigenvectors of graph
            laplacian, burn_in = number of burn in cycles
    output: length n array of heat values defined on a points dictated by initial observation
    use: MCMC
    '''
    #to_avg = np.empty((100, n))
    to_avg = []
    y_vals = y[:,2]
    e_vals *= 2/e_vals[1]
    basis = (e_vecs.T * np.sqrt(n))[0:truncation_point,:] #truncation point limits basis size
    current_coefficients = np.ones((len(e_vals[0:truncation_point])))
    forward_map = np.exp(-e_vals[0:truncation_point] * t)
    eigenvals_operator = (alpha + e_vals[0:truncation_point])**(-s_param/4)
    acceptance_rate = 0
    for i in range(burn_in): 
        phi_current = np.dot((forward_map * current_coefficients), basis)
        Xi = np.random.normal(0,1,len(e_vals[0:truncation_point])) * eigenvals_operator
        proposal = np.sqrt((1-beta**2)) * current_coefficients + beta * Xi
        phi_draw = np.dot((proposal * forward_map), basis)
        distance = np.exp((1/(2*gamma**2))*(L_2_norm(y_vals - phi_current[0:p])**2 - L_2_norm(y_vals - phi_draw[0:p])**2))
        if (np.random.uniform(0,1) <= np.min(np.array([1, distance]))):
            current_coefficients = proposal
    for i in range(cycles - burn_in):
        phi_current = np.dot((forward_map * current_coefficients), basis) 
        Xi = np.random.normal(0,1,len(e_vals[0:truncation_point])) * eigenvals_operator
        proposal = np.sqrt((1-beta**2)) * current_coefficients + beta * Xi
        phi_draw = np.dot((proposal * forward_map), basis)
        distance = np.exp((1/(2*gamma**2))*(L_2_norm(y_vals - phi_current[0:p])**2 - L_2_norm(y_vals - phi_draw[0:p])**2))
        if (np.random.uniform(0,1) < np.min(np.array([1, distance]))):
            current_coefficients = proposal
            acceptance_rate += 1
        if (i%100 == 0):
            #to_avg[int(i/100)] = (np.dot(current_coefficients, basis))
            to_avg.append(current_coefficients)
    print('acceptance rate is ', acceptance_rate/(cycles - burn_in))
    return np.dot((np.sum(to_avg, axis = 0)/(len(to_avg))) , basis)

spectral_cmap = cm.get_cmap('Spectral')
spectral_rgb = []
norm = c.Normalize(vmin=0, vmax=255)

for i in range(0, 255):
    k = c.colorConverter.to_rgb(spectral_cmap(norm(i)))
    spectral_rgb.append(k)

    
def matplotlib_to_plotly(cmap, pl_entries):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []
    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])
    return pl_colorscale

spectral = matplotlib_to_plotly(spectral_cmap, 255)