from django.contrib import admin
from .models import NewUser,Question,Answer

# Register your models here.

admin.site.register(NewUser)
admin.site.register(Question)
admin.site.register(Answer)
