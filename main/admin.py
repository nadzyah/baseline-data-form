from django.contrib import admin
from .models import *

class OrganizationAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'created_at', 'last_updated_at')

class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('uploaded_at',)

class FeedbackAdmin(admin.ModelAdmin):
    readonly_fields = ('submitted_at',)

admin.site.register(OrganizationModel, OrganizationAdmin) 
admin.site.register(DocumentModel, DocumentAdmin)
admin.site.register(FeedbackModel, FeedbackAdmin)
