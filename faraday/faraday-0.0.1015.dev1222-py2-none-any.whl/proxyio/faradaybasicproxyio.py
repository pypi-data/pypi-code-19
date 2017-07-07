#-------------------------------------------------------------------------------
# Name:        faraday.proxyio.faradaybasicproxyio
# Purpose:     Abstracted interface to Faraday Proxy
#
# Author:      Brent Salmi
#
# Created:     23/08/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import requests
import base64
import time
import logging


class proxyio(object):
    """
    A basic input and output class object to interact with the Faraday proxy server RESTful API

    :param port: (Optional, default = 80) flask port that the proxy to connect to is running on. This allows easy changing of the port if using multiple proxies at one time.

    :Example:

    >>> #A basic proxy IO object running on default proxy port
    >>> faraday_1 = proxyio()
    >>> #A basic proxy IO object running on port 8099 to connect to to proxy
    >>> faraday_1 = proxyio(8099)

    """

    def __init__(self, port=8000, logger=None):
        #Definitions
        self.FLASK_PORT = port  #TCP port
        self.TELEMETRY_PORT = 5  #Faraday Transport "Service Number"
        self.CMD_UART_PORT = 2  #Faraday COMMAND "Service Number"
        self.MAXPOSTPAYLOADLEN = 124  #123

        if logger is not None:
            self._logger = logger
        else:
            self._logger = logging.getLogger("FaradayBasicProxyIO")
            self._logger.setLevel(logging.WARNING)

    #Functions

    def POST(self, local_device_callsign, local_device_id, uart_port, data):
        """
        The POST function is a python function that interacts with the Faraday RESTful API and "POSTS" (puts into) data into the transmit queue. Data provided to this function will be transmitted
        to a local Faraday device over UART (as specified by the arguments) over the intended Faraday transport layer "Service Port."

        The POST function performs all needed BASE64 encoding and JSON dictionary creation as needed by the Faraday proxy API.

        .. note:: Only a single data item is currently accepted.


        :param local_device_callsign: Callsign of the local Faraday device to direct the data to (allows multiple local units)
        :param local_device_id: Callsign ID number of the local Faraday device to direct the data to (allows multiple local units)
        :param uart_port: Intended Faraday transport layer service port to direct the supplied data to
        :param data: Data to be transmitted in string format


        :Return: Python FLASK POST status result

        :Example:

        Usually the data sent over POST will be a generated bytestring that follows the Faraday protocol stack. Below is an example of sending a command to turn ON LED #1 of the KB1LQD-1 device.

        >>> faraday_1 = faradaybasicproxyio.proxyio()
        >>> faraday_cmd = faradaycommands.faraday_commands()
        >>> command = faraday_cmd.CommandLocalGPIOLED1On()
        >>> faraday_1.POST("KB1LQD", 1, faraday_1.CMD_UART_PORT, command)
        <Response [200]>


        """
        #Check if payload too large
        if len(data) > self.MAXPOSTPAYLOADLEN:
            return False  #Too large!
        else:
            #Convert supplied data into BASE64 encoding for safe network transmission
            b64_data = base64.b64encode(data)  #Converts to Base64
            payload = {'data': [b64_data]}

            #POST data to UART service port
            status = requests.post("http://127.0.0.1:" + str(self.FLASK_PORT) + "/?" + "callsign=" + str(local_device_callsign).upper() + '&port=' + str(uart_port) + '&' + 'nodeid=' + str(local_device_id), json=payload)  #Sends Base64 config flash update packet to Faraday

            #Return
            return status

    def GET(self, local_device_callsign, local_device_id, uart_service_number, limit=None):
        """
        This function returns a dictionary of all data packets waiting a Flask API interface queue as specified by the supplied
        UART Port (Service Number).

        :param local_device_callsign: Callsign of the local Faraday device to direct the data to (allows multiple local units)
        :param local_device_id: Callsign ID number of the local Faraday device to direct the data to (allows multiple local units)
        :param uart_service_number: Intended Faraday transport layer service port to direct the supplied data to
        :param limit: (optional) Number of data packets to pop off and return in dictionary from proxy


        :Return: A JSON dictionary of all data packets waiting for the specified UART port. False if no data waiting.

        .. Note:: All data returned will remain in BASE64 encoding from the proxy. Use the JSON decoding tool for further decoding.

        :Example:

        The example below retrieves two data packets waiting from the "Telemetry" UART port (Port 5 in this example).

        >>> faraday_1 = faradaybasicproxyio.proxyio()
        >>> faraday_1.GET("KB1LQD", 1, FARADAY_TELEMETRY_UART_PORT)
        [{u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQwME4GBzkpFhIACeAHMzM1Mi40MjAxTjExODIyLjYwNDhXMzQuNjIwMDBNMC4yNzAyMC45MgAXYAjdCKoICQe8B/sIFgAAAB4K/gAAHCAAAAAARgYHS0IxTFFEAAAABgcTKRYSABZf',
          u'port': 5},
         {u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQFewMGBxIqFhIACeAHMzM1Mi40MjAzTjExODIyLjYwNDdXMzQuNTIwMDBNMC4yNzAyMC45MAAXYAjeCKoICQe5B/oIGAAAAB4LAwAAHCAAAAAAAABGBgdLQjFMUUQAAAAGBxMpFhT/',
          u'port': 5}]
        """
        url = 'http://127.0.0.1:' + str(self.FLASK_PORT) + "/" + "?port=" + str(uart_service_number) + "&callsign=" + str(local_device_callsign) + "&nodeid=" + str(local_device_id)

        # If limit is provided, check that it's positive and add to url
        if limit is not None:
            if int(limit) >= 0:
                url = url + "&limit=" + str(limit)

        try:
            response = requests.get(url)  #calling IP address directly is much faster than localhost lookup
            if response.status_code == 204:
                # No data received
                return None
            else:
                # Data received, return JSON
                return response.json()

        except StandardError as e:
            self._logger.error("StandardError: " + str(e))
        except ValueError as e:
            self._logger.error("ValueError: " + str(e))
        except IndexError as e:
            self._logger.error("IndexError: " + str(e))
        except KeyError as e:
            self._logger.error("KeyError: " + str(e))

    def GETWait(self, local_device_callsign, local_device_id, uart_service_number, sec_timeout=1, debug=False, limit=None):
        """
        This is an abstraction of the *GET* function that implements a timing functionality to wait until a packet has been received (if none in queue) and returns the first received packet(s) or if it times out it will return False.

        :param local_device_callsign: Callsign of the local Faraday device to direct the data to (allows multiple local units)
        :param local_device_id: Callsign ID number of the local Faraday device to direct the data to (allows multiple local units)
        :param uart_service_number: Intended Faraday transport layer service port to direct the supplied data to
        :param sec_timeout: Timeout is in seconds and is a float (can be smaller than 1 seconds)
        :param debug: Default=False, True = prints rolling time in wait until data received
        :param limit: (optional) Number of data packets to pop off and return in dictionary from proxy
        :Return: A JSON dictionary of all data packets waiting for the specified UART port. False if no data waiting.

        :Example: This example will get all data from FARADAY_TELEMETRY_UART_PORT (port 5) and if none



            >>> faraday_1 = faradaybasicproxyio.proxyio()
            >>> faraday_1.GETWait("KB1LQD", 1, FARADAY_TELEMETRY_UART_PORT, 1, False)
            [{u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQ3M04GBwA5FhIACeAHMzM1Mi40MjEzTjExODIyLjYwMTBXMzEuMTIwMDBNMC4yNzAyMC44OAAXYAjcCKwIGAeFB20H0wAAACALCQAAHCAAAAAA2AYHS0IxTFFE/wAABgciOBYSABb5',
              u'port': 5},
             {u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQFewMGBxU5FhIACeAHMzM1Mi40MjIzTjExODIyLjYwNDFXMzIuMjIwMDBNMC4yNzAyMC44OAAXYAjdCKoIGAeGB2wH1wAAAB4LBQAAHCAAAAAAAADYBgdLQjFMUUT/AAAGByI4FhbL',
              u'port': 5}]

        """
        #Start timer "Start Time" and configure function variables to initial state
        starttime = time.time()
        timedelta = 0
        rx_data = None

        while rx_data is None and timedelta < sec_timeout:
            #Update new timedelta
            timedelta = time.time() - starttime
            time.sleep(0.01)  #Need to add sleep to allow threading to go and GET a new packet if it arrives. Why 10ms?

            #Attempt to get data
            rx_data = self.GET(local_device_callsign, local_device_id, uart_service_number, limit=limit)
        #Determine if timeout or got data
        if rx_data:
            if(debug):
                print "Got Data!", "Time In-waiting:", timedelta, "Seconds"
            else:
                pass
            return rx_data
        else:
            if(debug):
                print "Failed to get data!", "Timeout =", sec_timeout
            return False

    def FlushRxPort(self, local_device_callsign, local_device_id, uart_service_number):
        """
        This is a dummy retrieval of data from a port with NO return of the data to mimic a "flushing" of a port of old data.

        :param local_device_callsign: Callsign of the local Faraday device to direct the data to (allows multiple local units)
        :param local_device_id: Callsign ID number of the local Faraday device to direct the data to (allows multiple local units)
        :param uart_service_number: Intended Faraday transport layer service port to direct the supplied data to

        :Return: True if successful and False if error.

        :Example:

            This example will flush all received packets currently waiting in UART port 5.

            >>> faraday_1 = faradaybasicproxyio.proxyio()
            >>> faraday_1.FlushRxPort("KB1LQD", 1, 5)
            True
        """
        data = True
        while data:
            try:
                self.GET(local_device_callsign, local_device_id, uart_service_number)
                return True
            except:
                return False

    def DecodeRawPacket(self, jsonitem):
        """
        This function decodes (BASE64) data from a supplied encoded data packet as received from the GET functions (in JSON format). This function handle 1 packet at a time and returns only the resulting decoded data

        :param jsonitem: BASE64 encoded data packet as expected from the Faraday Proxy GET() functions.

        :Return: the supplied data packet decoded.

        :Example: This example decode a single telemetry packet from BASE64 encoding as received into it's original bytestring format.

            >>> faraday_1 = faradaybasicproxyio.proxyio()
            >>> data = faraday_1.GET(local_device_callsign, local_device_node_id, FARADAY_TELEMETRY_UART_PORT)
            >>> data
            [{u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQwNE4GBwYVBhMBCeAHMzM1Mi40MTk3TjExODIyLjYwMzRXMzIuMjAwMDBNMC40NjAyMC45MgAHYAeNBhwFeQVFBSQFAQAAABsK/gAAHCAAAAAARgYHS0IxTFFEAAAABgcoFAYTARQR',
              u'port': 5}]
            >>> decoded_data = faraday_1.DecodeJsonItemRaw(data[0]['data'])
        """
        data_packet = jsonitem
        decoded_data_packet = base64.b64decode(data_packet)
        return decoded_data_packet
