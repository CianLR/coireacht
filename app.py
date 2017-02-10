import codecs
import csv
import urllib
import json
import requests

from flask import Flask, request
from jinja2 import Template, Environment, FileSystemLoader

from garda_stations import Station

TEMPLATE_DIR = '/home/waterloo/prog/coireacht/templates'

app = Flask(__name__)
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def load_garda_loc(filename):
    locs = {}
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            name, lat, lng = row
            locs[name] = float(lat), float(lng)
    return locs

def load_csv(filename, locs):
    titles = None
    stations = []
    with codecs.open(filename, 'r', 'iso-8859-1') as f:
        reader = csv.reader(f)
        titles = next(reader)
        for row in reader:
            if row[1] not in locs:
                continue
            stations.append(Station(row, locs[row[1]][0], locs[row[1]][1]))
    return (titles, stations)

loc_data = load_garda_loc('data/fixed_garda_locations.csv')
garda_data = load_csv('data/garda_stations.csv', loc_data)

def find_nearest_station(lat, lng):
    return min(garda_data[1], key=lambda s: s.dist_from_coord(lat, lng))

def render_template(name, d):
    # d should be a dict of key:values to populate the template
    template = env.get_template(name)
    return template.render(d)

@app.route("/")
def index():
    return render_template('index.html', {})

@app.route("/details")
def details():
    eircode = request.args.get('eircode')
    addr_data = eir_to_cord(eircode)
    coords = addr_data[1]
    #coords = addr_data[1].strip('()').split(',') # is a string, not a tuple
    d = {
        'eircode': eircode,
        'address': addr_data[0],
        'coord_x': coords[0], 
        'coord_y': coords[1],
    }
    print(d)
    return render_template('details.html', d)

def eir_to_cord(eircode):
    url = "https://hackday.autoaddress.ie/2.0/FindAddress?key={}&address={}"
    key = 'GovHackYourWay-AATmpKey-630E84BE0C4B'
    final = url.format(key, eircode.replace(' ', '%20'))
    resp = requests.get(final)
    addr = ' '.join(json.loads(resp.text)['postalAddress'])
    return (addr, addr_to_cord(addr))


def get_garda_station_dists(x,y):
    return [0 for i in garda_data[1]]


def addr_to_cord(addr):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': addr}
    r = requests.get(url, params=params)
    results = r.json()['results']
    location = results[0]['geometry']['location']
    return location['lat'], location['lng']


if __name__ == "__main__":
    app.run(host="localhost", port=4321)
