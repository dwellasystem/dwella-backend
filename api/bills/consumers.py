import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BillNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Import inside the method to avoid AppRegistryNotReady
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import AccessToken

        User = get_user_model()

        query_params = self.scope["query_string"].decode()
        token = None
        if "token=" in query_params:
            token = query_params.split("token=")[1]

        self.user = None
        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token["user_id"]
                self.user = await self.get_user(user_id)
            except Exception:
                pass

        if self.user:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_request_notification(self, event):
        await self.send(json.dumps({
            "message": "new_request",
            "count": event["count"],
        }))

    async def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return None
