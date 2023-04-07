from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from api.api import db

import glob
import json
from csv import DictReader
from api.utils.images import get_response_image

from api.models.executions import Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionInputRelationship, ExecutionNetworkRelationship
from api.models.inputs import Input
from api.models.networks import Network, NetworkParameter

executions = Blueprint('executions', __name__)
@executions.route("/api/executions/types/<_name>/", methods=["GET"])
@cross_origin()
def types_details(_name):
    with open('api_data/config/execution_types.json', 'r') as f:
        file = json.load(f)

    if _name in file.keys():
        return jsonify(file[_name])
    else:
        return jsonify({'result': 'error'})
    
@executions.route("/api/executions/list/", methods=["GET"])
@cross_origin()
def list():
    executions = Execution.get_all()
    for execution in executions:
        executiontypes = ExecutionExecutiontypeRelationship.get_by_execution_code(execution['code'])
        execution['executiontypes'] = [Executiontype.get_name(executiontype['executiontype_code']) for executiontype in executiontypes]
        inputs = ExecutionInputRelationship.get_by_execution_code(execution['code'])
        execution['inputs'] = [Input.get_name(input['input_code']) for input in inputs]
        print(execution)
        networks = ExecutionNetworkRelationship.get_by_execution_code(execution['code'])
        execution['networks'] = [Network.get_name(network['network_code']) for network in networks]
    return jsonify({'result': executions})

@executions.route("/api/executions/<id>/", methods=["GET"])
@cross_origin()
def details(id):
    print(id)
    return id

@executions.route("/api/executions/<id>/plots/", methods=["GET"])
@cross_origin()
def details_plots(id):
    plots_path = 'output/executions/'+id+'/simulations/cerebellum_simple/1/plots/'
    result = glob.glob(plots_path+'*.png')
    encoded_imges = []
    for image_path in result:
        encoded_imges.append(get_response_image(image_path))
    return jsonify({'result': encoded_imges})

@executions.route("/api/executions/<_id>/notes/", methods=["GET"])
@cross_origin()
def details_notes(_id):
    notes_path = 'output/executions/'+_id+'/simulations/cerebellum_simple/1/simulation_notes.txt'
    with open(notes_path, 'r') as f: 
        text = f.read()
    return jsonify({'result': text})

@executions.route("/api/executions/new/", methods=["POST"])
@cross_origin()
def new():
    params = json.loads(request.data)
    # run_execution(params)
    print(params)
    
    return jsonify({'result': 'success'})
