import os
import time
from sws_tags.sws_utils import decorators_lua
import logging
logger = logging.getLogger('sws-tags')

def max_sim_execs():
	'''
		Decorator to limit concurrents executions of the same method.
		Args:
			param1(string): key to limit.
			param2(int): maximun number of concurrents executions.
			param3(redis): reids instance.
			param4(int): windows size. (optional)
		Returns:
			int: 0 or 1. if returns 1 the method has to wait, when returns 0 the methos continues.
	'''
	'''

	Example:
		@max_sim_execs('estemetodo', 2, r)
	'''
	def p_decorate(func):
		def func_wrapper(*args, **kwargs):
			def check_set_size(redis, limit, key):
				if redis:
					items = redis.zcard(key)
				if items >= limit:
						logger.warning('Rate limiter is full')
			try:
				key, limit, redis, limit_time = args[0]._get_decorator_params()
			except:
				key = kwargs.pop('key', 'MAX_SIM_EXEC')
				limit = kwargs.pop('limit', 0)
				redis = kwargs.pop('redis', None)
				limit_time = kwargs.pop('limit_time', 300)
			result = False
			check_set_size(redis, limit, key)
			if redis and limit > 0:
				subkey = '{0}.{1}'.format(int(time.time()*1000000), str(os.getpid()))
				srl = decorators_lua.StoneMRL(redis)
				reason = 0
				t0 = time.time()
				limit_time = limit_time*1000000
				while not reason:
					now = int(time.time()*1000000)
					reason = srl.callRL(key, subkey, limit, limit_time, now)
					time.sleep(0.05)
					# Max wait = limit_time
					if time.time() - t0 > limit_time/1000000:
						break

				if reason:
					try:
						result = func(*args, **kwargs)
					except:
						result = False
				redis.zrem(key, subkey)
			else:
				result = func(*args, **kwargs)
			return result
		return func_wrapper
	return p_decorate
