from flask import Flask, send_file, jsonify, request, make_response
from csv import DictReader
import nest

import string
import random
import glob
import json
from pathlib import Path

import io
from base64 import encodebytes
from PIL import Image

from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

# from flaskext.mysql import MySQL
# from pymysql.cursors import DictCursor
# from src.connection.mysql.select import select_rows
# from src.connection.mysql.insert import insert_row

from main_api import run as run_execution

# api = Flask(__name__)
# cors = CORS(api, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

# api.config['MYSQL_DATABASE_HOST'] = 'localhost'
# api.config['MYSQL_DATABASE_USER'] = 'root'
# api.config['MYSQL_DATABASE_PASSWORD'] = 'CerebSens01!'
# api.config['MYSQL_DATABASE_DB'] = 'sensorycerebellum'
# api.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'

# conn = connect(host='localhost', user='root', password='CerebSens01!', db='sensorycerebellum', charset='utf8mb4', cursorclass=cursors.DictCursor)
# mysql = MySQL(cursorclass=DictCursor)
# mysql.init_app(api)

api = Flask(__name__)
api.config['DEBUG'] = True
api.config['FLASK_ENV'] = 'development'

cors = CORS(api, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
db = SQLAlchemy(api)

nest.Install("cerebmodule")

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@api.route("/")
@cross_origin()
def home():
    return "MuSiN api homepage"

@api.route("/api/")
@cross_origin()
def api_home():
    return "APIs are up and running correctly"

@api.route("/api/existing_networks", methods=["GET"])
@cross_origin()
def existing_networks():

    networks = []

    if request.method == 'GET':
        conn = mysql.get_db()
        query = "SELECT `code`, `name`, `default_parameters` FROM `networks`"
        networks = select_rows(conn, query)
        if networks:
            for net in networks:
                query = "SELECT `name`, `raster`, `voltage`, `train`, `test`, `split`, `population_name` FROM `plots` WHERE network = %s"
                net['plots'] = select_rows(conn, query, (net['name']))

    return jsonify({'result': networks})

@api.route("/api/existing_types", methods=["GET"])
@cross_origin()
def existing_types():
    result = []

    if request.method == 'GET':
        conn = mysql.get_db()
        query = "SELECT `code`, `name`, `parameters_id` FROM `input_types`"
        types = select_rows(conn, query)
        if types:
            for type in types:
                query = "SELECT `rate_start`,`rate_end`,`rate_step`,`first_spike_latency_start`,`first_spike_latency_end`,`first_spike_latency_step`,`number_of_neurons_start`,`number_of_neurons_end`,`number_of_neurons_step`,`trial_duration_start`,`trial_duration_end`,`trial_duration_step` FROM `input_parameters` WHERE id = %s"
                r = {
                    'code': type['code'],
                    'name': type['name'],
                    'parameters': select_rows(conn, query, (type['parameters_id']))
                }
                result.append(r)

        print('existing_types: ', result)
        
    return jsonify({'result': result})


@api.route("/api/previous_executions/", methods=["GET"])
@cross_origin()
def previous_executions():
    executions = {
        "list": []
    }
    with open('output/executions/executions.csv', 'r') as csvfile:
        csv_dict_reader = DictReader(csvfile)
        for row in csv_dict_reader:
            executions['list'].append(row)
    return executions

@api.route("/api/previous_executions/<id>", methods=["GET"])
@cross_origin()
def previous_executions_detail(id):
    return id

@api.route("/api/previous_executions/<id>/plots", methods=["GET"])
@cross_origin()
def previous_execution_plots(id):
    plots_path = 'output/executions/'+id+'/simulations/cerebellum_simple/1/plots/'
    result = glob.glob(plots_path+'*.png')
    encoded_imges = []
    for image_path in result:
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'result': encoded_imges})

@api.route("/api/previous_executions/<_id>/notes", methods=["GET"])
@cross_origin()
def previous_execution_notes(_id):
    notes_path = 'output/executions/'+_id+'/simulations/cerebellum_simple/1/simulation_notes.txt'
    with open(notes_path, 'r') as f: 
        text = f.read()
    return jsonify({'result': text})

@api.route("/api/new_execution/", methods=["POST"])
@cross_origin()
def new_execution():
    
    params = json.loads(request.data)
    run_execution(params)
    
    return jsonify({'result': 'success'})

@api.route("/api/existing_type/<_code>", methods=["GET"])
@cross_origin()
def existing_type(_name):
    with open('api_data/config/execution_types.json', 'r') as f:
        file = json.load(f)

    if _name in file.keys():
        return jsonify(file[_name])
    else:
        return jsonify({'result': 'error'})

@api.route("/api/new_input_type/", methods=["POST"])
@cross_origin()
def new_input_type():
    params = json.loads(request.data)
    name = params['name']
    spikes = params['spikes']
    placeholders = ', '.join(['%s'] * len(spikes))
    columns = ', '.join(spikes.keys())
    if request.method == 'POST':
        conn = mysql.get_db()
        query = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('spikes', columns, placeholders)
        spikes_id = insert_row(conn, query, list(spikes.values()))

        new_code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
        query = "INSERT INTO input_types VALUES (NULL, %s, %s, %s)";
        result = insert_row(conn, query, (new_code, name, spikes_id))
        print('new_input_type', result)
        
    return jsonify({'result': 'aaa'})

@api.route("/api/existing_network/<_type>/<_name>", methods=["GET"])
@cross_origin()
def existing_network(_type, _name):
    filename = Path('api_data/config/networks/'+_type+'/'+_name+'.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})

#TODO! da aggiungere gestione plots
@api.route("/api/plots_config/<_name>", methods=["GET"])
@cross_origin()
def plots_config(_type, _name):
    filename = Path('api_data/config/plots_config.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})

if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)