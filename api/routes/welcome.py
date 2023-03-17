from flask import Blueprint

welcome = Blueprint('welcome', __name__)

@welcome.route("/api/")
def api_welcome():
    return "APIs are up and running correctly!"