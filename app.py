import json
import urllib

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/test/<eircode>")
def eir_to_cord(eircode):
    url = "https://hackday.autoaddress.ie/2.0/FindAddress?key={}&address={}"
    key = 'GovHackYourWay-AATmpKey-630E84BE0C4B'
    final = url.format(key, eircode.replace(' ', '%20'))
    print(final)
    resp = urllib.request.urlopen(final)
    return resp#json.load(resp)
        
if __name__ == "__main__":
    app.run()
