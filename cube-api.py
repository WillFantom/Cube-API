from flask import Flask, request, abort, jsonify
import RPi.GPIO as GPIO
import json
import sys
import time

'''
3D Cube LED Matrix

Many comments here just to help Chris understand
'''

## For REST API
app = Flask(__name__)
url_base = "/cube/api/v1/"

## Animations
config_file_path = "/home/.../"
animations_dir_path = "/home/.../"
config_data = {}
current_animation = {}
fps = 8
frame_time = float(1.0 / fps)
animation_thread = None

## Pi
SERIAL = 25
RCLK = 24
SRCLK = 23

def init():
    ''' Load in the required files from the file system '''
    load_config()
    load_animation(config_data["current_animation"])
    start_animation()

def start_animation():
    ''' Create new animation thread '''
    raise NotImplementedError

def display_loop(animation):
    ''' Play the current animation (in alt thread)'''
    while current_animation == animation:
        for frame in animation["frames"]:
            frame_start_t = time.now()
            while (time.now() - frame_start_t) <= frame_time:
                display_frame(frame)

def load_config():
    ''' load in the configuration file + validate '''
    raise NotImplementedError

def load_animation(animation_name):
    ''' load in the given animation from the fs '''
    raise NotImplementedError

def display_frame(frame):
    ''' Display a given frame on the cube '''
    for layer in frame["layers"]:
        display_layer(layer)

def display_layer(layer):
    ''' Display a given layer on the cube '''
    raise NotImplementedError


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
    init()