from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from api.api import db

import glob
import json
from csv import DictReader
from api.utils.images import get_response_image

from api.models.executions import Execution, ExecutionNetworkSideInputRelationship
from api.models.inputs import Input
from api.models.networks import Network

from api.src.run import run_execution

executions = Blueprint('executions', __name__)
    
@executions.route("/api/executions/list/", methods=["GET"])
@cross_origin()
def list():
    executions = Execution.get_all()

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
        if 'new_inputs' in params and len(params['new_inputs']) > 0:
            inputs = params['new_inputs']
            for input in inputs:
                input_code = Input.create(input)
                params['new_inputs'][inputs.index(input)]['code'] = input_code
        
        if 'name' in params and params['name'] != '' and 'networks' in params and len(params['networks']) > 0:
            #first I run all the checks, then I save stuff in the database
            for network in params['networks']:
                network_exists = Network.get_one(network['code'])
                if not network_exists:
                    # network_code = Network.create(network['name'], network['sides'])
                    # for parameter in network['parameters']:
                    #     NetworkParameter.create(network_code, parameter['name'], parameter['value'])
                    return jsonify({'result': 'error', 'message': 'Network not found'})
                # if 'inputsForSides' in network:
                #     one_input = False
                #     for side in network['inputsForSides']:
                #         if 'inputs' in side and len(side['inputs']) > 0:
                #             for input_code in side['inputs']:
                #                 input_exists = Input.get_one(input_code)
                #                 if not input_exists:
                #                     return jsonify({'result': 'error', 'message': 'Input not found'})
                #                 one_input = True
                #     if not one_input:
                #         return jsonify({'result': 'error', 'message': 'No inputs for sides selected'})
                # else:
                #     return jsonify({'result': 'error', 'message': 'No inputs for sides'})
            #the structure is --> inputsMap: {input_code: [{network_code: side_index}]}
            # inputsMap = {}
            if 'inputsMap' in params:
                for input_code in params['inputsMap']:
                    print('input_code', input_code)
                    for network_code in params['inputsMap'][input_code]:
                        for side_index in params['inputsMap'][input_code][network_code]:
                            input_exists = Input.get_one(input_code)
                            if not input_exists:
                                return jsonify({'result': 'error', 'message': 'Input not found'})
                            network_exists = Network.get_one(network_code)
                            if not network_exists:
                                return jsonify({'result': 'error', 'message': 'Network not found'})
            else:
                return jsonify({'result': 'error', 'message': 'No inputs map'})


            execution_code = Execution.create(params['name'])
            #TODO - check: loop through the relations between inputs and networks and save them in the database (table: ExecutionNetworkSideInputRelationship)
            for input_code in params['inputsMap']:
                for network_code in params['inputsMap'][input_code]:
                    for side_index in params['inputsMap'][input_code][network_code]:
                        ExecutionNetworkSideInputRelationship.create(execution_code, network_code, side_index, input_code)

            # for network in params['networks']:
            #     network_code = network['code']
            #     for side in network['inputsForSides']:
            #         for input_code in side['inputs']:
            #             ExecutionNetworkSideInputRelationship.create(execution_code, network_code, network['inputsForSides'].index(side), input_code)
        else:
            return jsonify({'result': 'error', 'message': 'Missing some description to run'})
        

        if not 'pairedInputs' in params:
            params['pairedInputs'] = True
            
        params['execution_code'] = execution_code
        run_execution(params)
        
        return jsonify({'result': 'success', 'message': 'Execution should have finished successfully'})
    else:
        return jsonify({'result': 'error'})