from django.shortcuts import render, get_object_or_404
from .forms import *
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.mail import send_mail

import yaml, json
import os
from datetime import datetime

from .modules.commands_to_schema import *
from .modules.substitutions import *


def register(request):
    """
    Generate register page

    Path in URL: /register
    """
    form = OrganizationForm()
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            post = form.save()
            # Check if commands field is specified
            if post.commands != '':
                # Convert comments field (string in yaml-format) to
                # json-editor friendly string
                post.commands = convert_dict_array(yaml.safe_load(post.commands))
            post.save()
            # Redirect to the main form page
            return HttpResponseRedirect(f"/{post.id}")
    return render(request, 'register.html', {'form': form})

def send_email(uuid, orgname, addresses):
    """
    Send email to specified addresses

    uuid: string with organization ID
    addresses: list of email addresses
    """
    date_time_now = str(datetime.now())[:-7]
    body = f"The webform https://data.solidex.by/{uuid}/ was \
updated at {date_time_now}."
    send_mail(
        f"{orgname} webform was updated",
        body,
        "webform@solidex.by",
        addresses,
        fail_silently=False)

def home(request, orgid):
    """
    Generate main form page

    Path in URL: /<uuid:orgid>/
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    # Get comments in yamldata string to display them instead of
    # some labels in web-form
    names_formats_orig = yaml_comments(org_object.yamldata)
    substitutions, formats, unique_orig = (names_formats_orig[0],
                                           names_formats_orig[1],
                                           names_formats_orig[2])
    unique_yamldata = names_formats_orig[3]
    yform = yaml.safe_load(unique_yamldata)  # Convert yaml-data to python object
    # Convert python object to string in json format
    json_from_yaml = json.dumps(yform, sort_keys=False)

    if request.method == "POST":
        after_edit = request.POST.get("after_edit")
        substitutions = request.POST.get("substitutions")
        formats = request.POST.get("formats")
        unique_orig = request.POST.get("unique_orig")
        yaml_no_comments = yaml.safe_dump(json.loads(after_edit), sort_keys=False)
        org_object.yamldata = set_comments_back(yaml_no_comments, [json.loads(substitutions),
                                                                   json.loads(formats),
                                                                   json.loads(unique_orig)])
        org_object.save()
        addresses = org_object.email_addresses.split(", ")
        send_email(orgid, org_object.company, addresses)
    return render(request, 'home.html', {'org_object': org_object,
                                         'orgid': orgid,
                                         'json_from_yaml': json_from_yaml,
                                         'substitutions': substitutions,
                                         'formats': formats,
                                         'unique_orig': unique_orig,
                                         })

def success(request, orgid):
    """
    Generate the page to informate customer that the data was sent successfully

    Path in URL: /<uuid:orgid>/success/
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    return render(request, 'success.html', {'org_object': org_object,
                                            'orgid': orgid, 
                                           })

def default(request):
    """
    Generate default page

    Path in URL: /
    """
    return render(request, 'default.html')


def files(request, orgid):
    """
    Generate page with possibility to upload, download and delete files

    Path in URL: /<uuid:orgid>/files/
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    # The page is accessible only if it should be used
    # That's why we check if the customer shouldn't provide any configs
    if org_object.num_conf == 0:
        raise Http404()
    docs = []
    # Get all the customer's files that they has already uploaded
    for doc in DocumentModel.objects.filter(organization__id=orgid):
        docs.append(doc)
    form = DocumentForm(request.POST or None)
    if 'upload_doc' in request.POST:
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.organization = org_object
            post.save()
            return HttpResponseRedirect(f"/{orgid}/files/")
    return render(request, 'files.html', {'org_object': org_object,
                                         'orgid': orgid,
                                         'comment': org_object.comment_conf,
                                         'docs': docs,
                                         'form': form,
                                         'current_uploaded_files': len(docs),
                                         'max_files': org_object.num_conf,
                                        })

def download_file(request, path):
    """
    Send user file if it exists

    Path in URL (also path parameter): /media/<uuid>/filename
        uuid: unique id of the organization
    """
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    # Check if file exists and if it's a file (not a directory)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'rb') as fh:
            # Send file and force browser to download it without displaying
            response = HttpResponse(fh.read(), content_type="application/force-download")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404()

def delete_file(request, orgid, fileid):
    """
    Delete file from server and database

    Path in URL: /<uuid:orgid>/files/<uuid:fileid>/
        orgid: unique id of the organization
        fileid: unique id of the file
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    if request.method == 'POST':
        doc = DocumentModel.objects.get(pk=fileid)
        # Remove the file from the server
        os.remove(os.path.join(settings.MEDIA_ROOT, doc.document.name))
        doc.delete()  # Remove info about the file from the database
    return HttpResponseRedirect(f"/{orgid}/files/")

def commands(request, orgid):
    """
    Generate page with possibility to provide commands output

    Path in URL: /<uuid:orgid>/commands/
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    # The page is accessible only if it should be used
    # That's why we check if "commands" field is empty
    if org_object.commands == '':
        raise Http404()
    # Convert commands field in json-editor friendly schema
    commands_schema = commands_to_schema(json.loads(org_object.commands))
    if request.method == "POST":
        # Get filled data and save it
        filled_output = request.POST.get("filled_output")
        org_object.commands = filled_output
        org_object.save()
    return render(request, 'commands.html', {'org_object': org_object,
                                             'orgid': orgid,
                                             'commands_schema': commands_schema,
                                             })

def feedback(request, orgid):
    """
    Provide user with page to write a feedback

    Path in URL: /<uuid:orgid>/feedback/
        orgid: unique id of the organization
    """

    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    feedback_obj = FeedbackModel.objects.filter(organization__id=orgid)
    if feedback_obj:
        instance = feedback_obj[0]
    else:
        instance = FeedbackModel()
    form = FeedbackForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.organization = org_object
            post.save()
            return HttpResponseRedirect(f"/{orgid}/feedback/thanks")
    return render(request, 'feedback.html', {'org_object': org_object,
                                             'orgid': orgid,
                                             'form': form,
                                            })

def feedback_thanks(request, orgid):
    """
    Generate the page to informate customer that the feedback was sent successfully

    Path in URL: /<uuid:orgid>/feedback/thanks/
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    return render(request, 'feedback_thanks.html', {'org_object': org_object,
                                            'orgid': orgid, 
                                           })

def yaml_response(request, orgid):
    """
    Send yamldata field in plain yaml text

    Path in URL: /<uuid:orgid>/yamldata.yml
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    response = HttpResponse(org_object.yamldata, content_type="text/yaml")
    return response

def commands_response(request, orgid):
    """
    Send commands field in json format

    Path in URL: /<uuid:orgid>/commands.json
        orgid: unique id of the organization
    """
    org_object = get_object_or_404(OrganizationModel, pk=orgid)
    response = HttpResponse(org_object.commands, content_type="application/json")
    return response

