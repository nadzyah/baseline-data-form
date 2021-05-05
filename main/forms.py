from django import forms
from .models import *
import yaml

class OrganizationForm(forms.ModelForm):
    
    class Meta:
        model = OrganizationModel
        fields = ['company', 'yamldata']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget.attrs['placeholder'] = "Cutomer's Organization"
        self.fields['yamldata'].widget.attrs['placeholder'] = "Insert data from your .yml file with valid syntax." 
        for x in self.fields:
            self.fields[x].widget.attrs['class'] = 'form-control'
