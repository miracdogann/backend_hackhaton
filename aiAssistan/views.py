from django.http import HttpResponse

def home(request):
    return HttpResponse("Merhaba, burası anasayfa!")
