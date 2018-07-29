from django.contrib.auth.models import User
from rest_framework.response import Response as HTTPResponse
from rest_framework import permissions, viewsets, status
from cq.permission import CustomProfilePermission, CustomUserPermission
from rest_framework.decorators import detail_route
from cq.models import Research, Article, Sentence, Question, Take, Response, Milestone, Profile
from cq.serializers import UserSerializer, ResearchSerializer, ArticleSerializer, QuestionSerializer, \
    SentenceSerializer, TakeSerializer, ResponseSerializer, TakeBindMilestoneSerializer, MileStoneSerializer, \
    ProfileSerializer


class ResearchViewSet(viewsets.ModelViewSet):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.data.get('author'),
            title=self.request.data.get('title')
        )


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticated,)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SentenceViewSet(viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TakeBindMilestoneViewSet(viewsets.ModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeBindMilestoneSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @detail_route(methods=['patch'])
    def update_highlight(self, request, pk=None):

        # will receive take_id, sentence_id(Many)
        take = self.get_object()
        # create new milestone
        m_serializer = MileStoneSerializer(data={
            'take': take.id,
        })
        m_serializer.is_valid(raise_exception=True)
        m_serializer.save(user=self.request.user)

        # save highlights(Response)
        sentences = request.data.pop('sentences', [])
        response_form = []
        for sentence_id in sentences:
            response_form.append({
                'take': take.id,
                'milestone': m_serializer.data.get('id'),
                'sentence': sentence_id,
                'found': request.data.get('found'),
            })
        r_serializer = ResponseSerializer(data=response_form, many=True)
        r_serializer.is_valid(raise_exception=True)
        r_serializer.save(user=self.request.user)

        return HTTPResponse(r_serializer.data)


class TakeViewSet(viewsets.ModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )


class ResponseViewSet(viewsets.ModelViewSet):
    queryset = Response.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MileStoneSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (CustomUserPermission,)
    lookup_field = 'username'

    def list(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        else:
            queryset = User.objects.filter(username=self.request.user)
        serializer = UserSerializer(queryset, many=True)
        return HTTPResponse(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (CustomProfilePermission,)

