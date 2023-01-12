from flask import Flask, send_file, jsonify, request, make_response

api = Flask(__name__)

if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True)
