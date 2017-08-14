#MIT License
#
#Copyright (c) 2017 TheChyz
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

def startSC2():
    args = [
          "C:\Users\chyziak\Desktop\my_folder\my_games\sc2\StarCraft II\Versions\Base55958\SC2_x64.exe",
          "-listen", "127.0.0.1",
          "-port", "18612",
          "-dataDir", "C:\Users\chyziak\Desktop\my_folder\my_games\sc2\StarCraft II",
          "-tempDir", "c:\users\chyziak\\appdata\local\\temp\sc-hquxxh",
          "-displayMode", "0",
    ]
    sc2_process = subprocess.Popen(args, cwd="C:\Users\chyziak\Desktop\my_folder\my_games\sc2\StarCraft II\Support64", env=None)
    sc2_socket = connect(proc, 18612)
    return sc2_socket


    sock.send(makeGameRequest().SerializeToString())
    response = sc2api_pb2.Response()
    response_bytes = sock.recv()
    response.ParseFromString(response_bytes)

    sock.send(makeJoinGameRequest().SerializeToString())
    response = sc2api_pb2.Response()
    response_bytes = sock.recv()
    response.ParseFromString(response_bytes)

    still_going = True
    while still_going:
	    sock.send(makeObservationRequest().SerializeToString())

	    response = sc2api_pb2.Response()
	    response_bytes = sock.recv()
	    response.ParseFromString(response_bytes)
	    if len(response.observation.player_result) > 0:
		  still_going = False

	    sock.send(makeStepRequest().SerializeToString())

	    response = sc2api_pb2.Response()
	    response_bytes = sock.recv()
	    response.ParseFromString(response_bytes)

    sock.send(makeLeaveRequest().SerializeToString())

    response = sc2api_pb2.Response()
    response_bytes = sock.recv()
    response.ParseFromString(response_bytes)

def makeGameRequest():
    req = sc2api_pb2.Request()
    req.create_game.battlenet_map_name = "Ohana LE"
    req.create_game.disable_fog = True
    req.create_game.realtime = True
    me = req.create_game.player_setup.add()
    me.type = sc2api_pb2.Participant
    me.race = sc2api_pb2.Protoss
    opponent = req.create_game.player_setup.add()
    opponent.type = sc2api_pb2.Computer
    opponent.race = sc2api_pb2.Terran
    opponent.difficulty = sc2api_pb2.CheatInsane
    return req

def makeJoinGameRequest():
	req = sc2api_pb2.Request()
	req.join_game.race = sc2api_pb2.Protoss
	req.join_game.options.raw = True
	return req


def makeStepRequest():
	req = sc2api_pb2.Request()
	req.step.count = 1
	return req

def makeObservationRequest():
	req = sc2api_pb2.Request()
	req.observation.SetInParent()
	return req

def makeLeaveRequest():
	req = sc2api_pb2.Request()
	req.leave_game.SetInParent()
	return req

def makeDataRequest():
	req = sc2api_pb2.Request()
	req.data.SetInParent()
	return req




def connect(proc, port):
   """Connect to the websocket, retrying as needed. Returns the socket."""
   was_running = False
   for i in range(120):
     is_running = running(proc)
     was_running = was_running or is_running
     if (i >= 30 or was_running) and not is_running:
      print(
           "SC2 isn't running, so bailing early on the websocket connection.")
      break
     print("Connection attempt %s", i)
     time.sleep(1)
     try:
       return websocket.create_connection("ws://127.0.0.1:%s/sc2api" % port,
                                          timeout=2 * 60)  # 2 minutes
     except socket.error:
       pass  # SC2 hasn't started listening yet.
     except websocket.WebSocketException as err:
       if "Handshake Status 404" in str(err):
         pass  # SC2 is listening, but hasn't set up the /sc2api endpoint yet.
       else:
         raise
   sys.exit("Failed to create the socket.")

def running(proc):
  return proc.poll() if proc else False
