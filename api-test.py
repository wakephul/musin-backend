from flask import Flask, send_file, jsonify, request, make_response
import nest

api = Flask(__name__)

nest.Install("cerebmodule")

@api.route("/api/", methods=["GET"])
def index():
    # nest.Install('cerebmodule')
    # nest.Create('poisson_generator')
    return "APIs workingg"

if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)
