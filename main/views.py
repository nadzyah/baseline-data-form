from django.shortcuts import render, get_object_or_404
from .forms import *
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.edit import FormView
from django.conf import settings
import yaml, json
import os
from .modules.logs_to_schema import *
from .modules.substitutions import *

# http://<server's_IP>/register
def register(request):
    """ View for register page
    """
    form = OrganizationForm()
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            post = form.save()
            if post.commands != '':
                post.commands = convert_dict_array(yaml.safe_load(post.commands))
            post.save()
            return HttpResponseRedirect(f"/{post.id}")
    return render(request, 'register.html', {'form': form})

# /<uuid:userid>/
def home(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    replaced_yaml = org_object.yamldata
    yform = yaml.safe_load(replaced_yaml)
    json_from_yaml = json.dumps(yform, sort_keys=False)
    substitutions = yaml_comments(org_object.yamldata)
    return render(request, 'home.html', {'org_object': org_object,
                                         'userid': userid,
                                         'json_from_yaml': json_from_yaml,
                                         'substitutions': substitutions,
                                         })

# /<uuid:userid>/success/
def success(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    if request.method == "POST":
        after_edit = request.POST.get("after_edit")
        substitutions = request.POST.get("substitutions")
        without_comments = yaml.dump(yaml.safe_load(json.dumps(json.loads(after_edit), ensure_ascii=False)), sort_keys=False)
        org_object.yamldata = set_comments_back(without_comments, json.loads(substitutions))
        org_object.save()
    return render(request, 'success.html', {'org_object': org_object,
                                            'userid': userid, 
                                           })

# http://<server's_IP/
def default(request):
    return render(request, 'default.html')


# /<uuid:userid>/files/
def files(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    if org_object.num_conf == 0:
        raise Http404()
    docs = []
    for doc in DocumentModel.objects.filter(organization__id=userid):
        docs.append(doc)
    form = DocumentForm(request.POST or None)
    if 'upload_doc' in request.POST:
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.organization = org_object 
            post.save()
            return HttpResponseRedirect(f"/{userid}/files/")
    return render(request, 'files.html', {'org_object': org_object,
                                         'userid': userid,
                                         'comment': org_object.comment_conf,
                                         'docs': docs,
                                         'form': form,
                                         'current_uploaded_files': len(docs),
                                         'max_files': org_object.num_conf,
                                        })
# /media/<uuid>/filename
def download_file(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404()

# /<uuid:userid>/files/<uuid:fileid>/
def delete_file(request, userid, fileid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    if request.method == 'POST':
        doc = DocumentModel.objects.get(pk=fileid)
        os.remove(os.path.join(settings.MEDIA_ROOT, doc.document.name))
        doc.delete()
    return HttpResponseRedirect(f"/{userid}/files/")

# /<uuid:userid>/commands/
def commands(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    if org_object.commands == '':
        raise Http404()
    commands_schema = commands_to_schema(json.loads(org_object.commands))
    if request.method == "POST":
        filled_output = request.POST.get("filled_output")
        org_object.commands = filled_output
        org_object.save()
    return render(request, 'commands.html', {'org_object': org_object,
                                             'userid': userid,
                                             'commands_schema': commands_schema,
                                             })

# /<uuid:userid>/yamldata.yml
def yaml_response(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    response = HttpResponse(org_object.yamldata, content_type="text/yaml")
    return response

# /<uuid:userid>/commands.json
def commands_response(request, userid):
    org_object = get_object_or_404(OrganizationModel, pk=userid)
    response = HttpResponse(org_object.commands, content_type="application/json")
    return response
