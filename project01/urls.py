"""
URL configuration for project01 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views. Home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', views.main_page, name='main'),
    path('', views.login, name='login'),
    path('translate/', views.translate_page, name='translate'),

    # 这里必须是 translate/trans/ ,而不能是trans/ 因为是translate页面下的url (js代码)
    path('translate/trans/', views.trans_func, name='trans'),

    path('register/', views.register, name='register'),

    path('ai/', views.ai_page, name='ai'),

    path('ai/Aians/', views.answer, name='Aians'),

    path('main/', views.main_page, name='main'),

    path('music/', views.music_page, name='music'),

    path('music/download/', views.download_music, name='download_music'),

    path('main/s/', views.search, name='search'),

    path('main/hot_top/', views.hot_topic, name='hot_top'),
]
