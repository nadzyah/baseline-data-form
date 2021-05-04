from django import forms
from .models import *
import yaml

class OrganizationForm(forms.ModelForm):
    
    class Meta:
        model = OrganizationModel
        fields = ['company', 'yamldata']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].widget.attrs['placeholder'] = 'Solidex'
        self.fields['yamldata'].widget.attrs['placeholder'] = """ bgp:
    as: 65101
    router_id: 178.124.134.121
    neighbor:
      - _ip: ~ 
        remote-as: 6697
        prefix: []

static:
   - _dst: ~
     _gw: ~
        """
        for x in self.fields:
            self.fields[x].widget.attrs['class'] = 'form-control'
