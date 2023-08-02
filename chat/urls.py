from django.urls import path

from chat.views import ChatView

app_name = "chat"

urlpatterns = [
    path("room/<int:user_id>", ChatView.as_view(), name="room"),
]
