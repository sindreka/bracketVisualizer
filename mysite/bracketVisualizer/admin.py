from django.contrib import admin

# Register your models here.
from .models import bracketModel

#class bracketAdmin(admin.ModelAdmin):
#	fieldset = [
#		(None, {'fields': ['title']}),
#		(None, {'fields': ['post']}),		
#	]

admin.site.register(bracketModel)

