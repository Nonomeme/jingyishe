from django.contrib import admin

from .models import User, Question, Answer, Case, Expert,Course

# Register your models here.

admin.site.register(User)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Case)
admin.site.register(Expert)
admin.site.register(Course)
