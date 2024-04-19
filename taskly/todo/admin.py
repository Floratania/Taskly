from django.contrib import admin

# Register your models here.

from .models import Task, Profile, Activity

admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(Activity)
