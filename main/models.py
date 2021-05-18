from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class OrganizationModel(models.Model):
    """
    A class used to represent an Organization
   
    Attributes
    ----------
    company: CharField
        the name of the organization
    id: UUIDField
        the unique identifier of the organization
    yamldata: TextField
        the information if yaml format about baseline data
    num_conf: IntegerField
        number of configuration files
    comment_conf: CharField
        comment that the customer will be able to use to understand 
        what files they should to upload
    commands: TextField
        set of commands for each device (you provide it in yaml format,
        then it's converted and stored in json format)
    """

    company = models.CharField(help_text='Company name', max_length=200)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    yamldata = models.TextField(help_text='Data from .yml file')
    num_conf = models.IntegerField(help_text='Number of requested config files',
                       validators=[MinValueValidator(0, message="Minimal number of files\
                                                        that may be requested is 0"), 
                                   MaxValueValidator(10, message="Maximal number of files\
                                                        that may be requested is 10")], 
                       default=0)
    comment_conf = models.CharField(help_text='Comment for configs',
                                    max_length=500,
                                    blank=True)
    commands = models.TextField(blank=True)

    def __str__(self):
        return self.company

    class Meta:
        verbose_name = "Organization"

def get_upload_path(instance, filename):
    """Generate path where the config files will be stored"""
    return '{0}/{1}'.format(instance.organization.id, filename)

class DocumentModel(models.Model):
    """
    A class used to represent a Configuration File
   
    Attributes
    ----------
    id: UUIDField
        the unique identifier of the organization
    organization: ForeignKey
        the OrganizationModel object that is associated with the file
    description: CharField
        the information about the file that customer can provide while
        uploading it
    document: FileField
        the file instance
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(OrganizationModel, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=get_upload_path)

    @property
    def org_id(self):
        return self.organization.id
    
    def __str__(self):
        return self.document.name

    def delete(self, *args, **kwargs):
        """Delete information about the file from the database"""
        self.document.delete()
        super().delete(*args, **kwargs)
