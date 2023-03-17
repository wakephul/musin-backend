from flask import Blueprint

networks = Blueprint('networks', __name__)
@networks.route("/existing_networks")
def existing_networks():
    return "List of existing networks"