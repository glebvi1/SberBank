from django.urls import path

from vip_users.views import (CategoriesListView, CategoryEditView,
                             CreateCategoryView, MonthStatisticsCategory,
                             StatisticsForCategory, bind_transaction, buy_vip,
                             delete_category)

app_name = "vip_users"

urlpatterns = [
    path("buy_vip/", buy_vip, name="buy_vip"),

    path("categories/", CategoriesListView.as_view(), name="all_categories"),
    path("category/create", CreateCategoryView.as_view(), name="create_category"),
    path("category/edit/<int:pk>", CategoryEditView.as_view(), name="edit_category"),
    path("category/delete/<int:pk>", delete_category, name="delete_category"),

    path("category/bind/<int:card_id>/<int:transaction_id>/<int:page>/", bind_transaction, name="bind_transaction"),

    path("statistics/<int:month>/<int:year>/", MonthStatisticsCategory.as_view(), name="statistics"),
    path("statistics/<int:category_id>/<int:month>/<int:year>/", StatisticsForCategory.as_view(),
         name="statistics_for_category"),
]
