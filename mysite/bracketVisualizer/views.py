from django.shortcuts import render
from urllib import request
import re

# Create your views here.


def getInfoFromLine(line):
    info = line.split(" defeats ")
    info = [info[0]] + info[1].split(' with ')
    info[2] = info[2][0:info[2].find('%')]
    info.append(str(round(100-float(info[-1]),1)))
    return info

def getInfoFromPost(text):
    info = []
    for line in text:
        info.append(getInfoFromLine(line))
    return info

def getImageFromCardName(card):
    #card = card.replace('Ae','Æ') 
    # Ae won't work since magiccards.info uses æ

    infoSite = "http://magiccards.info/query?q=" + card.replace(' ','+').replace('ö','o') + "&v=card&s=cname"
    page = request.urlopen(infoSite)
    data = page.read()
    expression = '(?<=\<img src=")http://magiccards.info/scans/en/[a-z,0-9]{1,3}/[0-9]{0,3}.jpg(?="\s*alt="' + card + ')'
    img = re.search(expression,data.decode("utf-8"))
    return img.group(0)

def navn(text):
    cardTable = getInfoFromPost(text)
    results = []
    for line in cardTable:
        results.append([[line[0], line[2], getImageFromCardName(line[0])], [line[1], line[3], getImageFromCardName(line[1])]])
    return results
