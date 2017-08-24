'''
Main file to Run MCMC From
'''
import sys
from task_mcmc.thabo_and_zach_work import * 

scene = Scene(
        xaxis=XAxis(
            visible =False,
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=False,
            backgroundcolor='rgb(230, 230,230)'
        ),
        yaxis=YAxis(
            visible = False,
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=False,
            backgroundcolor='rgb(230, 230,230)'
        ),
        zaxis=ZAxis(
            visible = False,
            gridcolor='rgb(255, 255, 255)',
            zerolinecolor='rgb(255, 255, 255)',
            showbackground=False,
            backgroundcolor='rgb(230, 230,230)'
        )
    )

layout = Layout(
    title='Graph on Sphere',
    scene=scene
)

mode_limit = 9
n = 1000
p = 200
t = 0.1
gamma = 0.2
cycles = 10000
s_param = 5
beta = 0.06
alpha = 1
epsilon = 2/(n**(1/4))
truncation_point = int(70/2000 * n)  
initial_function = design

def set_params():
	n = int(input('Enter n: ') or  '1000')
	p = int(input('Enter p: ') or '200')
	t = float(input('Enter t: ') or '0.1')
	gamma = float(input('Enter gamma: ') or '0.2')
	epsilon = 2/(n**(1/4))
	s_param = float(input('Enter s: ') or '5')
	cycles = int(input('Enter markov chain length: ') or '10000')
	beta = float(input('Enter beta: ') or '0.03')
	print('parameters set')

def main():
	set_params()
	harmonics = harmonic_analysis(initial_function)
	print('making initial condition')
	color_s = composition(0, harmonics)
	color_s_after_time = composition(t, harmonics)
	print('sampling points')
	n_cart, n_sphere = observation(composition(t, harmonics), n)
	p_cart, p_sphere = n_cart[0:p,:], n_sphere[0:p,:]
	g_laplacian = make_graph_laplacian(n, s_param, 3, n_cart, epsilon)
	print('making graph laplacian')
	e_vals, e_vecs = LA.eigh(g_laplacian)
	c_max = np.max(color_s)
	c_min = np.min(color_s)
	print('running MCMC')
	discrete = graph_pCN(1, beta, s_param, p_sphere, cycles, e_vals, e_vecs, int(cycles*.9))
	fig = tools.make_subplots(rows=1, cols=2,specs=[[{'is_3d': True}, {'is_3d': True}],])
	count = 0
	scenes = ['scene1','scene2']
	names = ['Initial Condition', 'Discrete MCMC']
	color_maps = [color_s, k_nearest_neighbors(discrete, 3, n_cart[:,0:3])]
	for i in range(1,3):
		fig.append_trace(dict(type='surface', x=X, y=Y, z=Z, cmin = c_min, hoverinfo = names[count],
                              	cmax = c_max, surfacecolor=color_maps[count], name = names[count], 
                              	scene=scenes[count], colorscale = spectral, showscale=True), 1, i)
		count += 1

	fig['layout'].update(title='Initial Condition and Discrete MCMC',
                     height=800, width=1400)
	for i in range(2):
		fig['layout'][scenes[i]].update(scene)
	print('plotting figures')
	plot(fig)


if __name__ == '__main__':
	main()
