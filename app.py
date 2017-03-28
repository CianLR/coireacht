import codecs
import csv
import urllib
import json
import requests
import os

from heapq import nsmallest
from flask import Flask, request
from jinja2 import Template, Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

from garda_stations import Station

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
app = Flask(__name__)
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

template_langs = {
    'en': 'en',
    'ga': 'ga'
}

def get_template_path(template, language):
    return os.path.join(template_langs[language], template)


def render_template(name, d):
    # d should be a dict of key:values to populate the template
    template = env.get_template(name)
    return template.render(d)


def get_and_render_template(template, language, d=None):
    print ('Getting template', template, 'in language', language)
    if language not in template_langs:
        language = 'en'
    template_path = get_template_path(template, language)
    if d is None:
        d = {}
    if 'lang' not in d:
        d['lang'] = language
    try:
        return render_template(template_path, d)
    except TemplateNotFound:
        return render_template(get_template_path(template, 'en'), d)


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
stations_by_division = {}
for st in garda_data[1]:
    if st.division in stations_by_division:
        stations_by_division[st.division].append(st)
    else:
        stations_by_division[st.division] = [st]
for div in stations_by_division:
    stations_by_division[div] = sorted(
        stations_by_division[div],
        key=lambda s: s.get_score(),
        reverse=True)


def find_nearest_n_stations(n, lat, lng):
    return nsmallest(
        n=n,
        iterable=garda_data[1],
        key=lambda s: s.dist_from_coord(lat, lng))


@app.route("/")
def index():
    lang = request.args.get('lang', default='en')
    return get_and_render_template('index.html', lang)


@app.route("/details")
def details():
    lang = request.args.get('lang', default='en')
    input_address = request.args.get('input')
    try:
        addr, coords = eir_to_cord(input_address)
        crime_score = score_for_coords(coords)
        uni_dists = time_to_unis(addr)
        #coords = addr_data[1].strip('()').split(',') # is a string, not a tuple
        d = {
            'input': input_address,
            'address': addr,
            'dists_to_unis': uni_dists,
            'coord_x': coords[0],
            'coord_y': coords[1],
            'true_score': crime_score,
            'rounded_score': round(crime_score),
            'lang': lang
        }
        print(d)
        return get_and_render_template('details.html', lang, d)
    except Exception as e:
        print(e)
        return get_and_render_template('error.html',
                                       lang,
                                       {'input': input_address})

@app.route("/about")
def about():
    lang = request.args.get('lang', default='en')
    return get_and_render_template('about.html', lang)


def eir_to_cord(eircode):
    u = 'https://maps.googleapis.com/maps/api/geocode/json?address={},IRELAND'
    resp = json.loads(requests.get(u.format(eircode)).text)
    if resp['status'] != 'OK':
        print("Address for location {} not found. Status '{}'".format(
            eircode, resp['status']))
        raise Exception("Eircode not found")

    addr = resp['results'][0]['formatted_address']
    lat = float(resp['results'][0]['geometry']['location']['lat'])
    lng = float(resp['results'][0]['geometry']['location']['lng'])
    return addr, (lat, lng)

@app.route('/nearest_stations_stats/<input_address>')
def ns_stats(input_address):
    addr, coords = eir_to_cord(input_address)
    score = score_for_coords(coords)
    return "Name {}, Score {}".format(addr, score)

def get_cross_division_ranking(divisions):
    # Return a list of all stations in the given divisions, sorted worst to
    # best.
    stations = []
    for div in divisions:
        stations.extend(stations_by_division[div])
    return sorted(stations, key=lambda s: s.get_score(), reverse=True)

def score_for_coords(coords):
    NEAREST_STATIONS = 3
    stations = find_nearest_n_stations(NEAREST_STATIONS, *coords)
    rank_list = get_cross_division_ranking(set(s.division for s in stations))
    dists = []
    rankings = []
    for s in stations:
        dists.append(s.dist_from_coord(*coords) + 0.000001)
        rankings.append(rank_list.index(s))
    inverse_sum = sum(1/x for x in dists)
    scale_factor = 1/inverse_sum
    # Get a weight for each station that's inversely proportional to distance
    # The weights all add up to 1
    weightings = [(1/dist) * scale_factor for dist in dists]
    # Get the estimated ranking (or index) for a Garda station on the given
    # co-ordinates
    weighted_index = sum(rank * weight for rank, weight in zip(rankings, weightings))
    # The score is this rank scaled from 1 to 5
    score = 1 + ((weighted_index+1)/len(rank_list))*4
    return score

def time_to_unis(addr, unis=None, mode='walking'):
    """Takes the address of a house and returns a list of its times to
    all the universities, optionally provide a list in the unis parameter to
    only get times to the specified addresses."""
    uni_addrs = {
        'DCU - Dublin City University, Glasnevin, Dublin 9': 'DCU',
        'Trinity College Dublin, College Green, Dublin 2': 'TCD',
        'University College Dublin, Stillorgan Rd, Belfield, Dublin 4': 'UCD',
        'University of Limerick, Sreelane, Castletroy, Co. Limerick': 'UL',
        'National University of Ireland, Galway, University Rd, Galway': 'NUIG',
        'University College Cork, College Rd, University College, Cork': 'UCC',
        'Maynooth University, Newtown Road, Kilcock, Maynooth, Co. Kildare': 'MH'
    }
    unis = unis or list(uni_addrs.keys())
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?mode={}&origins={}&destinations={}'
    filled_url = url.format(mode, addr, '|'.join(unis))
    resp = json.loads(requests.get(filled_url).text)

    times = []
    if resp['status'] != 'OK':
        return times

    for i, elem in enumerate(resp['rows'][0]['elements']):
        if elem['status'] != 'OK':
            continue
        uni_short_name = uni_addrs[unis[i]]
        time = elem['duration']['text']
        dist = elem['distance']['value']
        times.append((dist, uni_short_name, time))

    return [(name, time) for _, name, time in sorted(times)]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4321)
