from django.shortcuts import render, get_object_or_404
from .forms import *
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView
import yaml
import json
import dynaform


def register(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            post = form.save()
            post.save()
            return HttpResponseRedirect(f"/{post.id}")
    form = OrganizationForm()
    return render(request, 'register.html', {'form': form})

def home(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    yform = yaml.safe_load(org_object.yamldata)
    json_from_yaml = json.dumps(yform)
    return render(request, 'home.html', {'orgname': org_object.company,
                                         'userid': userid,
                                         'json_from_yaml': json_from_yaml,
                                         })

def default(request):
    return render(request, 'default.html')

def success(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    if request.method == "POST":
        after_edit = request.POST.get("after_edit")
        org_object.yamldata = yaml.dump(yaml.safe_load(json.dumps(json.loads(after_edit))), sort_keys=False)
        org_object.save()
    return render(request, 'success.html', {'orgname': org_object.company,
                                            'userid': userid, 
                                           })
def yaml_response(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    yamldata = org_object.yamldata
    return render(request, 'yamldata.yml', {'yamldata': yamldata})

