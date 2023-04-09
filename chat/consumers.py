import json
from channels.generic.websocket import WebsocketConsumer


# FIXME: This is temp code just to make sure my middleware is working!
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        self.accept()
        self.send(text_data=json.dumps({"message": user.username}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
