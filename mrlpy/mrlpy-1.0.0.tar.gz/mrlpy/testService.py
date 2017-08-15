from mservice import MService

class TestService(MService):
	def __init__(self, name):
		super(TestService, self).__init__(name)
	
	def test(self):
		print "TEST SUCCESSFUL"

if __name__ == "__main__":
	t = TestService("t")
