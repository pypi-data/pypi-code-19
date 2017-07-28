from reservation import Server, Client

def test_client_register(addr):
  c = Client(addr)
  c.register({'id': 1234, 'host': 'localhost', 'port': 8080})
  c.close()

def test_client_await(addr):
  c = Client(addr)
  c.await_reservations()
  c.close()

s = Server(1)
addr = s.start()

test_client_register(addr)
test_client_await(addr)

s.stop()
