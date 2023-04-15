import rp2
import network
import array
import ubinascii
import machine
import time
from secrets import secrets
import socket
from umqtt.simple import MQTTClient
from machine import Pin
import random

def sub_cb(topic, msg):
    print((topic, msg))
    global LED_MODE, LED_STATE
    if msg == b'Solid':
        print("Solid Received")
        LED_MODE = 0
        solid_lights()
    if msg == b'Flicker':
        print("Flicker Received")
        LED_MODE = 1
        flicker_lights()
    if msg == b'On':
        print('Device received On message on subscribed topic')
        LED_STATE = 1
        led.value(1)
        if LED_MODE == 0:
            solid_lights()
        if LED_MODE == 1:
            flicker_lights()
    if msg == b'Off':
        print('Device received Off message on subscribed topic')
        LED_STATE = 0
        led.value(0)
        lights_off()
        sm_ledbranch1.restart()
        sm_ledbranch2.restart()


def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    
    #client = MQTTClient(client_id, brokerip)
    client = MQTTClient(client_id, brokerip, brokerport, brokerusername, brokerpassword, keepalive=30)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(sub_topic1)
    client.subscribe(sub_topic2)
    #print('Connected to %s MQTT broker as client ID: %s, subscribed to %s topic' % (brokerip, client_id, sub_topic1))
    return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  
def pixels_show(speed,brightness):
    global NUM_LEDBRANCH1, NUM_LEDBRANCH2, ar_ledbranch1, ar_ledbranch2, ar_flicker1, ar_flicker2, sm_ledbranch1, sm_ledbranch2
    dimmer_ar_ledbranch1 = array.array("I", [0 for _ in range(NUM_LEDBRANCH1)])
    dimmer_ar_ledbranch2 = array.array("I", [0 for _ in range(NUM_LEDBRANCH2)])
    if LED_MODE == 1 and LED_STATE == 1:
        for i,c in enumerate(ar_ledbranch1):
            if ar_flicker1[i] == 1:
                r = int(((c >> 8) & 0xFF) * (speed*brightness))
                g = int(((c >> 16) & 0xFF) * (speed*brightness))
                b = int((c & 0xFF) * (speed*brightness))
                dimmer_ar_ledbranch1[i] = (g<<16) + (r<<8) + b
            else:
                r = int(((c >> 8) & 0xFF)* (brightness))
                g = int(((c >> 16) & 0xFF) * (brightness))
                b = int((c & 0xFF) * (brightness))
                dimmer_ar_ledbranch1[i] = (g<<16) + (r<<8) + b
                
        for i,c in enumerate(ar_ledbranch2):
            if ar_flicker2[i] == 1:
                r = int(((c >> 8) & 0xFF) * (speed*brightness))
                g = int(((c >> 16) & 0xFF) * (speed*brightness))
                b = int((c & 0xFF) * (speed*brightness))
                dimmer_ar_ledbranch2[i] = (g<<16) + (r<<8) + b
            else:
                r = int(((c >> 8) & 0xFF)* (brightness))
                g = int(((c >> 16) & 0xFF) * (brightness))
                b = int((c & 0xFF) * (brightness))
                dimmer_ar_ledbranch2[i] = (g<<16) + (r<<8) + b   

    if LED_MODE == 0 and LED_STATE == 1:
        for i,c in enumerate(ar_ledbranch1):
            r = int(((c >> 8) & 0xFF)* (speed*brightness))
            g = int(((c >> 16) & 0xFF) * (speed*brightness))
            b = int((c & 0xFF) * (speed*brightness))
            dimmer_ar_ledbranch1[i] = (g<<16) + (r<<8) + b
        for i,c in enumerate(ar_ledbranch2):
            r = int(((c >> 8) & 0xFF)* (speed*brightness))
            g = int(((c >> 16) & 0xFF) * (speed*brightness))
            b = int((c & 0xFF) * (speed*brightness))
            dimmer_ar_ledbranch2[i] = (g<<16) + (r<<8) + b
    sm_ledbranch1.put(dimmer_ar_ledbranch1, 8)
    sm_ledbranch2.put(dimmer_ar_ledbranch2, 8)
    time.sleep_ms(10)

