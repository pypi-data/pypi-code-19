from djangoApiDec.djangoApiDec import queryString_required
from django.http import JsonResponse
from .apps import SearchOb

# Create your views here.
@queryString_required(['keyword', 'school'])
def search(request):
	keyword = request.GET['keyword']
	school = request.GET['school']
	sob = SearchOb(keyword, school)
				
	return JsonResponse(sob.getResult(), safe=False)

@queryString_required(['keyword', 'fullTitle'])
def incWeight(request):
	keyword = request.GET['keyword']
	fullTitle = request.GET['fullTitle']
	sob = SearchOb(keyword)
	sob.incWeight(fullTitle)
	return JsonResponse({"receive Weight success":1}, safe=False)