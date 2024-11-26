from django.contrib import admin
from .models import Document, Maimltype, OtherFiles

admin.site.register(Document)
admin.site.register(OtherFiles)
admin.site.register(Maimltype)