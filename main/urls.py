from django.urls import path
from django.conf.urls import url
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.static import serve 

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.default, name="default"),
    path("register/", views.register, name="register"),
    url(r'^favicon\.ico$', RedirectView.as_view(url=staticfiles_storage.url("favicons/favicon.ico"), permanent=True), name='favicon'),
    
    # URL for the main form
    path("<uuid:userid>/", views.home, name="home"),

    # URL with info that the data was sent successfully 
    path("<uuid:userid>/success/", views.success, name="success"),

    # URLs for files
    path("<uuid:userid>/files/", views.files, name="files"),
    path("<uuid:userid>/files/<uuid:fileid>/", views.delete_file, name="delete_file"),
    path(r'media/<path:path>', views.download_file, name="download_file"),
    
    # URLs for commands
    path("<uuid:userid>/commands/", views.commands, name="commands"),
    
    # URLs to get fields in plain text
    path("<uuid:userid>/yamldata.yml", views.yaml_response, name="yaml_response"),
    path("<uuid:userid>/yamldata.yml/", views.yaml_response, name="yaml_response"),
    
    path("<uuid:userid>/commands.json", views.commands_response, name="commands_response"),
    path("<uuid:userid>/commands.json/", views.commands_response, name="commands_response"),
]
