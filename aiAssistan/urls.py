from django.urls import path
from .views import *


urlpatterns = [

    path("",home,name="home"),
    path("chat/",Chat.as_view(),name="chat"),
    path("analiz/", analyze_trendyol_product, name="analyze_trendyol_product"),
    path("qna/", answer_question_view, name="answer_question_view"),
]