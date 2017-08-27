"""which module to find executables"""
from os import X_OK, access, environ

def which(prog):
	"""which function like the linux 'which' program"""
	for path in environ['PATH'].split(':'):
		if access('%s/%s'%(path, prog), X_OK):
			return '%s/%s'%(path, prog)
