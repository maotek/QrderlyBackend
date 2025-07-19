# restaurants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("api/restaurants/", views.restaurant_detail_by_code, name="restaurant-detail-by-code"),
    path("api/tables/", views.table_detail_by_code, name="table-detail-by-code"),
    path("api/auth/login/", views.staff_login, name="staff-login"),
    path("api/auth/me/", views.current_user, name="current-user"),
    path("api/auth/logout/", views.staff_logout, name="staff-logout"),
]
