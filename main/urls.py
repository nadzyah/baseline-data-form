from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.default, name="default"),
    path("register/", views.register, name="register"),
    path("<uuid:userid>/", views.home, name="home"),
    path("<uuid:userid>/success/", views.success, name="success"),
    path("<uuid:userid>/yamldata/", views.yaml_response, name="yaml_response"),
]
