#: The default number to seed random number generators
baseseed = 0

#: The default number of iterations for minimizers that use sampling.
iterations = 10000

#: Display the minimizer's state to the screen
print_status = True

# Grid Minimizer options

#: If the total number of points aren't specified, calculate them based on the
#: number of adjustable parameters and the points per adjustable parameter.
gr_points_per_parameter = 10

#: The default kwargs to send to the minimizer for the basin hopping minimizer
#: (:class:`mollib.minimizer.BHMinimizer`)
bh_minimizer_kwargs = {'method': 'Nelder-Mead'}

#: The default number of steps without finding a new minimum before stopping
#: the minimum search
bh_niter_success = 100
