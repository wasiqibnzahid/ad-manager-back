from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin/create-user', views.create_user, name='create_user'),
    path('admin/update-user', views.update_user, name='update_user'),
    path("user", views.user_info_view, name="user_info"),
    path("report", views.create_report, name="report"),
    path("ad_units", views.get_ad_units, name="ad_units"),
    path("list_users", views.list_users, name="list_users"),
    path("list_reports", views.list_reports, name="list_reports"),
    path("assign_report", views.assign_report, name="assign_report"),
    path("list_records/<int:report_id>", views.get_records, name="get_records"),
    path("delete_user/<int:user_id>", views.delete_user, name="delete_user"),
    path("delete_report/<int:report_id>",
         views.delete_report, name="delete_report")
]
