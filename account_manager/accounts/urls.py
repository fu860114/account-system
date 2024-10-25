from django.urls import path
from .views import LoginView, AccountManagementView, UserView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('accounts/', AccountManagementView.as_view(), name='accounts'),
    path('user/', UserView.as_view()),  # 定義 '/user/' 路徑
]
