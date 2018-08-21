from django.contrib import admin
from django.conf.urls import include, url
from .models import Article, Research, Question, Profile, Sentence, Codefirst, Codesecond, Reftext, Shown, Take, Answertext, Judgement, Similarity 

admin.site.register(Article)
admin.site.register(Research)
admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Sentence)
admin.site.register(Codefirst)
admin.site.register(Codesecond)
admin.site.register(Reftext)
admin.site.register(Shown)
admin.site.register(Take)
admin.site.register(Answertext)
admin.site.register(Judgement)
admin.site.register(Similarity)
