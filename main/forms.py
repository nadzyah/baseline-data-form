from django import forms
from .models import *
import yaml
from yaml.parser import ParserError, ScannerError

class OrganizationForm(forms.ModelForm):
    
    class Meta:
        model = OrganizationModel
        fields = ['company', 'yamldata']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget.attrs['placeholder'] = "Cutomer's Organization"
        self.fields['yamldata'].widget.attrs['placeholder'] = "Insert data from your .yml file with valid syntax."
        self.fields['yamldata'].widget.attrs['validators'] = self.clean_yamldata

        for x in self.fields:
            self.fields[x].widget.attrs['class'] = 'form-control'

    def clean_yamldata(self):
        yamldata = self.cleaned_data['yamldata']
        try:
            yaml.safe_load(yamldata)
        except (ScannerError, ParserError):
            raise forms.ValidationError(
                    ('Parser error',),
                    code='invalid',
                    params={'yamldata': "Parser error. Check yaml syntax."}
                    )

