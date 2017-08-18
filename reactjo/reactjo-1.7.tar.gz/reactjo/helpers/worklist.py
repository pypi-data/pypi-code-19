from reactjo.helpers.config_manipulation import get_cfg, set_cfg

def worklist(string = None):
	cfg = get_cfg()
	if not 'worklist' in cfg:
		cfg['worklist'] = []

	if string == None:
		print('Here\'s what Reactjo just did for you:')
		print('====================')
		for item in cfg['worklist']:
			print('- ' + item)
		print('Enjoy! :-)')
		cfg['worklist'] = []
		set_cfg(cfg)

	else:
		cfg['worklist'].append(string)
		set_cfg(cfg)