import requests
import json

class ApiClient:

    def __init__(self, api_key):
        self.base_url = 'https://developer.cumtd.com/api/v2.2/json/'
        self.api_key = api_key
        self.api_key_url = '?key=' + self.api_key

    def get_calendar_dates_by_date(self, date):

        data = requests.get(self.base_url+'getcalendardatesbydate'+self.api_key_url+'&date='+date)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_calendar_dates_by_service(self, service_id):

        data = requests.get(self.base_url+'getcalendardatesbyservice'+self.api_key_url+"&service_id="+service_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_departures_by_stop(self, stop_id):

        data = requests.get(self.base_url+'getdeparturesbystop'+self.api_key_url+'&stop_id='+stop_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_reroutes(self):

        data = requests.get(self.base_url+'getreroutes'+self.api_key_url)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_reroutes_by_route(self, route_id):

        data = requests.get(self.base_url+'getreroutesbyroute'+self.api_key_url+'&route_id='+route_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_route(self, route_id):

        data = requests.get(self.base_url+'getroute'+self.api_key_url+'&route_id='+route_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_routes(self):

        data = requests.get(self.base_url+'getroutes'+self.api_key_url)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_routes_by_stop(self, stop_id):

        data = requests.get(self.base_url+'getroutesbystop'+self.api_key_url+'&stop_id='+stop_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_shape(self, shape_id):

        data = requests.get(self.base_url+'getshape'+self.api_key_url+'&shape_id='+shape_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_shape_between_stops(self, begin_stop_id, end_stop_id, shape_id):

        data = requests.get(self.base_url+'getshapebetweenstops'+self.api_key_url+'&begin_stop_id='+begin_stop_id+'&end_stop_id='+end_stop_id+'&shape_id='+shape_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_stop(self, stop_id):

        data = requests.get(self.base_url+'getstop'+self.api_key_url+'&stop_id='+stop_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_stops(self):

        data = requests.get(self.base_url+'getstops'+self.api_key_url)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_stops_by_lat_lon(self, lat, lon, count):

        data = requests.get(self.base_url+'getstopsbylatlon'+self.api_key_url+'&lat='+lat+'&lon='+lon+'&count='+count)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_stops_by_search(self, query):

        data = requests.get(self.base_url+'getstopsbysearch'+self.api_key_url+'&query='+query)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_stop_times_by_trip(self, trip_id):

        data = requests.get(self.base_url+'getstoptimesbytrip'+self.api_key_url+'&trip_id='+trip_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_stop_times_by_stop(self, stop_id):

        data = requests.get(self.base_url+'getstoptimesbystop'+self.api_key_url+'&stop_id='+stop_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_planned_trips_by_lat_lon(self, origin_lat, origin_lon, destination_lat, destination_lon):

        data = requests.get(self.base_url+'getplannedtripsbylatlon'+self.api_key_url+'&origin_lat='+origin_lat+'&origin_lon='+origin_lon+'&destination_lat='+destination_lat+"&destination_lon="+destination_lon)
        if(data.ok):
            jsonData = json.loads(data.content)
            print(jsonData)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_planned_trips_by_stops(self, origin_stop_id, destination_stop_id):

        data = requests.get(self.base_url+'getplannedtripsbystops'+self.api_key_url+'&origin_stop_id='+origin_stop_id+'&destination_stop_id='+destination_stop_id)
        if(data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_trip(self, trip_id):

        data = requests.get(self.base_url+'gettrip'+self.api_key_url+'&trip_id='+trip_id)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_trips_by_block(self, block_id):

        data = requests.get(self.base_url+'gettripsbyblock'+self.api_key_url+'&block_id='+block_id)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_trips_by_route(self, route_id):

        data = requests.get(self.base_url+'gettripsbyroute'+self.api_key_url+'&route_id='+route_id)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_vehicle(self, vehicle_id):

        data = requests.get(self.base_url+'getvehicle'+self.api_key_url+'&vehicle_id='+vehicle_id)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_vehicles(self):

        data = requests.get(self.base_url+'getvehicles'+self.api_key_url)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_vehicles_by_route(self, route_id):

        data = requests.get(self.base_url+'getvehiclesbyroute'+self.api_key_url+'&route_id='+route_id)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_news(self):

        data = requests.get(self.base_url+'getnews'+self.api_key_url)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

    def get_api_usage(self):

        data = requests.get(self.base_url + 'getapiusage' + self.api_key_url)
        if (data.ok):
            jsonData = json.loads(data.content)
            return jsonData
        else:
            print("Unsuccesful: " + str(data.status_code))
            return None

