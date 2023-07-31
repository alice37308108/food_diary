from django.contrib import admin
from diary.models import Meal, Diary, Supplement, RegularExpressionWord

admin.site.register(Meal)

admin.site.register(Diary)

admin.site.register(Supplement)

admin.site.register(RegularExpressionWord)