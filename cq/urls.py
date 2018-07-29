from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token, obtain_jwt_token

from cq import views


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'researches', views.ResearchViewSet)
router.register(r'responses', views.ResponseViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'sentences', views.SentenceViewSet)
router.register(r'takes', views.TakeBindMilestoneViewSet)
router.register(r'milestones', views.MilestoneViewSet)
router.register(r'profiles', views.ProfileViewSet)


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
