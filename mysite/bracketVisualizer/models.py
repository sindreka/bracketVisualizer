from django.db import models
import json
from urllib import request 

# Create your models here.

class bracketModel(models.Model):
	title = models.CharField(max_length = 200)
	post = 	models.TextField()
	

class AppURLopener(request.FancyURLopener):
    version = "User-Agent:bracketVisualizer:v0.2 (by /u/schpere)"
 

def getResults(batchNumber):
    batchNumber = str(batchNumber)
    request._urlopener = AppURLopener
    url = "http://reddit.com/r/mtgbracket.json"
    source = urllib.urlopen(url)
    posts = json.load(source)["data"]["children"]
    for post in posts:
        if post['data']['title'] == "Batch " + batchNumber + " results":
            url = "http://reddit.com" + post['data']['permalink']
            break
    source = urllib.urlopen(url + ".json")
    comments = json.load(source)[1]['data']['children']
    for comment in comments:
        if comment['data']['body'].count('%') >= 32:
            post = comment['data']['body']
            return post[post.find("*")+2:].split("\n* ")
