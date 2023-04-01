from django.contrib import admin
from .models import ChatHistory
# Register your models here.


@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'pdf_file', 'user', 'history_list', 'create_time', 'update_time'
    )
    list_filter = ('create_time', 'user')
    search_fields = ('user', 'question', 'answer')
    ordering = ['-create_time']
