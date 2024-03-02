from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from api.api import db

import glob
import json
from csv import DictReader
from api.utils.images import get_response_image

from api.models.executions import Execution, Executiontype, ExecutionExecutiontypeRelationship, ExecutionNetworkSideInputRelationship, ExecutionResult
from api.models.inputs import Input
from api.models.networks import Network, NetworkParameter

from api.src.run import run_execution

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
        # inputs = ExecutionInputRelationship.get_by_execution_code(execution['code'])
        # execution['inputs'] = [Input.get_name(input['input_code']) for input in inputs]
        # print(execution)
        # networks = ExecutionNetworkRelationship.get_by_execution_code(execution['code'])
        # execution['networks'] = [Network.get_name(network['network_code']) for network in networks]
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
    if request.method == 'POST':
        params = json.loads(request.data)
        #if there are new inputs, save them and their corresponding parameters in the database
        if 'new_inputs' in params:
            inputs = params['new_inputs']
            for input in inputs:
                input_code = Input.create(input)
                params['new_inputs'][inputs.index(input)]['code'] = input_code
            print('updated inputs:', params['new_inputs'])
        
        if 'name' in params and 'networks' in params and len(params['networks']) > 0 and 'execution_type' in params:
            #first I run all the checks, then I save stuff in the database
            for network in params['networks']:
                network_exists = Network.get_one(network['code'])
                if not network_exists:
                    # network_code = Network.create(network['name'], network['sides'])
                    # for parameter in network['parameters']:
                    #     NetworkParameter.create(network_code, parameter['name'], parameter['value'])
                    return jsonify({'result': 'error', 'message': 'Network not found'})
                if 'inputsForSides' in network:
                    one_input = False
                    for side in network['inputsForSides']:
                        if 'inputs' in side and len(side['inputs']) > 0:
                            for input_code in side['inputs']:
                                input_exists = Input.get_one(input_code)
                                if not input_exists:
                                    return jsonify({'result': 'error', 'message': 'Input not found'})
                                one_input = True
                    if not one_input:
                        return jsonify({'result': 'error', 'message': 'No inputs for sides selected'})
                else:
                    return jsonify({'result': 'error', 'message': 'No inputs for sides'})

            execution_code = Execution.create(params['name'])
            execution_type_code = params['execution_type']
            execution_type_exists = Executiontype.get_one(execution_type_code)
            if not execution_type_exists:
                return jsonify({'result': 'error', 'message': 'Execution type not found'})
            print('execution - execution type relationship:', execution_code, execution_type_code)
            ExecutionExecutiontypeRelationship.create(execution_code, execution_type_code)
            for network in params['networks']:
                network_code = network['code']
                for side in network['inputsForSides']:
                    for input_code in side['inputs']:
                        ExecutionNetworkSideInputRelationship.create(execution_code, network_code, network['inputsForSides'].index(side), input_code)
        else:
            return jsonify({'result': 'error', 'message': 'Missing some description to run'})
        
        run_execution(params)
        
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'error'})
    
#add route to get all execution types
@executions.route("/api/executions/types/", methods=["GET"])
@cross_origin()
def types():
    executiontypes = Executiontype.get_all()
    return jsonify({'result': executiontypes})
