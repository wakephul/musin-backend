from flask import Blueprint, jsonify, send_file
from flask_cors import cross_origin
from api.api import db

from pathlib import Path

plots = Blueprint('plots', __name__)
#TODO! da aggiungere gestione plots
@plots.route("/api/plots/<_name>/", methods=["GET"])
@cross_origin()
def details(_type, _name):
    filename = Path('api_data/config/plots_config.json')
    if filename.is_file():
        return send_file(filename)
    else: 
        return jsonify({'result': 'error'})