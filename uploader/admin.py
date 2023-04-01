from django.contrib import admin
from .models import UploadFile
# Register your models here.


@admin.register(UploadFile)
class UploadFileAdmin(admin.ModelAdmin):
    list_display = (
        'origin_file_name', 'file_name', 'gcs_path', 'upload_time', 'owner',
        'context'
    )
    list_filter = ('upload_time', 'owner')
    search_fields = ('origin_file_name', 'file_name', 'gcs_path', 'owner')
    ordering = ['-upload_time']
