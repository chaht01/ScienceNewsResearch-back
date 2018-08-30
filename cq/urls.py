from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token, obtain_jwt_token
from rest_framework_extensions.routers import ExtendedSimpleRouter

from cq import views

router = ExtendedSimpleRouter()


users_router = router.register(r'users', views.UserViewSet, base_name='user')
users_router.register(r'profiles', views.ProfileViewSet, base_name='users-profile', parents_query_lookups=['user'])

researches_router = router.register(r'researches', views.ResearchViewSet, base_name='research')
researches_router.register(r'articles', views.ArticleViewSet, base_name='researches-article', parents_query_lookups=['research'])
researches_router.register(r'questions', views.QuestionViewSet, base_name='researches-question', parents_query_lookups=['research'])

articles_router = router.register(r'articles', views.ArticleViewSet, base_name='article')

sentences_router = router.register(r'sentences',views.SentenceViewSet, base_name='sentence')

codefirsts_router = router.register(r'codefirsts',views.CodefirstViewSet, base_name='codefirst')

codeseconds_router = router.register(r'codeseconds',views.CodesecondViewSet, base_name='codesecond')

questions_router = router.register(r'questions', views.QuestionViewSet, base_name='question')
#questions_router.register(r'takes', views.TakeBindMilestoneViewSet, base_name='questions-take', parents_query_lookups=['question'])

reftexts_router = router.register(r'reftexts', views.ReftextViewSet, base_name='reftext')

showns_router = router.register(r'showns',views.ShownViewSet, base_name='shown')

takes_router = router.register(r'takes',views.TakeViewSet, base_name='take')

answertexts_router = router.register(r'answertexts',views.AnswertextViewSet, base_name='answertext')

judgements_router = router.register(r'judgements', views.JudgementViewSet, base_name='judgement')

similaritys_router = router.register(r'similaritys',views.SimilarityViewSet, base_name='similarity')

codesecond_router = router.register(r'codeseconds', views.CodesecondViewSet, base_name='codesecond')

profiles_router = router.register(r'profiles', views.ProfileViewSet, base_name='profile')



# Create schema view of api
schema_view = get_schema_view(title='pastebin api')

urlpatterns = [
    url(r'^schema/$', schema_view),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^', include(router.urls)),
    # auth login / logout
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

