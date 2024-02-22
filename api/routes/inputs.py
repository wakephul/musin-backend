from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from api.api import db

import json
import string
import random

from api.models.inputs import Input

inputs = Blueprint('inputs', __name__)
@inputs.route("/api/inputs/list/", methods=["GET"])
@cross_origin()
def list():
    result = []
    if request.method == 'GET':
        inputs = Input.get_all()
        
    return jsonify({'result': inputs})

@inputs.route("/api/inputs/new/", methods=["POST"])
@cross_origin()
def new():
    if request.method == 'POST':
        params = json.loads(request.data)
        
    return jsonify({'result': params})