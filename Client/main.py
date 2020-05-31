from network import WLAN
import pycom
from machine import UART, Pin, ADC, RTC
import machine
from LTR329ALS01 import LTR329ALS01
import ujson
import utime as time
import sock
from pysense import Pysense
import network
import _thread
import uos
from umqtt import MQTTClient
from setup_led import find_led, obs_min, obs_max, increment

pycom.heartbeat(False)
pycom.rgbled(0xFF0000)


wlan = network.WLAN(mode=network.WLAN.STA)

# # # # # # # # #
# CONNECT WIFI  #
# # # # # # # # #

wifi_name = 'weirdchamp'
wifi_pass = 'banana12'

def connect_wifi():
    wlan.connect(ssid=wifi_name, auth=(network.WLAN.WPA2, wifi_pass))
    start = time.time()
    while not wlan.isconnected():
        current = time.time()
        if(current > start+5 ):
            # Sometimes the wifi connection is stuck, try to connect again with recursive call
            connect_wifi()
        machine.idle()

connect_wifi()
print("CONNECTED")
pycom.rgbled(0x111111)

rtc = RTC()
rtc.ntp_sync("pool.ntp.org") #Sync the time hopefully

while(not rtc.synced()):
    time.sleep(0.5)

real_time_in_milli = time.time() * 1000
zero_time = time.ticks_ms()


# # # # # # # # #
# Create light  #
#     sensor    #
# # # # # # # # #

py = Pysense()
lt = LTR329ALS01(pysense=py, integration=LTR329ALS01.ALS_INT_50, rate=LTR329ALS01.ALS_RATE_500, gain=LTR329ALS01.ALS_GAIN_48X)

time.sleep(2) # need small break to not break everything

# # # # # # # # #
#  Setup  MQTT  #
#     Client    #
# # # # # # # # #

device_id = "device"
broker_address = "broker.hivemq.com"

mqtt_client = MQTTClient(device_id, broker_address, port=1883)
mqtt_client.connect()

mode = 0 # mode determines auto/manual/rgb
set_point = 0 # user received setpoint
current_led = 0
user_intensity = 0 # manual mode intensity
timestamp = real_time_in_milli + time.ticks_ms() - zero_time
has_started = False # should not start listening for messages until end
should_check_time = True # ensures only one difference is printed

def handle_msg(topic, msg):
    """
    Looks like in umqtt.py that "set_callback" has to be provided for stuff to work
    This method will be provided as "set_callback" in client
    """

    global set_point
    global user_intensity
    global mode
    global should_check_time
    global current_led
    
    topic = topic.decode("utf8")
    message = ujson.loads(msg.decode("utf8"))

    if has_started:

        if topic == "sdu/iot/gruppe9/intensity": # set mode 0
            print("intensity")
            mode = 0
            try:
                user_intensity = int(message["var"])
            except:
                pass
        if topic == "sdu/iot/gruppe9/setpoint": # set mode 1
            print("setpoint")
            mode = 1
            try:
                set_point = int(message["var"])
                if set_point < obs_min:
                    set_point = obs_min
                elif set_point > obs_max:
                    set_point = obs_max
                should_check_time = True
                current_led = find_led(set_point)
                timestamp = float(message["time"])
            except:
                pass
        if topic == "sdu/iot/gruppe9/rgb": # set mode 2
            try:
                rgb = int(message["var"])
                mode = 2
                print("rgb mode")
                pycom.rgbled(rgb)
            except:
                pass

mqtt_client.set_callback(handle_msg)

def subscribe():
    mqtt_client.subscribe(topic="sdu/iot/gruppe9/rgb")
    mqtt_client.subscribe(topic="sdu/iot/gruppe9/intensity")
    mqtt_client.subscribe(topic="sdu/iot/gruppe9/setpoint")


subscribe() # like and subscribe to topics


def reconnect_mqtt():
    try:
        mqtt_client.connect()
        subscribe()
    except:
        time.sleep(1)
        reconnect_mqtt()
        

