# encoding: utf-8
import routes.mapper
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.base as base

def get_non_empty_groups():
    '''Retorna uma lista dos temas.'''
    all_groups = toolkit.get_action('group_list')(
        data_dict={'all_fields': True})
    groups = []
    for group in all_groups:
        if group['package_count'] > 0:
            groups.append(group)
    return groups


class Govdf_ThemePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.ITemplateHelpers)


    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'govdf_theme')

    def before_map(self, route_map):
        with routes.mapper.SubMapper(route_map, controller='ckanext.govdf_theme.plugin:Govdf_ThemeController') as m:

            m.connect('perguntas', '/perguntas', action='asks')
            m.connect('outros_dados', '/outros-dados', action='data_sugestions')
            m.connect('contato', '/contato', action='contact')
            m.connect('dados_abertos', '/dados-abertos', action='what_is_op')
            m.connect('mapa', '/mapa', action='map')
        return route_map

    def after_map(self, route_map):
        return route_map

    def get_helpers(self):
    	'''Registra a função get_non_empty_groups() como função helper do template'''
    	return {'govdf_theme_get_non_empty_groups': get_non_empty_groups
                }

class Govdf_ThemeController(base.BaseController):
    # Aqui são descritas as actions
    def asks(self):
        return base.render('content/perguntas.html')

    def data_sugestions(self):
        return base.render('content/outros-dados.html')

    def contact(self):
        return base.render('content/contato.html')

    def what_is_op(self):
        return base.render('content/dados-abertos.html')

    def map(self):
        return base.render('content/mapa.html')
