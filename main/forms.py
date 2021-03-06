from django import forms
from .models import *
import yaml
from yaml.parser import ParserError, ScannerError
from .modules.commands_to_schema import *
import re

class OrganizationForm(forms.ModelForm):
    """A class used to generate form object from OrganizationModel object"""

    class Meta:
        model = OrganizationModel
        fields = ['company', 'yamldata', 'email_addresses',
                  'num_conf', 'comment_conf', 'commands']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget.attrs['placeholder'] = "Solidex"
        self.fields['yamldata'].widget.attrs['placeholder'] = """Insert the data from your .yml file with valid syntax:
FG-100F:
  interfaces:
  - ip_mask: 0.0.0.0/0
    gw: 0.0.0.0
FM:
  interfaces:
  - ip_mask: 172.22.10.1/31
    gateway: 172.22.10.0
global:
  syslog: 0.0.0.0
  ntp: 0.0.0.0
  dns1: 0.0.0.0
        """
        self.fields['email_addresses'].widget.attrs['placeholder'] = "worker1@solidex.by, worker2@solidex.by"
        self.fields['comment_conf'].widget.attrs['placeholder'] = 'Example: Загрузите конфигурационные файлы всех устройств FortiGate'
        self.fields['commands'].widget.attrs['placeholder'] = """Provide required commands for each device in yaml syntax:
FG-100F:
  - show system interface
FM:
  - diag dvm device list
  - diag dvm adom list
        """
        not_required_fields = ['comment_conf', 'num_conf']
        for field in not_required_fields:
            self.fields[field].widget.attrs['required'] = False

        for x in self.fields:
            self.fields[x].widget.attrs['class'] = 'form-control'

    def clean_yamldata(self):
        """Validate that yamldata field is filled correctly"""
        yamldata = self.cleaned_data['yamldata']
        try:
            yaml.safe_load(yamldata)
        except (ScannerError, ParserError):
            raise forms.ValidationError('Parser error. Check yaml syntax\
                                        in "yamldata" field',
                                        code='invalid')
        return yamldata

    def clean_commands(self):
        """Validate that commands are provided correctly"""
        commands = self.cleaned_data['commands']
        if commands != '':
            try:
                data = yaml.safe_load(commands)
            # Check yaml syntax
            except (ScannerError, ParserError):
                raise forms.ValidationError('Parser error. Check yaml syntax\
                                            in "commands" field',
                                            code='invalid')
            try:
                convert_dict_array(data)
            # Check correctness of format
            except (TypeError, AttributeError):
                raise forms.ValidationError("Error. Specify commands in correct format",
                                            code='invalid')
        return commands

    def clean_email_addresses(self):
        """Validate that email addresses are provided in correct format"""
        addresses = self.cleaned_data['email_addresses']
        addr_list = addresses.split(", ")
        email_regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        if not all(re.search(email_regex, addr) for addr in addr_list):
            raise forms.ValidationError('Wrong email format', code='invalid')
        return addresses


class DocumentForm(forms.ModelForm):
    """A class used to generate form object from DocumentModel object"""

    class Meta:
        model = DocumentModel
        fields = ['document', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Например: FortiGate config'

class FeedbackForm(forms.ModelForm):
    """A class used to represent feedback form"""

    class Meta:
        model = FeedbackModel
        fields = ['is_user_friendly', 'how_to_make_it_better']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for x in self.fields:
            self.fields[x].widget.attrs['class'] = 'form-control'