def check_messages():
    try:
        mqtt_client.check_msg()

    except OSError as e:
        if not wlan.isconnected():
            connect_wifi()
            reconnect_mqtt()
        else: 
            reconnect_mqtt()

# # # # # # # # # # #
#   set point algo  #
# # # # # # # # # # #

# Dictonary used to know what light level to change to, 
# first value in tuple is when needs lowering, and second is when need increasing

color_list_for_intensity = [
    0x000000, 0x111111, 0x222222, 
    0x333333, 0x444444, 0x555555, 
    0x666666, 0x777777, 0x888888, 
    0x999999, 0xAAAAAA, 0xBBBBBB, 
    0xCCCCCC, 0xDDDDDD, 0xEEEEEE, 
    0xFFFFFF
]

check_count = 0  # Check if there is still no one in the room or more than 10 people
people_in_room = 1  # No people inside a room to begin with
start = time.time()
rand = int(time.time())
add_person_limit = 12
leave_person_limit = 11
alerted = False
empty_room = False


# # # # # # # # #
#  enter/leave  #
#      room     #
# # # # # # # # #


def lcg():
    global rand
    a = 18
    c = 11
    m = 17
    rand = (a * rand + c) % m
    return rand


def room_count():
    global check_count, people_in_room, add_person_limit, leave_person_limit

    action = lcg()  # Integer to decide whether or not a person enters or leaves the room
    # Even number means entering, odd number means leaving
    if action < add_person_limit:
        people_in_room += 1
        if people_in_room > 10:
            check_count += 1
        else:
            check_count = 0
    elif people_in_room == 0:
        people_in_room = 0
        check_count += 1
    elif action > leave_person_limit:
        people_in_room -= 1
        if people_in_room == 0:
            check_count += 1
        else:
            check_count = 0


def check_every_30_seconds():
    global start
    end = time.time()
    if end > start + 30:
        room_count()
        start = time.time()


# # # # # # # # #
#     thread    #
#  mqtt subscr  #
# # # # # # # # #


def auto_light_change():
    global check_count, current_led, add_person_limit, leave_person_limit, alerted, empty_room, timestamp, set_point, should_check_time


    current_light = lt.light()[0]
    check_every_30_seconds()

    # COVID-19 case, more than 10 people will alert the room, this if block need to be in auto
    if people_in_room > 10 and check_count == 2 and not alerted:
        print("DANGER MORE THAN 10 PEOPLE")
        add_person_limit = 5
        leave_person_limit = 4
        check_count = 0
        alerted = True
    elif people_in_room == 0 and check_count == 2 and not empty_room:
        print("NO ONE IS HERE")
        pycom.rgbled(0x000000)  # Turn off the light 
        add_person_limit = 12
        leave_person_limit = 11
        check_count = 0
        empty_room = True
    elif not empty_room and not alerted or 0 < people_in_room < 11:
        # This is where the LED might change in response to the current light level and the given set point
        # This needs to be in a loop or called every x minute.
        empty_room = False
        alerted = False
        percent = 0.12
        lower = ((1.0-percent) * set_point)
        upper = ((1.0+percent) * set_point)

        if lower <= current_light <= upper: # do nothing
            print("set_point: " + str(set_point))
            print("current_light: " + str(current_light))
            if should_check_time:
                ending_stamp = real_time_in_milli + time.ticks_ms() - zero_time
                diff = ending_stamp - timestamp
                print(diff)
                should_check_time = False
        elif current_light > set_point + increment: # has to decrement
            if current_led > 0:
                current_led -= 1
        elif current_light < set_point + increment: # has to increment
            if current_led < 16:
                current_led+= 1

        pycom.rgbled(color_list_for_intensity[current_led])


def manual_light_change(intensity):

    global color_list_for_intensity
    try:
        INTensity = int(intensity)
    except:
        pass
    if INTensity < 0:
        pycom.rgbled(color_list_for_intensity[0])
    elif INTensity > len(color_list_for_intensity):
        pycom.rgbled(color_list_for_intensity[15])
    else:
        pycom.rgbled(color_list_for_intensity[int(intensity)])


