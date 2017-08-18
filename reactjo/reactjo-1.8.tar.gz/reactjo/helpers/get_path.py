from reactjo.helpers.config_manipulation import get_cfg

# Organization:

# root
#	/env
# 	/reactjorc
# 		/config.json
# 		/extensions
# 			/react-django
# 				/assets/
# 				/helpers/
# 				/entry.py
# 	/project
# 		/manage.py
# 		/app
# 			/templates
# 				/home.html
# 				/react
#					/components
# 					/containers
# 						/Home.js
# 			/static
# 			/urls.py
# 			/views.py
# 			/settings.py (root app only)
# 	        /webpack.config.js
# 	        /package.json
# 	        /redux
# 	        	/store
# 			/reducers
# 			/actions

# ROOT
def root_path():
	return get_cfg()['paths']['root']

# REACTJORC
def reactjorc_path(x, f = ''):
	return get_cfg()['paths']['reactjorc'] + '/' + f

def rc_path(x, f = ''):
	return reactjorc_path(x,f)

def extensions_path(x, f = ''):
	return get_cfg()['paths']['reactjorc'] + '/extensions/' + x + '/' + f

def ext_path(x, f = ''):
	return extensions_path(x,f)
#f(p.assets_path() + 'templates/home.html', 'f', {'title': name})

def assets_path(x = 'react-django', f = ''):
	return ext_path(x) + 'assets/' + f


# PROJECT
def project_path(f = ''):
	return get_cfg()['paths']['project'] + '/' + f

def prj_path(f = ''):
	return project_path(f)

def settings_path():
	return get_cfg()['paths']['settings']

# APP
def app_path(a, f = ''):
	return prj_path() + a + '/' + f

def templates_path(a, f = ''):
	return app_path(a) + 'templates/' + f

def tpl_path(a,f = ''):
	return templates_path(a,f)

def react_path(a, f = ''):
	return templates_path(a) + 'react/' + f

def components_path(a, f = ''):
	return react_path(a) + 'components/' + f

def containers_path(a, f = ''):
	return react_path(a) + 'containers/' + f

def urls_path(a):
	return app_path(a) + 'urls.py'

def views_path(a):
	return app_path(a) + 'views.py'


# The only reason to use static would be webpack output paths... not scaffolding.
# Don't do that. They need to be relative paths.
# def static_path(a, f = ''): pass

def webpack_path():
	return project_path('webpack.config.js')

def package_json_path():
	return project_path('package.json')

def babelrc_path():
	return project_path('.babelrc')

def redux_path(f = ''):
	return project_path('redux/') + f

def store_path(f = ''):
	return redux_path('store/') + f

def actions_path(f = ''):
	return redux_path('actions/') + f

def reducers_path(f = ''):
	return redux_path('reducers/') + f
