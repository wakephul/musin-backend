from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from ..api import db

import json
import string
import random

from ..models.executions import Input

inputs = Blueprint('inputs', __name__)
@inputs.route("/api/inputs/list/", methods=["GET"])
@cross_origin()
def list():
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

@inputs.route("/api/inputs/new/", methods=["POST"])
@cross_origin()
def new():
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