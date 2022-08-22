from csv import DictReader
from flask import Flask, send_file, jsonify
import glob

from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)

import io
from base64 import encodebytes
from PIL import Image

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

@app.route("/")
@cross_origin()
def index():
    return send_file('data/config/execution_types.json')


@app.route("/api/old_executions/")
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

@app.route("/api/old_executions/<id>")
@cross_origin()
def old_executions_detail(id):
    return id

@app.route("/api/old_executions/<id>/plots")
@cross_origin()
def old_execution_plots(id):
    plots_path = 'output/executions/'+id+'/simulations/cerebellum_simple/1/plots/'
    result = glob.glob(plots_path+'*.png')
    encoded_imges = []
    for image_path in result:
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'result': encoded_imges})

@app.route("/api/old_executions/<id>/notes")
@cross_origin()
def old_execution_notes(id):
    notes_path = 'output/executions/'+id+'/simulations/cerebellum_simple/1/simulation_notes.txt'
    with open(notes_path, 'r') as f: 
        text = f.read()
    return jsonify({'result': text})


if __name__ == "__main__":
    app.run(debug=True, threaded=False)