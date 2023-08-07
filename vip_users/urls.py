from django.urls import path

from vip_users.views import (CategoriesListView, MonthStatisticsCategory,
                             StatisticsForCategory, bind_transaction, buy_vip,
                             create_category)

app_name = "vip_users"

urlpatterns = [
    path("buy_vip/", buy_vip, name="buy_vip"),

    path("categories/", CategoriesListView.as_view(), name="all_categories"),
    path("categories/create", create_category, name="create_category"),
    path("categories/bind/<int:card_id>/<int:transaction_id>/", bind_transaction, name="bind_transaction"),

    path("statistics/<int:month>/<int:year>/", MonthStatisticsCategory.as_view(), name="statistics"),
    path("statistics/<int:category_id>/<int:month>/<int:year>/", StatisticsForCategory.as_view(), name="statistics_for_category"),
]
