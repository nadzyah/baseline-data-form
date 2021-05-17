from django import forms
from .models import *
import yaml
from yaml.parser import ParserError, ScannerError
from .modules.logs_to_schema import *

class OrganizationForm(forms.ModelForm):
    
    class Meta:
        model = OrganizationModel
        fields = ['company', 'yamldata', 'num_conf', 'comment_conf', 'commands']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget.attrs['placeholder'] = "Solidex"
        self.fields['yamldata'].widget.attrs['placeholder'] = """Insert data from your .yml file with valid syntax. See the example bellow:
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
        self.fields['comment_conf'].widget.attrs['placeholder'] = 'Example: Загрузите конфигурационные файлы всех устройств FortiGate'
        self.fields['commands'].widget.attrs['placeholder'] = """Provide required log commands for each device in yaml syntax. See the example bellow:
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
        yamldata = self.cleaned_data['yamldata']
        try:
            yaml.safe_load(yamldata)
        except (ScannerError, ParserError):
            raise forms.ValidationError('Parser error. Check yaml syntax in "yamldata" field',
                                        code='invalid')
        return yamldata

    def clean_commands(self):
        commands = self.cleaned_data['commands']
        if commands != '':
            try:
                data = yaml.safe_load(commands)
            except (ScannerError, ParserError):
                raise forms.ValidationError('Parser error. Check yaml syntax in "commands" field',
                                            code='invalid')
            try:
                convert_dict_array(data)
                print(data)
            except (TypeError, AttributeError):
                raise forms.ValidationError("Error. Specify commands in correct format",
                                            code='invalid')
        return commands


class DocumentForm(forms.ModelForm):

    class Meta:
        model = DocumentModel
        fields = ['document', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['placeholder'] = 'Например: FortiGate config'
