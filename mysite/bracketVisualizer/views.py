from django.shortcuts import render
from urllib import request
import re
from .models import bracketModel
import io

# Create your views here.




def bracketViews(request):
        brackets = io.StringIO(bracketModel.objects.all()[0].post)

        results = getResults(brackets)

        context = {
                'key': results,
        }
        return render(request,'bracketVisualizer/bracket.html',context = context)
