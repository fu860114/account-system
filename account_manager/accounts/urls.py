from django.urls import path
from .views import LoginView, AccountManagementView, UserView
from .image_to_text import extract_text_from_image

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('accounts/', AccountManagementView.as_view(), name='accounts'),
    path('user/', UserView.as_view()),  # 定義 '/user/' 路徑

    path('extract_text/', extract_text_from_image, name='extract_text_from_image'),
]