def do_light():


    global user_intensity
    global mode

    if mode == 0: # MANUAL
        manual_light_change(user_intensity) 
    if mode == 1: # AUTO
        auto_light_change()
    if mode == 2: # RGB
        pass
    check_messages()


def subscribe_to_updates():
    while True:
        try:
            do_light()
        except:
            reconnect_mqtt()
            time.sleep(5)
        time.sleep(1)


# # # # # # # # #
#    thread     #
# mqtt  publish #
# # # # # # # # #


# TODO: this looks like it is working
topic = "sdu/iot/gruppe9/light"

def message_for_server():


    global user_intensity
    global set_point
    global mode

    light_level = lt.light()[0]
    string_mode = "MANUAL"
    var = user_intensity
    if mode == 1:
        string_mode = 'AUTO'
        var = set_point
    if mode == 2:
        string_mode = 'RGB'
        var = 0

    true_time = real_time_in_milli + time.ticks_ms() - zero_time
    message = {
        "name": device_id,
        "time": str(true_time),
        "light": str(light_level),
        "mode": string_mode,
        "var": str(var)
    }
    mqtt_client.publish(topic=topic, msg=ujson.dumps(message))
        

def publish_light_to_server():
    while True:
        try:
            message_for_server()
        except:
            reconnect_mqtt()
            time.sleep(5)
        time.sleep(1)


# # # # # # # # #
#     start     #
#  the threads  #
# # # # # # # # #


has_started = True
_thread.start_new_thread(publish_light_to_server, tuple())
_thread.start_new_thread(subscribe_to_updates(), tuple())
pycom.rgbled(0x000000)
start = time.time()
while True:


    end = time.time()
    # if start + 10 > end >= start + 5:
    #     pycom.rgbled(color_list_for_intensity[0])
    # elif start + 15 > end >= start + 10:
    #     pycom.rgbled(color_list_for_intensity[1])
    # elif start + 20 > end >= start + 15:
    #     pycom.rgbled(color_list_for_intensity[2])    
    # elif start + 25 > end >= start + 20:
    #     pycom.rgbled(color_list_for_intensity[3])
    # elif start + 30 > end >= start + 25:
    #     pycom.rgbled(color_list_for_intensity[4])    
    # elif start + 35 > end >= start + 30:
    #     pycom.rgbled(color_list_for_intensity[5])
    # elif start + 40 > end >= start + 35:
    #     pycom.rgbled(color_list_for_intensity[6])
    # elif start + 45 > end >= start + 40:
    #     pycom.rgbled(color_list_for_intensity[7])
    # elif start + 50 > end >= start + 45:
    #     pycom.rgbled(color_list_for_intensity[8])
    # elif start + 55 > end >= start + 50:
    #     pycom.rgbled(color_list_for_intensity[9])    
    # elif start + 60 > end >= start + 55:
    #     pycom.rgbled(color_list_for_intensity[10])
    # elif start + 65 > end >= start + 60:
    #     pycom.rgbled(color_list_for_intensity[11])    
    # elif start + 70 > end >= start + 65:
    #     pycom.rgbled(color_list_for_intensity[12])
    # elif start + 75 > end >= start + 70:
    #     pycom.rgbled(color_list_for_intensity[13])
    # elif start + 80 > end >= start + 75:
    #     pycom.rgbled(color_list_for_intensity[14])
    # elif start + 85 > end >= start + 80:
    #     pycom.rgbled(color_list_for_intensity[15])
    # else:
    #     pass

    if end >= start + 21:
        pycom.rgbled(color_list_for_intensity[15])
        
    time.sleep(0.5)
    light_level = lt.light()[0]
    message = {
        "light": str(light_level),
    }
    mqtt_client.publish(topic=topic, msg=ujson.dumps(message))
