from django.urls import path
from .views import LoginView, AdminCreateUserView, UserView, AdminView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('create-user/', AdminCreateUserView.as_view(),
         name='admin-create-user'),
    path('user/', UserView.as_view(), name='user'),
    path('admin/', AdminView.as_view(), name='admin'),
]
