from django.shortcuts import render
from django.http import Http404

class Custom404Middleware:
    def __init__(self,get_respone):
        self.get_respone = get_respone
        
    def __call__(self,request):
        respone = self.get_respone(request)
        if respone.status_code == 404:
            return render(request,'404.html',status = 404)
        return respone