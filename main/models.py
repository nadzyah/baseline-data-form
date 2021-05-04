from django.db import models
from django.contrib.auth.models import User
import uuid

class OrganizationModel(models.Model):
    """
    The main class for Organizations
    """
    company = models.CharField('Company name', max_length=200)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    yamldata = models.TextField()

    def __str__(self):
        return self.company

    class Meta:
        verbose_name = "Organization"

