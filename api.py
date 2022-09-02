from csv import DictReader
from flask import Flask, send_file, jsonify, request, make_response
import glob
import json
from pathlib import Path

import io
from base64 import encodebytes
from PIL import Image

from flask_cors import CORS, cross_origin

from main_api import run as run_execution

app = Flask(__name__)
cors = CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@app.route("/", methods=["GET"])
@cross_origin()
def index():
    return send_file('api_data/config/execution_types.json')


@app.route("/api/old_executions/", methods=["GET"])
@cross_origin()
def old_executions():
    executions = {
        "list": []
    }
    with open('output/executions/executions.csv', 'r') as csvfile:
        csv_dict_reader = DictReader(csvfile)
        for row in csv_dict_reader:
            executions['list'].append(row)
    return executions

@app.route("/api/old_executions/<id>", methods=["GET"])
@cross_origin()
def old_executions_detail(id):
    return id

@app.route("/api/old_executions/<id>/plots", methods=["GET"])
@cross_origin()
def old_execution_plots(id):
    plots_path = 'output/executions/'+id+'/simulations/cerebellum_simple/1/plots/'
    result = glob.glob(plots_path+'*.png')
    encoded_imges = []
    for image_path in result:
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'result': encoded_imges})

@app.route("/api/old_executions/<_id>/notes", methods=["GET"])
@cross_origin()
def old_execution_notes(_id):
    notes_path = 'output/executions/'+_id+'/simulations/cerebellum_simple/1/simulation_notes.txt'
    with open(notes_path, 'r') as f: 
        text = f.read()
    return jsonify({'result': text})

@app.route("/api/new_execution/", methods=["POST"])
@cross_origin()
def new_execution():
    
    params = json.loads(request.data)
    run_execution(params)
    
    return jsonify({'result': 'success'})

@app.route("/api/existing_types", methods=["GET"])
@cross_origin()
def existing_types():
    with open('api_data/config/execution_types.json', 'r') as f:
        file = json.load(f)

    return jsonify({'types': list(file.keys())})

@app.route("/api/existing_type/<_name>", methods=["GET"])
@cross_origin()
def existing_type(_name):
    with open('api_data/config/execution_types.json', 'r') as f:
        file = json.load(f)

    if _name in file.keys():
        return jsonify(file[_name])
    else:
        return jsonify({'result': 'error'})

@app.route("/api/existing_networks", methods=["GET"])
@cross_origin()
def existing_networks():
    return send_file('api_data/config/networks/existing_networks.json')

@app.route("/api/existing_network/<_type>/<_name>", methods=["GET"])
@cross_origin()
def existing_network(_type, _name):
    filename = Path('api_data/config/networks/'+_type+'/'+_name+'.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})

#TODO! da aggiungere gestione plots
@app.route("/api/plots_config/<_name>", methods=["GET"])
@cross_origin()
def plots_config(_type, _name):
    filename = Path('api_data/config/plots_config.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})

if __name__ == "__main__":
    app.run(debug=True, threaded=False)