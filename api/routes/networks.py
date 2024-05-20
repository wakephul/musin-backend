from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from api.api import db

from pathlib import Path

from api.models.networks import Network, NetworkParameter

networks = Blueprint('networks', __name__)
@networks.route("/api/networks/list/", methods=["GET"])
@cross_origin()
def list():
    networks = []
    if request.method == 'GET':
        networks = Network.get_all()
        for network in networks:
            parameters = NetworkParameter.get_by_network_code(network['code'])
            network['parameters'] = parameters

    return jsonify({'result': networks})

@networks.route("/api/networks/<_type>/<_name>/", methods=["GET"])
@cross_origin()
def details(_type, _name):
    network = Network.get_one(_name)
    parameters = NetworkParameter.get_by_network_code(network['code'])
    filename = Path('api/src/nest/networks/'+_type+'/'+_name+'.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})