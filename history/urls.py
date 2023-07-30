from django.urls import path

from history.views import CardHistoryListView, StatisticsView

app_name = "history"

urlpatterns = [
    path("card/<int:card_id>/", CardHistoryListView.as_view(), name="card_history"),
    path("card/<int:card_id>/page/<int:page>/", CardHistoryListView.as_view(), name="paginator_history"),
    path("statistics/<int:card_id>/", StatisticsView.as_view(), name="statistics"),
]
