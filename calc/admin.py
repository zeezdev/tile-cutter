from django.contrib import admin
from .models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('name', 'ts')
    # fields = ('name', 'data', 'result', 'ip', 'ts')
    readonly_fields = ('ts',)
