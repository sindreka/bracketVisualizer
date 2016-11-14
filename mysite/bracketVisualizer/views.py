from django.shortcuts import render
from urllib import request
import re
from .models import bracketMatch, bracketBatch
import io

# Create your views here.


def batchViews(request, bracketBatch_batchNumber):
    matches = bracketMatch.objects.filter(batch__batchNumber=bracketBatch_batchNumber)
    context = {
        'key': matches,
    }
    return render(request,'bracketVisualizer/batch.html', context = context)

def bracketViews(request):
    brackets = bracketBatch.objects.all()

    context = {
        'key': brackets,
    }
    return render(request,'bracketVisualizer/bracket.html', context = context)
