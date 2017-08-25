from os import X_OK, access, environ

def which(prog):
	for path in environ['PATH'].split(':'):
		if access('%s/%s'%(path, prog), X_OK):
			return '%s/%s'%(path, prog)
