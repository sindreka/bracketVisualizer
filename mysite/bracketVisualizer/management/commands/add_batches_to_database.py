#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bracketVisualizer.settings")
from django.core.management.base import BaseCommand

# Import lots of stuff
#import django
#django.setup()
from urllib import request
import simplejson as json

# This function must run every two hours.
from bracketVisualizer.models import bracketBatch, bracketMatch


class AppURLopener(request.FancyURLopener):
    version = "User-Agent:bracketVisualizer:v0.3 (by /u/schpere)"
 


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
    print(comments)
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
    expression = '(?<=\<img src=")http://magiccards.info/scans/en/[a-z,0-9]{1,3}/[0-9]{0,3}.jpg(?="\s*alt="' + card + ')'
    img = re.search(expression, data.decode("utf-8"))
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
    except:
        batchNumber = 0
    print(batchNumber)
    #return
    # Check if new batchResults are avilable
    results = getBatchResults(batchNumber+1)
    print(results)
    resultMatrix = getResults(results)

    # Add result key to matchBatch
    B = bracketBatch(batchNumber+1)
    B.save()
    for row in resultmatrix:
        # Add results to matchResult
        match = bracketMatch(batch=B, winnerURL = row[0][1], winnerName = row[0][1], winnerProsent = row[0][1],
                                       loserURL = row[0][1],  loserName = row[1][1],  loserProsent = row[1][1])
        match.save()
        #del match





class Command(BaseCommand):
    def handle(self, **kwargs):    
        addToDatabase()



