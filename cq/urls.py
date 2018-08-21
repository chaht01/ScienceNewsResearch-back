from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token, obtain_jwt_token
from rest_framework_extensions.routers import ExtendedSimpleRouter

from cq import views

router = ExtendedSimpleRouter()

articles_router = router.register(r'articles', views.ArticleViewSet, base_name='article')

users_router = router.register(r'users', views.UserViewSet, base_name='user')
users_router.register(r'profiles', views.ProfileViewSet, base_name='users-profile', parents_query_lookups=['user'])
#users_router.register(r'takes', views.TakeBindMilestoneViewSet, base_name='users-take', parents_query_lookups=['user'])

researches_router = router.register(r'researches', views.ResearchViewSet, base_name='research')
researches_router.register(r'questions', views.QuestionViewSet, base_name='researches-question', parents_query_lookups=['research'])
researches_router.register(r'articles', views.ArticleViewSet, base_name='researches-article', parents_query_lookups=['research'])

#responses_router = router.register(r'responses', views.ResponseViewSet, base_name='response')

questions_router = router.register(r'questions', views.QuestionViewSet, base_name='question')
#questions_router.register(r'takes', views.TakeBindMilestoneViewSet, base_name='questions-take', parents_query_lookups=['question'])

sentences_router = router.register(r'sentences', views.SentenceViewSet, base_name='sentence')

#takes_router = router.register(r'takes', views.TakeBindMilestoneViewSet, base_name='take')
#takes_router.register(r'milestones', views.MilestoneViewSet, base_name='takes-milestone', parents_query_lookups=['take'])\
#    .register(r'responses', views.ResponseViewSet, base_name='takes-milestones-response', parents_query_lookups=['milestone__take', 'milestone'])

#milestones_router = router.register(r'milestones', views.MilestoneViewSet, base_name='milestone')
#milestones_router.register(r'responses', views.ResponseViewSet, base_name='milestones-response', parents_query_lookups=['milestone'])

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

# urlpatterns = format_suffix_patterns(urlpatterns)
