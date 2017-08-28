import requests

def get_temp():
    r = requests.get("http://api.openweathermap.org/data/2.5/weather?lat=40.2212&lon=23.6666&APPID=73f3a8c7b0681b685f4195065c6719e7")
    data = r.json()
    temp_K = data['main']['temp']
    temp_C = convert_K_to_C(temp_K)
    return temp_C

def convert_K_to_C(k):
    return k - 273.15

def print_temp():
    temp = get_temp()
    print(temp)

def activities():
    temp = get_temp()
    if temp <= 15:
        act = 'Go hiking in the gorgeous mountains!'
    elif temp > 15 and temp <=25 :
        act = 'Spend a beautiful day at the beach!'
    else :
        act = 'Stay inside and don\'t die'
    print(act)
