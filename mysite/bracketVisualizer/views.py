from django.shortcuts import render

# Create your views here.
from .models import bracketModel

def bracketViews(request):
	brackets =bracketModel.objects.all()[0]

	# run harald function A = ...

	A = [[['b','c','d'],['b','c','d'],['b','c','d'],['b','c','d'],['b','c','d'],['b','c','d']],[['b','c','d'],['b','c','d'],['b','c','d'],['b','c','d'],['b','c','d'],['b','c','d']]]
	context = {
		'key': A,
	}
	return render(request,'bracketVisualizer/bracket.html',context = context)