def pixels_set(color):
    ar_temp = (color[1]<<16) + (color[0]<<8) + color[2]
    return int(ar_temp)

def pixels_fill(color):
    global ar_ledbranch1, ar_ledbranch2
    for i in range(len(ar_ledbranch1)):
        ar_ledbranch1[i] = pixels_set(color)
    for j in range(len(ar_ledbranch2)):
        ar_ledbranch2[j] = pixels_set(color)


    
def color_brighten(color, speed, brightness):
    pixels_fill(color)
    for i in range(speed):
        pixels_show((i/speed),brightness)
def color_dim(color, speed, brightness):
    pixels_fill(color)
    for i in range(speed,0,-1):
        pixels_show((i/speed),brightness)

def flicker_state(ledbranch):
    return array.array("I", [random.randint(0,1) for _ in range(ledbranch)])

def flicker_lights():
    global ar_flicker1, ar_flicker2
    ar_flicker1 = flicker_state(NUM_LEDBRANCH1)
    ar_flicker2 = flicker_state(NUM_LEDBRANCH2)
    color_dim(WHITE,100,.1)
    time.sleep(0.2)
    color_brighten(WHITE,100,.1)
    time.sleep(0.2)

def solid_lights():
    color_brighten(WHITE,100,1)
    time.sleep(0.2)

    
def lights_off():
    color_dim(WHITE,100,.1)
    time.sleep(0.2)
    LED_STATE = 0

# Configure the number of WS2812 LEDs.
# LED_MODE 0=Solid, 1 = Flicker
LED_MODE = 0
#LED_STATE 0=Off, 1=On
LED_STATE = 0
NUM_LEDBRANCH1 = 10
NUM_LEDBRANCH2 = 10
PIN_LEDBRANCH1 = 22
PIN_LEDBRANCH2 = 21

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)

last_message = 0
message_interval = 2
counter = 0

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm_ledbranch1 = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_LEDBRANCH1))
sm_ledbranch2 = rp2.StateMachine(1, ws2812, freq=8_000_000, sideset_base=Pin(PIN_LEDBRANCH2))

# Start the StateMachine, it will wait for data on its FIFO.
sm_ledbranch1.active(1)
sm_ledbranch2.active(1)
ar_ledbranch1 = array.array("I", [0 for _ in range(NUM_LEDBRANCH1)])
ar_flicker1 = array.array("I", [0 for _ in range(NUM_LEDBRANCH1)])
ar_ledbranch2 = array.array("I", [0 for _ in range(NUM_LEDBRANCH2)])
ar_flicker2 = array.array("I", [0 for _ in range(NUM_LEDBRANCH2)])
lights_off()


# Display a pattern on the LEDs via an array of LED RGB values.
#ar = array.array("I", [0 for _ in range(NUM_LEDS)])

#
# Set country to avoid possible errors / https://randomnerdtutorials.com/micropython-mqtt-esp32-esp8266/
rp2.country('US')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
ssid = secrets['ssid']
pw = secrets['pw']
brokerusername = secrets['mqtt_username']
brokerpassword = secrets['mqtt_key']
brokerip = secrets['brokerip']
brokerport = secrets['brokerport']
sub_topic1 = secrets['subtopic1']
sub_topic2 = secrets['subtopic2']
pub_topic = secrets['pubtopic']
#client_id = ubinascii.hexlify(machine.unique_id())
#client_id = mac
client_id = secrets['client_id']

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)
    
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth
if wlan.status() != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(wlan.status()):
        led.on()
        time.sleep(.1)
        led.off()
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    
### Topic Setup ###



try:
    client = connect_and_subscribe()
except OSError as e:
    restart_and_reconnect()
  


while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            pub_msg = b'Hello #%d' % counter
            client.publish(pub_topic, pub_msg)
            last_message = time.time()
            counter += 1
        
            if LED_STATE == 1 and LED_MODE == 1:
                flicker_lights()
    except OSError as e:
        restart_and_reconnect()
        
    if LED_STATE == 1 and LED_MODE == 1:
        print("I am in the right state")
        flicker_lights()
        

    
        
