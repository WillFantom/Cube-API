from flask import Flask, request, abort, jsonify
import json

app = Flask(__name__)

url_base = "/cube/api/v1/"
animations_dir_path = "/home/.../" ## SET THIS

@app.route(url_base + "add-animation", methods=["POST"])
def add_animation():
    if not request.json:
        abort(400)
    ### Do JSON Validation Here
    # For Example
    if not "name" in request.json:
        abort(400)
    #
    with open(animations_dir_path + request.json["name"].lower() + ".json", "w+") as f:
        json.dumps(request.json, f)
    return jsonify({'code': 0}), 201

@app.route(url_base + "set-animation", methods=["GET"])
def set_animation():
    if not request.json:
        abort(400)
    ### Do JSON Validation Here
    # For Example
    if not "name" in request.json:
        abort(400)
    #
    try:
        with open(animations_dir_path + request.json["name"].lower() + ".json", "r") as f:
            print("Put the code to set the animation here!!")
        return jsonify({'code': 0})
    except:
        return jsonify({'code': 1}) # Return some sort of error code (Valid Request -> Invalid File)


if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")