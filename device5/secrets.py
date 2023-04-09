firstname = 'Nathan'
lastname = 'Winter'
idnumber = '5'
ssidhome = 'NESsy'
pwhome = 'g1r4ff3s'
ssidnwr = 'Nebula'
pwnwr = 'NWRits5727!'
brokeriphome = '192.168.1.22'
brokeripnwr = '192.168.1.133'
client_id = f"{firstname}_{lastname}_{idnumber}"
topic_id = client_id.lower()
subtopic = f"lightsuit/{topic_id}/state"
pubtopic = f"lightsuit/{topic_id}/status"
mqtt_username = 'mqtt-user'
mqtt_key = '@1phabeta'

secrets = {
    'ssid': ssidnwr,
    'pw': pwnwr,
    'mqtt_username' : mqtt_username,
    'mqtt_key' : mqtt_key,
    'brokerip' : brokeriphome,
    'brokerport' : 1883,
    'client_id' : client_id,
    'subtopic' : bytes(subtopic, 'utf8'),
    'pubtopic' : bytes(pubtopic, 'utf8')
    }