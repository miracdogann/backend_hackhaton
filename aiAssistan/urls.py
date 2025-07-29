from django.urls import path
from .views import *
from .views import analyze_trendyol_product, answer_question_view
urlpatterns = [

    path("",home,name="home"),
    path("analyze/", analyze_trendyol_product, name="analyze_trendyol_product"),
    path("qna/", answer_question_view, name="answer_question_view"),
   
    

]