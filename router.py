# encoding: utf-8

"""
127.0.0.1:5000/?start=Казань ул. Баумана, 70&finish=Казань, ул Кремлевская, 5
"""


import requests

from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)


class AddressNotFoundError(Exception):
    pass


class Cache:
    def __init__(self):
        self.cache = {}

    def set_value(self, addr, value):
        self.cache[addr] = value

    def in_cache(self, addr):
        return addr in self.cache.keys()

    def get_value(self, addr):
        return self.cache[addr]


_ADDRESS_COORD_CACHE = Cache()


def geocode(address):
    """Геокодирование адреса на API Яндекса
    """
    # https://geocode-maps.yandex.ru/1.x/?format=json&apikey=10edb3e5-200b-4eea-a6a8-0d052347c20b&geocode=

    BASE_URL = "https://geocode-maps.yandex.ru/1.x/?format=json"
    API_KEY = "10edb3e5-200b-4eea-a6a8-0d052347c20b"

    url = "%s&apikey=%s&geocode=%s" % (BASE_URL, API_KEY, address)

    r = requests.get(url)
    answ = r.json()

    app.logger.debug("YANDEX: %s %r", r, answ)

    response = answ["response"]
    collection = response["GeoObjectCollection"]
    members = collection["featureMember"]

    if len(members) == 0:
        raise AddressNotFoundError('Искомый адрес "%s" не найден' % address)

    feature0 = members[0]
    point = feature0["GeoObject"]["Point"]
    point = point["pos"]

    x, y = [float(t) for t in point.split()]

    return x, y


def ask_for_route(x1, y1, x2, y2):
    URL = (
        "https://gooddeed.me/noname4/wheel/route/v1/foot/%s,%s;%s,%s?steps=true&geometries=geojson"
        % (x1, y1, x2, y2)
    )
    osrm_response = requests.get(URL)

    data = osrm_response.json()

    app.logger.debug("OSRM: %s %r", osrm_response, data)

    route = data["routes"][0]

    return route


def nmeter(m):
    m = int(m)
    if m >= 10 and m < 21:
        return '%d метров' % m
    if m % 10 == 1:
        return '%d метр' % m
    if m % 10 != 0 and m % 10 < 5:
        return '%d метра' % m
    return '%d метров' % m


def ru_plural_formatter(single, couple, many):
    def formatter(m):
        m = int(m)
        if m >= 10 and m < 21:
            return '%d %s' % (m, many)
        if m % 10 == 1:
            return '%d %s' % (m, single)
        if m % 10 != 0 and m % 10 < 5:
            return '%d %s' % (m, couple)
        return '%d %s' % (m, many)
    return formatter


n_meter = ru_plural_formatter('метр', 'метра', 'метров')
n_km = ru_plural_formatter('километр', 'километра', 'километров')


def humanize_distance(m):
    if m < 3:
        return 'пару метров'
    for a, b in [
            (25, 2.5),
            (100, 5),
            (500, 25),
            (2500, 50),
    ]:
        if m < a:
            m += b  # for proper rounding
            return n_meter(m - m % (b * 2))
    km = m // 1000
    if km < 10:
        ret = n_km(km)
        m = m - km * 1000
        m += 50
        m -= m % 100
        if m:
            ret += ' ' + n_meter(m - m % 100)
        return ret
    return n_km(km)


def describe_route(route):
    """Описание маршрута в виде "маневров": точка и действие в точке
    """
    leg = route["legs"][0]
    steps = leg["steps"]

    distances = [humanize_distance(s["distance"]) for s in steps]
    maneuvers = [s["maneuver"] for s in steps]

    # From https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md
    # --------------------------------------------------
    # | modifier     | Description                     |
    # --------------------------------------------------
    # | uturn        | indicates reversal of direction |
    # | sharp right  | a sharp right turn              |
    # | right        | a normal turn to the right      |
    # | slight right | a slight turn to the right      |
    # | straight     | no relevant change in direction |
    # | slight left  | a slight turn to the left       |
    # | left         | a normal turn to the left       |
    # | sharp left   | a sharp turn to the left        |
    # --------------------------------------------------
    moves = {
        "uturn": "развернитесь",
        "sharp right": "резко поверните направо",
        "right": "поверните направо",
        "slight right": "незначительно поверните направо",
        "straight": "продолжайте движение прямо",
        "slight left": "незначительно поверните налево",
        "left": "поверните налево",
        "sharp left": "резко поверните налево",
    }

    maneuvers = [
        (moves[m["modifier"]] + " и ") if "modifier" in m else "" for m in maneuvers
    ]

    texts = []
    for i in range(len(distances)):
        t = "%sпройдите %s" % (maneuvers[i], distances[i])
        texts.append(t)

    return texts


def _get_xy(address):
    if not _ADDRESS_COORD_CACHE.in_cache(address):
        x, y = geocode(address)
        _ADDRESS_COORD_CACHE.set_value(address, (x, y))

    return _ADDRESS_COORD_CACHE.get_value(address)


@app.route("/geo")
def hello():
    start = request.args.get("start")
    finish = request.args.get("finish")

    x1, y1 = _get_xy(start)
    x2, y2 = _get_xy(finish)

    route = ask_for_route(x1, y1, x2, y2)
    description = describe_route(route)

    result = {"geo": route, "text": description}

    return jsonify(result)


def main():
    # x1, y1 = geocode('Казань, ул. Баумана, дом 70')
    # x2, y2 = geocode('Казань, ул. Кремлевская, дом 7')
    x1, y1 = (49.117355, 55.789082)
    x2, y2 = (49.110411, 55.796268)

    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(
        """Координаты прописаны руками -- раскомментируй геокодирование.
          (сделано из экономии количества вызовов API)"""
    )
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    r = ask_for_route(x1, y1, x2, y2)
    man = describe_route(r)
    for t in man:
        print(t)


if __name__ == "__main__":
    app.run()
