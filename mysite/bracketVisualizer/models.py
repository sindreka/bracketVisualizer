from django.db import models

# Create your models here.

def getInfoFromLine(line):
    info = line.split(" defeats ")
    info = [info[0]] + info[1].split(' with ')
    info[2] = info[2][0:info[2].find('%')]
    return info

def getInfoFromPost(text):
    info = []
    for line in text:
        info.append(getInfoFromLine(line))
    return info

