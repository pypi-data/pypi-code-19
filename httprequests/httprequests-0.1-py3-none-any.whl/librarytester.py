import philipsHue

ip = "http://192.168.1.137/api/QSL3tIiR9BLIm03BdGNWLY5Fs09SVlEtjfjdx6EU/lights/1/state"

philipsHue.changeHue(ip, True, 254, 0, 254)