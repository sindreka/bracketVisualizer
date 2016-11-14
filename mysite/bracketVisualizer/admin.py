from django.contrib import admin

# Register your models here.
from .models import bracketBatch, bracketMatch

#class bracketAdmin(admin.ModelAdmin):
#	fieldset = [
#		(None, {'fields': ['title']}),
#		(None, {'fields': ['post']}),		
#	]

admin.site.register(bracketBatch)
admin.site.register(bracketMatch)

