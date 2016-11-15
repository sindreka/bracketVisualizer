#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bracketVisualizer.settings")
from django.core.management.base import BaseCommand

# Import lots of stuff
#import django
#django.setup()
from urllib import request
import re
import simplejson as json



# This function must run periodically.
from bracketVisualizer.models import bracketBatch, bracketMatch


class AppURLopener(request.FancyURLopener):
    version = "User-Agent:MTGcrsdasdasdawler:v0.74asd2 (by /u/harry_THEada_potter)"
 


def getBatchResults(batchNumber):
    batchNumber = str(batchNumber)
    request._urlopener = AppURLopener
    url = "http://reddit.com/r/mtgbracket.json"
    source = request.urlopen(url)
    posts = json.load(source)["data"]["children"]
    #print(posts)
    for post in posts:
        if post['data']['title'] == "Batch " + batchNumber + " results":
            url = "http://reddit.com" + post['data']['permalink']
            break
    else:
        raise Exception("No new batch found")
        return -1
    source = request.urlopen(url + ".json")
    comments = json.load(source)[1]['data']['children']
    #print(comments)
    for comment in comments:
        if comment['data']['body'].count('%') >= 32:
            post = comment['data']['body']
            return post[post.find("*")+2:].split("\n* ")
    raise Exception("Bøøøø")
    return -1

def getInfoFromLine(line):
    info = line.split(" defeats ")
    info = [info[0]] + info[1].split(' with ')
    info[2] = info[2][0:info[2].find('%')]
    info.append(str(round(100-float(info[-1]),1)))
    return info

def getInfoFromPost(text):
    info = []
    #print(text)
    for line in text:
        info.append(getInfoFromLine(line))
    return info
#    return list(map(getInfoFromLine, text))

def getImageFromCardName(card):
    #card = card.replace('Ae','Æ') 
    # Ae won't work since magiccards.info uses æ

    infoSite = "http://magiccards.info/query?q=" + card.replace(' ', '+').replace('ö', 'o') + "&v=card&s=cname"
    page = request.urlopen(infoSite)
    data = page.read()
    expression = '(?<=\<img src=")http://magiccards.info/scans/en/[a-z,0-9]{1,10}/[a-z,0-9]{0,10}.jpg(?="\s*alt="' + card + ')'
    img = re.search(expression, data.decode("utf-8"))
    print(img)
    return img.group(0)

def getResults(text):
    cardTable = getInfoFromPost(text)
    return [
        [[line[0], line[2], getImageFromCardName(line[0])], [line[1], line[3], getImageFromCardName(line[1])]]
        for line in cardTable
    ]


def addToDatabase():
    # Get batchNumber
    try:
        batchNumber= bracketBatch.objects.all().order_by('-id')[0].batchNumber
    except IndexError:
        batchNumber = 0
    print(batchNumber)
    #return
    # Check if new batchResults are avilable
    results = getBatchResults(batchNumber+1) # add error
    print(results)
    resultMatrix = getResults(results) # add error
    print(resultMatrix)
    # Add result key to matchBatch
    B = bracketBatch(batchNumber = batchNumber+1)
    B.save()
    for row in resultMatrix:
        # Add results to matchResult
        match = bracketMatch(batch=B, winnerURL = row[0][2], winnerName = row[0][0], winnerProsent = row[0][1],
                                       loserURL = row[1][2],  loserName = row[1][0],  loserProsent = row[1][1])
        match.save()
        #del match


class Command(BaseCommand):
    def handle(self, **kwargs):    
        addToDatabase()



