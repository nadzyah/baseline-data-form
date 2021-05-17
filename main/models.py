from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class OrganizationModel(models.Model):
    """
    The main class for Organizations
    """
    company = models.CharField(help_text='Company name', max_length=200)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    yamldata = models.TextField(help_text='Data from .yml file')

    # Number of config files
    num_conf = models.IntegerField(help_text='Number of required config files',
                       validators=[MinValueValidator(0, message="Minimum number\
                                                        of required config files is 0"), 
                                   MaxValueValidator(10, message="Maximum number\
                                                        of required config files is 10")], 
                       default=0)
    
    # Comment that the customer will use to understand what to upload
    comment_conf = models.CharField(help_text='Comment for configs', max_length=500, blank=True)
    commands = models.TextField(help_text='Commands for commands', blank=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name = "Organization"

def get_upload_path(instance, filename):
    return '{0}/{1}'.format(instance.organization.id, filename)

class DocumentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(OrganizationModel, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def org_id(self):
        return self.organization.id
    
    document = models.FileField(upload_to=get_upload_path)

    def __str__(self):
        return self.document.name

    def delete(self, *args, **kwargs):
        self.document.delete()
        super().delete(*args, **kwargs)

"""
class LogModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(OrganizationModel, on_delete=models.CASCADE)
    command = models.CharField(max_length=100)
    output = models.TextField()

    def __str__(self):
        return selt.command

    @property
    def org_id(self):
        return self.organization.id
"""
