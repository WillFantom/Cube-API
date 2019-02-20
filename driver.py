import json

import sys

import time

import RPi.GPIO as GPIO

frames = {}

frames_per_second = 8

SERIAL = 25
RCLK = 24
SRCLK = 23


# loads JSON based animation
def open_JSON():
    global frames
    _filename = "cube.json"
    if(len(sys.argv) > 1):
        _filename = sys.argv[1]
    with open(_filename, 'r') as f:
        data = json.load(f)
        frames = data["frames"]


# initialises the script
def initialise():
    open_JSON()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SERIAL, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)



# converts bit array into a single byte
def to_byte(bit_array):
    byte_val = 0b00000000
    for x in range(0, len(bit_array)):
        byte_val |= (bit_array[x] << x)
    return byte_val


def push_pin(pin_no, bit):
    GPIO.output(SRCLK, GPIO.LOW)
    val = 0
    if(bit == 1):
        val = 1
    GPIO.output(SERIAL, val)
    GPIO.output(SRCLK, GPIO.HIGH)


def push_byte(nth, byte):
    base_pin = 71
    start_pin = base_pin - (8 * nth)
    for x, y in zip(range(start_pin, start_pin - 8, -1), range(0, 8)):
        push_pin(x, ((byte >> y) & 0b00000001))


# displays a single layer (all 8 rows)
def display_layer(layer_no, layer):
    GPIO.output(RCLK, GPIO.LOW)
    z_state = 0b00000000
    z_state |= (1 << layer_no)
    push_byte(0, z_state)
    for x in range(1, len(layer) + 1):
        byte_val = to_byte(layer[x - 1])
        push_byte(x, byte_val)
    GPIO.output(RCLK, GPIO.HIGH)


# displays a given frame (all 8 layers)
def display_frame(frame_index):
    frame_layers = frames[frame_index]["layers"]
    for x in range(len(frame_layers) -1, -1, -1):
        display_layer(7 - x, frame_layers[x])


def main_loop():
    index = 0
    index_goal = len(frames) - 1
    frame_time = float(1.0 / frames_per_second)
    current_time = 0
    tmp_time = 0
    while(True):
        display_frame(index)
        tmp_time = time.clock()
        if((tmp_time - current_time) >= frame_time):
            index = index + 1
            if(index == index_goal):
                index = 0
            current_time = tmp_time

initialise()
print("Line for the best GUI guy ever!")
try:
	main_loop()
except valueError:
	print("it was a value error")
except IOError, e:
	if e.errno == errno.EPIPE:
		print("Fucked IO")

# to run:
# python driver.py cube.json
# to run with frames per second setting:
# python driver.py cube.json <30 etc.>
