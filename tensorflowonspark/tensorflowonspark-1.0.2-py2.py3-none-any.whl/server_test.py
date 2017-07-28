from reservation import MessageServer, MessageClient

def test_client_send(addr):
  c = MessageClient(addr)
  c.send("hello")
  c.close()

def test_client_send_recv(addr):
  c = MessageClient(addr)
  c.send("hi")
  msg = c.receive()
  c.close()

s = MessageServer()
addr = s.start()

test_client_send(addr)
test_client_send_recv(addr)

s.stop()
