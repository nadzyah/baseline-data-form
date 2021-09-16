from __future__ import unicode_literals
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

import datetime
import dateparser
from babel.dates import format_date, format_datetime, format_time

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
    email_addresses: CharField
        the string with emails of workers that are focused on the project
    created_at: DateTimeField
        represents date and time when the object was created
    last_updated_at: DateTimeField
        represents date and time when the object was last updated
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
    email_addresses = models.CharField(help_text="emails of project workers", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        date = (self.created_at.day, self.created_at.month, self.created_at.year)
        return self.company + "-" + "%02d-%02d-%d" % date

    def created_at_ru(self):
        date_time_en = dateparser.parse(str(self.created_at))
        date_time_ru = format_datetime(date_time_en, locale='ru_RU')
        return date_time_ru[:-3]

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
        the unique identifier of the file
    organization: ForeignKey
        the OrganizationModel object that is associated with the file
    description: CharField
        the information about the file that customer can provide while
        uploading it
    document: FileField
        the file instance
    uploaded_at: DateTimeField
        represents date and time when the document was uploaded
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(OrganizationModel, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=get_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def org_id(self):
        return self.organization.id

    def __str__(self):
        return str(self.organization) + "_" + self.document.name[37:]

    def delete(self, *args, **kwargs):
        """Delete information about the file from the database"""
        self.document.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Config file"


class FeedbackModel(models.Model):
    """
    A class used to represent feedbacks from customers

    Attributes
    ----------
    id: UUIDField
        the unique identifier of the feedback
    organization: ForeignKey
        the organization which the author of the feedback belongs to
    is_user_friendly: CharField
        answer on the question "Был ли портал удобен в использовании при 
        предоставлении исходных данных?"
    how_to_make_it_better: TextField
        answer on the question "Что бы Вы посоветовали улучшить в функционале портала?"
    submitted_at: DateTimeField
        represents date and time when the feedback was submitted
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(OrganizationModel, on_delete=models.CASCADE)
    is_user_friendly = models.CharField("Был ли портал удобен в использовании при\
            предоставлении исходных данных?", max_length=255, choices=(
                                                            ("Да", "Да"),
                                                            ("Частично", "Частично"),
                                                            ("Нет", "Нет"),
                                                        )
                                       )   

    how_to_make_it_better = models.TextField("Что бы Вы посоветовали улучшить\
                                              в функционале портала?")
    submitted_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        date = (self.submitted_at.day, self.submitted_at.month, self.submitted_at.year)
        return self.organization.company + "-" + "%02d-%02d-%d" % date

    class Meta:
        verbose_name = "Review"

