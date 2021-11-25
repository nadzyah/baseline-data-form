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
    path("<uuid:orgid>/", views.home, name="home"),

    # URL with info that the data was sent successfully 
    path("<uuid:orgid>/success/", views.success, name="success"),

    # URLs for files
    path("<uuid:orgid>/files/", views.files, name="files"),
    path("<uuid:orgid>/files/<uuid:fileid>/", views.delete_file, name="delete_file"),
    path(r'media/<path:path>', views.download_file, name="download_file"),
    
    # URLs for commands
    path("<uuid:orgid>/commands/", views.commands, name="commands"),
   
    # Feedback
    path("<uuid:orgid>/feedback/", views.feedback, name="feedback"),
    path("<uuid:orgid>/feedback/thanks/", views.feedback_thanks, name="feedback_thanks"),

    # URLs to get fields in plain text
    path("<uuid:orgid>/yamldata.yml", views.yaml_response, name="yaml_response"),
    path("<uuid:orgid>/yamldata.yml/", views.yaml_response, name="yaml_response"),
    
    path("<uuid:orgid>/commands.json", views.commands_response, name="commands_response"),
    path("<uuid:orgid>/commands.json/", views.commands_response, name="commands_response"),
]
