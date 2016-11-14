from django.shortcuts import render
from urllib import request
import re
from .models import bracketMatch, bracketBatch
import io

# Create your views here.




def bracketViews(request):
        brackets = bracketBatch.objects.all()

        #results = getResults(brackets)

        context = {
                'key': brackets,
        }
        return render(request,'bracketVisualizer/bracket.html',context = context)
