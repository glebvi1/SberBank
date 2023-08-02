from django.urls import path

from system_admin.views import (CardHistoryView, UsersListView, UserView,
                                search_users, unban)

app_name = "system_admin"

urlpatterns = [
    path("all_users/", UsersListView.as_view(), name="all_users"),
    path("all_users/page/<int:page>/", UsersListView.as_view(), name="paginator"),
    path("search_users/", search_users, name="search_users"),

    path("unban/<int:user_id>/", unban, name="unban"),
    path("user_view/<int:user_id>/", UserView.as_view(), name="user_view"),

    path("user_view/<int:user_id>/card_view/<int:card_id>", CardHistoryView.as_view(), name="card_view"),
    path("user_view/<int:user_id>/card_view/<int:card_id>/page/<int:page>/", CardHistoryView.as_view(), name="paginator_history"),
]
