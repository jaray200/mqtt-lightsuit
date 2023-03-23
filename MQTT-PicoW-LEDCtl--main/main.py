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

# Configure the number of WS2812 LEDs.
NUM_LEDS = 1
PIN_NUM = 22
brightness = 0.2

last_message = 0
message_interval = 5
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
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(0)
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

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
sub_topic = secrets['subtopic']
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

def sub_cb(topic, msg):
    print((topic, msg))
    if msg == b'On':
        print('Device received On message on subscribed topic')
        led.value(1)
        sm.active(1)
        run_lights()
    if msg == b'Off':
        print('Device received Off message on subscribed topic')
        led.value(0)
        sm.active(0)
        sm.restart()


def connect_and_subscribe():
    print("1")
    global client_id, mqtt_server, topic_sub
    
    #client = MQTTClient(client_id, brokerip)
    client = MQTTClient(client_id, brokerip, brokerport, brokerusername, brokerpassword)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(sub_topic)
    print('Connected to %s MQTT broker as client ID: %s, subscribed to %s topic' % (brokerip, client_id, sub_topic))
    return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    time.sleep_ms(10)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        time.sleep(wait)
        pixels_show()
    time.sleep(0.2)
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        time.sleep(wait)
        
def run_lights():
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 150, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    WHITE = (255, 255, 255)
    COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

    print("fills")
    for color in COLORS:       
        pixels_fill(color)
        pixels_show()
        time.sleep(0.2)

    print("chases")
    for color in COLORS:       
        color_chase(color, 0.01)

    print("rainbow")
    rainbow_cycle(0)          

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
  except OSError as e:
    restart_and_reconnect()