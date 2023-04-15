firstname = 'Noah'
lastname = 'Davidson'
idnumber = '3'
ssidhome = 'NESsy'
pwhome = 'g1r4ff3s'
ssidnwr = 'Nebula'
pwnwr = 'NWRits5727!'
brokeriphome = '192.168.1.22'
brokeripnwr = '192.168.1.133'
client_id = f"{firstname}_{lastname}_{idnumber}"
topic_id = client_id.lower()
subtopic1 = f"lightsuit/{topic_id}/power"
subtopic2 = f"lightsuit/{topic_id}/flicker"
pubtopic = f"lightsuit/{topic_id}/status"
mqtt_username = 'mqtt-user'
mqtt_key = '@1phabeta'

secrets = {
    'ssid': ssidnwr,
    'pw': pwnwr,
    'mqtt_username' : mqtt_username,
    'mqtt_key' : mqtt_key,
    'brokerip' : brokeripnwr,
    'brokerport' : 1883,
    'client_id' : client_id,
    'subtopic1' : bytes(subtopic1, 'utf8'),
    'subtopic2' : bytes(subtopic2, 'utf8'),
    'pubtopic' : bytes(pubtopic, 'utf8')
    }                 