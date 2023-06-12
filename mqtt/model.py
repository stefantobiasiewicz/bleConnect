

class MQTTConnectionDTO:
    def __init__(self, broker_address='localhost', port=1883, client_id="", clean_session=True, username=None, password=None, keepalive=60):
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id
        self.clean_session = clean_session
        self.username = username
        self.password = password
        self.keepalive = keepalive
