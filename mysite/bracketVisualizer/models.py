from django.db import models
import json
from urllib import request 

# Create your models here.



class bracketBatch(models.Model):
    batchNumber = models.IntegerField();
    def __str__(self):
        return "BatchNumber " + str(self.batchNumber)



class bracketMatch(models.Model):
    batch = models.ForeignKey(bracketBatch)

    winnerURL = models.CharField(max_length = 200)
    winnerName = models.CharField(max_length = 200)
    winnerProsent = models.DecimalField(decimal_places = 1,max_digits = 3)

    loserURL = models.CharField(max_length = 200)
    loserName = models.CharField(max_length = 200)
    loserProsent = models.DecimalField(decimal_places = 1,max_digits = 3)
    def __str__(self):
        return self.winnerName + " vs " + self.loserName


    
