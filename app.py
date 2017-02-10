from flask import Flask, request
from jinja2 import Template, Environment, FileSystemLoader

TEMPLATE_DIR = '/home/soso/prog/coireacht/templates'

app = Flask(__name__)
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

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
    return render_template('details.html', {})

if __name__ == "__main__":
    app.run(host="localhost", port=4321)
