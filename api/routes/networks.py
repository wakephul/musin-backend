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
        conn = mysql.get_db()
        query = "SELECT `code`, `name`, `default_parameters` FROM `networks`"
        networks = select_rows(conn, query)
        if networks:
            for net in networks:
                query = "SELECT `name`, `raster`, `voltage`, `train`, `test`, `split`, `population_name` FROM `plots` WHERE network = %s"
                net['plots'] = select_rows(conn, query, (net['name']))

    return jsonify({'result': networks})

@networks.route("/api/networks/<_type>/<_name>/", methods=["GET"])
@cross_origin()
def details(_type, _name):
    filename = Path('api_data/config/networks/'+_type+'/'+_name+'.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})