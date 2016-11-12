from django.db import models

# Create your models here.


class bracketModel(models.Model):
	title = models.CharField(max_length = 200)
	post = 	models.TextField()
	
