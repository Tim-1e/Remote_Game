import json
import gameObjects

class Msg:
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def to_bytes(self):
        return json.dumps({'type': self.type, 'data': self.data})
    
    def from_bytes(data):
        info = json.loads(data)
        return Msg(info['type'], info['data'])
    
class ClientMsg:
    def __init__(self, ):
        pass
    
class ServerMsg:
    def __init__(self, tanks, bullet_pool):
        self.tanks = tanks
        self.bullet_pool = bullet_pool

    def to_bytes(self):
        pass
