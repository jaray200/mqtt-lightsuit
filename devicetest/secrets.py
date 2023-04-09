firstname = 'Whitney'
lastname = 'Southam'
idnumber = '2'
ssidhome = 'NESsy'
pwhome = 'g1r4ff3s'
ssidnwr = 'Nebula'
pwnwr = 'NWRits5727!'
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
    'brokerip' : '192.168.1.133',
    'brokerport' : 1883,
    'client_id' : client_id,
    'subtopic' : bytes(subtopic, 'utf8'),
    'pubtopic' : bytes(pubtopic, 'utf8')
    }