import codecs
import csv
import urllib
import json
import requests

from flask import Flask, request
from jinja2 import Template, Environment, FileSystemLoader

TEMPLATE_DIR = '/home/soso/prog/coireacht/templates'

app = Flask(__name__)
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


def load_csv(filename):
    titles = None
    data = []
    with codecs.open(filename, 'r', 'iso-8859-1') as f:
        reader = csv.reader(f)
        titles = next(reader)
        for row in reader:
            print('hi')
            data.append(row)
    return (titles, data)

garda_data = load_csv('data/garda_stations.csv')
print(garda_data[1][-1])

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
    d = {
        'eircode': eircode,
        'address': addr_data[0],
        'coord': addr_data[1], 
    }
    print(d)
    return render_template('details.html', d)

@app.route("/test/<eircode>")
def eir_to_cord(eircode):
    url = "https://hackday.autoaddress.ie/2.0/FindAddress?key={}&address={}"
    key = 'GovHackYourWay-AATmpKey-630E84BE0C4B'
    final = url.format(key, eircode.replace(' ', '%20'))
    resp = requests.get(final)
    addr = ' '.join(json.loads(resp.text)['postalAddress'])
    return (addr, str(addr_to_cord(addr)))


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
