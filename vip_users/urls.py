from django.urls import path

from vip_users.views import create_category, CategoriesListView

app_name = "vip_users"

urlpatterns = [
    path("categories/", CategoriesListView.as_view(), name="all_categories"),
    path("categories/create", create_category, name="create_category"),
]
