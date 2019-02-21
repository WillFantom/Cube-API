from flask import Flask, request, abort, jsonify
from threading import Thread
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

## Stoarge
config_file_path = "/home/pi/cube/config.json"
animations_dir_path = "/home/pi/cube/animations/"

class CubeController():

    def __init__(self):

        ### Animation
        self.animation_thread = None
        self.frame_time = 0

        ### Pi
        self.SERIAL = 25
        self.RCLK = 24
        self.SRCLK = 23
        self.init_gpio()

        ### Data Stores
        self.config_data = self.load_config()
        self.animation_data = {}

        ### Start Animation
        self.start_animation(self.config_data["animation_name"])

    def init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.SERIAL, GPIO.OUT)
        GPIO.setup(self.RCLK, GPIO.OUT)
        GPIO.setup(self.SRCLK, GPIO.OUT)

    def load_config(self):
        ''' load in the configuration file + validate '''
        try:
            with open(config_file_path, "r") as f:
                config = json.load(f)
        except:
            print("! Config file does not exist")
            exit(1)
        if self.validate_configuration(config) == True:
            print("> Config file loaded")
            return config
        else:
            print("! Invalid configuration file")
            exit(1)

    def start_animation(self, animation_name):
        ''' Create new animation thread '''
        try:
            with open(animations_dir_path + animation_name + ".json", "r") as f:
                animation = json.load(f)
            if self.validate_animation(animation) == True:
                print("> Valid animation loading")
                self.kill_animation()
                self.animation_data = animation
                self.frame_time = float(1/int(animation["fps"]))
                self.animation_thread = Thread(target=self.display_loop, args=[animation])
                self.animation_thread.start()
                print("> Animation ["+ animation_name +"] loaded")
            else:
                print("! Invalid animation file")
                self.kill_animation()
        except:
            print("! Animation file does not exist: %s", animation_name + ".json")
            self.kill_animation()

    def kill_animation(self):
        if not self.animation_thread == None:
            print("> Killing animation")
            self.animation_data = {}
            time.sleep(1.0)
            self.animation_thread.join()
            self.animation_thread = None
            print("> Animation Killed")


    def validate_animation(self, animation):
        if "name" in animation:
            if "fps" in animation:
                if type(animation["fps"]) is int:
                    if animation["fps"] > 0:
                        if "frames" in animation:
                            if len(animation["frames"]) > 0:
                                if "layers" in animation["frames"][0]:
                                    if len(animation["frames"][0]["layers"]) == self.config_data["cube_height"]:
                                        return True
        return False

    def validate_configuration(self, config):
        if "version" in config:
            if "animation_name" in config:
                if "cube_height" in config:
                    if type(config["cube_height"]) is int:
                        if config["cube_height"] > 0:
                            if "cube_width" in config:
                                if type(config["cube_width"]) is int:
                                    if config["cube_width"] > 0:
                                        return True
        return False

    def display_loop(self, animation):
        ''' Play the current animation (in alt thread)'''
        while self.animation_data == animation:
            for frame in animation["frames"]:
                frame_start_t = time.time()
                while (time.time() - frame_start_t) <= self.frame_time:
                    self.display_frame(frame)

    def display_frame(self, frame):
        ''' Display a given frame on the cube '''
        for idx, layer in enumerate(frame["layers"][::-1]):
            self.display_layer(idx, layer)

    def display_layer(self, idx, layer):
        ''' Display a given layer on the cube '''
        # Write layer Height
        GPIO.output(self.RCLK, GPIO.LOW)
        height = 0b00000000
        height |= (1 << idx)
        self.out_byte(0, height)

        # Write Layer Data
        for idx, layer_data in enumerate(layer):
            self.out_layer(idx, layer_data)
        GPIO.output(self.RCLK, GPIO.HIGH)

    def out_layer(self, idx, layer):
        ''' Write the layer data as a byte to the pi '''
        byte = 0b00000000
        for idx, bit in enumerate(layer):
            byte |= (bit << idx)
        self.out_byte(idx+1, byte)
        
    def out_byte(self, n, byte):
        ''' Output a byte via GPIO '''
        base_pin = 71
        start_pin = base_pin - (8*n)
        for x, y in zip(range(start_pin, start_pin - 8, -1), range(0, 8)):
            self.push_pin(x, ((byte >> y) & 0b00000001))

    def push_pin(self, no, bit):
        ''' Push bit via a pin on GPIO header '''
        GPIO.output(self.SRCLK, GPIO.LOW)
        val = 0
        if(bit == 1):
            val = 1
        GPIO.output(self.SERIAL, val)
        GPIO.output(self.SRCLK, GPIO.HIGH)

contoller = CubeController()

##### API #####

@app.route(url_base + "add-animation", methods=["POST"])
def add_animation():
    if not request.json:
        abort(400)
    ### Do JSON Validation Here
    # For Example
    if not "name" in request.json:
        abort(400)
    with open(animations_dir_path + request.json["name"].lower() + ".json", "w+") as f:
        json.dumps(request.json, f)
    return jsonify({'code': 0}), 201

@app.route(url_base+"setanimation/<name>")
def set_animation(name):
    print("? Set Animation: " + name)
    contoller.start_animation(name)
    return "okay"

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")
    
###############

