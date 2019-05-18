# encoding: utf-8
# Get coordinates using Yandex Geocoder

import requests

from cost import GRASS

# https://geocode-maps.yandex.ru/1.x/?format=json&apikey=10edb3e5-200b-4eea-a6a8-0d052347c20b&geocode=

class AddressNotFoundError(Exception):
    pass


def geocode(address):
    """Геокодирование адреса на API Яндекса
    """
    BASE_URL = "https://geocode-maps.yandex.ru/1.x/?format=json"
    API_KEY = "10edb3e5-200b-4eea-a6a8-0d052347c20b"

    url = "%s&apikey=%s&geocode=%s" % (BASE_URL, API_KEY, address)

    r = requests.get(url)
    answ = r.json()

    response = answ["response"]
    collection = response["GeoObjectCollection"]
    members = collection["featureMember"]

    if len(members) == 0:
        raise AddressNotFoundError('Address "%s" not found' % address)

    feature0 = members[0]
    point = feature0["GeoObject"]["Point"]
    point = point['pos']

    x, y = [float(t) for t in point.split()]

    return x, y


def ask_for_route(x1, y1, x2, y2):
    URL = "https://gooddeed.me/noname4/wheel/route/v1/foot/%s,%s;%s,%s?steps=true&geometries=geojson" % (x1, y1, x2, y2)
    r = requests.get(URL)
    
    r = r.json()
    route  = r['routes'][0]

    return route


def describe_route(route):
    """Описание маршрута в виде "маневров": точка и действие в точке
    """
    leg = route['legs'][0]
    steps = leg['steps']
    
    distances = [s['distance'] for s in steps]
    maneuvers = [s['maneuver'] for s in steps]
    
    """https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md :
    
        modifier 	Description
    uturn 	indicates reversal of direction
    sharp right 	a sharp right turn
    right 	a normal turn to the right
    slight right 	a slight turn to the right
    straight 	no relevant change in direction
    slight left 	a slight turn to the left
    left 	a normal turn to the left
    sharp left 	a sharp turn to the left
    """
    moves = {
        'uturn': 'развернитесь',
        'sharp right': "резко поверните направо",
        'right': "поверните на право",
        'slight right': "незначительно поверните направо",
        'straight': "продолжайте движение прямо",
        'slight left': "незначительно поверните налево",
        'left': "поверните налево",
        'sharp left': "резко поверните налево"
    }

    maneuvers = [moves[m['modifier']] for m in maneuvers]
    
    texts = []
    for i in range(len(distances)):
        t = 'Пройдите %s метров и %s' % (distances[i], maneuvers[i])
        texts.append(t)

    return texts

    

if __name__ == "__main__":

    # x1, y1 = geocode('Казань, ул. Баумана, дом 70')
    # x2, y2 = geocode('Казань, ул. Кремлевская, дом 7')
    x1, y1 = (49.117355, 55.789082)
    x2, y2 = (49.110411, 55.796268)

    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print("""Координаты прописаны руками -- раскомментируй геокодирование.
          (сделано из экономии количества вызовов API)""")
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


    r = ask_for_route(x1, y1, x2, y2)
    man = describe_route(r)
    for t in man:
        print (t)
    
