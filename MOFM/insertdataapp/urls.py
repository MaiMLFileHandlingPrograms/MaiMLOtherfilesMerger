from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import ListDL, DocumentUpload, DocumentUpdate

app_name = 'insertdataapp'

urlpatterns = [
    path("upload/", DocumentUpload.modelform_upload, name='maimlfileupload'),  # menu --> maimlfileupload UI
    path("toinsertdata/<slug:upload_maiml_id>/", DocumentUpload.upload_datafiles, name='toinsertdata'),  # maimlfileupload UI --> data file upload UI
    path("selectID/", DocumentUpdate.update_maiml, name='createdata'),  # select insertionID UI -->  update data class
    path("update/", DocumentUpdate.update_maiml, name='updateform'),  # input data UI -->  update data class --> 
    path("fromidupload/<slug:upload_maiml_id>/", DocumentUpload.upload_datafiles, name='fromidupload'),  # list UI --> file upload UI
    path("fromidupload/", DocumentUpload.upload_datafiles, name='fromidupload'),  # list UI --> file upload UI
    path("list/", ListDL.displayList, name='list'), 
    path("download/<slug:upload_maiml_id>/", ListDL.download_zip, name='zipdownload'),  # list UI --> zip download
    path("download/", ListDL.download_zip, name='zipdownload'),  # list UI --> zip download
] #+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)