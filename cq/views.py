import itertools
from functools import reduce

from django.http import JsonResponse
from django.utils.timezone import now
from datetime import datetime 

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response as HTTPResponse
from rest_framework import permissions, viewsets, status
from cq.permission import CustomProfilePermission, CustomUserPermission
from rest_framework.decorators import detail_route, list_route
from rest_framework_extensions.mixins import NestedViewSetMixin

from cq.models import Article, Research, Question, Profile, Sentence, Codefirst, Codesecond, Reftext, Shown, Take, Answertext, Judgement, Similarity
from cq.serializers import UserSerializer, ProfileSerializer, ResearchSerializer, ArticleSerializer, QuestionSerializer, \
    SentenceSerializer, CodefirstSerializer, CodesecondSerializer, ShownSerializer, TakeSerializer,AnswertextSerializer, \
    ReftextSerializer, JudgementSerializer, SimilaritySerializer
    


class ResearchViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Research.objects.all()
    serializer_class = ResearchSerializer
    permission_classes = (permissions.IsAuthenticated,)

class ArticleViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticated,)

class SentenceViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAuthenticated,)

class CodefirstViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Codefirst.objects.all()
    serializer_class = CodefirstSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CodesecondViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Codesecond.objects.all()
    serializer_class = CodesecondSerializer
    permission_classes = (permissions.IsAuthenticated,)

    """docstring for CodeSecondView"""
    def get_queryset(self):
        queryset = Codesecond.objects.all()
        first_code = self.request.query_params.get('first_code', None)
        if first_code is not None:
            queryset = queryset.filter(first_code=first_code)
        return queryset


class QuestionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(questioner=self.request.user, created_at=datetime.now())    


    @detail_route(methods=['put'])
    def delete(self, request,pk=None):
        removed_step=request.data.get('removed_step')
        question=self.get_object()
        serializer=self.get_serializer(question, data={'removed_step':removed_step, 'removed_at':datetime.now()}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return HTTPResponse(serializer.data)

    def get_queryset(self):
        queryset = Question.objects.all()
        created_step = self.request.query_params.get('created_step', None)
        if created_step is not None:
            queryset = queryset.filter(created_step=created_step)
        return queryset
    

    # Show samples at Phase 1 - Step 2 
    # Now just show questions with pk up to 20
    @detail_route(methods=['get'])
    def show_samples(self, request):
        allquestions=Question.objects.all()
        maxnum=Max(20, allquestions.count())
        samples=Question.objects.all().order_by('id')[:maxnum]
        return samples

    # get others' question at Step 4
    @detail_route(methods=['get'])
    def get_othersquestion(self, request):
        question = self.get_object()
        othersquestions=Question.objects\
            .filter(article=question.article)\
            .filter(created_step=4)\
            .exclude(user=self.request.user)
        return othersquestions
        

class ReftextViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    queryset = Reftext.objects.all()
    serializer_class = ReftextSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        serializer.save(questioner=self.request.user)    


class ShownViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    queryset = Shown.objects.all()
    serializer_class = ShownSerializer
    permission_classes = (permissions.IsAuthenticated,)

class TakeViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeSerializer
    permission_classes = (permissions.IsAuthenticated,)

class AnswertextViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    queryset = Answertext.objects.all()
    serializer_class = AnswertextSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        serializer.save(answerer=self.request.user)    

# Not sure whether we need this
class JudgementViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    queryset = Judgement.objects.all()
    serializer_class = JudgementSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def perform_create(self, serializer):
        # get question_first_id, question_second_id, score 
        # get similarity for that 
        question_first=self.request.data.get('question_first')
        question_second=self.request.data.get('question_second')
        if (question_first<question_second):
            question_smaller=question_first
            question_larger=question_second
        else:
            question_smaller=question_second
            question_larger=question_second 
        
        first_question=Question.objects.filter(id=question_smaller)[0]
        second_question=Question.objects.filter(id=question_larger)[0]

        related_similarity=Similarity.objects.filter(question_first=first_question, question_second=second_question)
        if not related_similarity:
            s_serializer=SimilaritySerializer(data={"question_first":question_smaller, "question_second":question_larger,"similarity":0})
            s_serializer.is_valid(raise_exception=True)
            this_similarity=s_serializer.save()
        else:
            this_similarity=related_similarity[0]
        print(this_similarity)
        serializer.save(questioner=self.request.user, similarity=this_similarity)    


# Not sure whether we need this
class SimilarityViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    # Note that similarity only exist for question pairs s.t. question_first_id<question_second_id
    queryset = Similarity.objects.all()
    serializer_class = SimilaritySerializer
    permission_classes = (permissions.IsAuthenticated,)

##
##class TakeBindMilestoneViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
##    pagination_class = None
##    queryset = Take.objects.all()
##    serializer_class = TakeBindMilestoneSerializer
##    permission_classes = (permissions.IsAuthenticated,)
##
##    def perform_update(self, serializer):
##        is_removed = self.request.data.get('remove')
##        if is_removed:
##            serializer.save(removed_at=now())
##        else:
##            serializer.save()
##
##    @detail_route(methods=['patch'])
##    def renew_milestone(self, request, pk=None):
##
##        # will receive take_id, sentence_id(Many)
##        take = self.get_object()
##        sentences = request.data.pop('sentences', [])
##
##        # create new milestone
##        request.data.update(take=take.id)
##        m_serializer = MileStoneSerializer(data=request.data)
##        m_serializer.is_valid(raise_exception=True)
##        milestone = m_serializer.save(user=self.request.user)
##
##        # save highlights(Response)
##        response_form = []
##        for sentence_id in sentences:
##            response_form.append({
##                'take': take.id,
##                'milestone': m_serializer.data.get('id'),
##                'sentence': sentence_id,
##            })
##        r_serializer = ResponseSerializer(data=response_form, many=True)
##        r_serializer.is_valid(raise_exception=True)
##        r_serializer.save(user=self.request.user)
##
##        serializer = MileStoneSerializer(milestone, data={'take': take.id, 'responses': r_serializer})
##        serializer.is_valid(raise_exception=True)
##        serializer.save()
##
##        return HTTPResponse(serializer.data)
##
##    @detail_route(methods=['get'])
##    def suggestions(self, request, pk=None):
##        take = self.get_object()
##        related_takes = Take.objects\
##            .exclude(article=take.article)\
##            .filter(question=take.question)
##        query_set = list(related_takes)
##        milestones = list(map(lambda x: list(x.milestones.filter(copied_from=None).exclude(found=None).exclude(responses=None)), query_set))
##        milestones_flatten = list(itertools.chain.from_iterable(milestones))
##        latest_milestone = None if len(milestones_flatten) is 0 \
##            else reduce(lambda x, y: y if x.response_at < y.response_at else x, milestones_flatten)
##        if latest_milestone is None:
##            responses = Response.objects.none()
##        else:
##            responses = latest_milestone.responses
##        return HTTPResponse(ResponseSerializer(responses, many=True).data)
##

class TakeViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
        )

##
##class ResponseViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
##    queryset = Response.objects.all()
##    serializer_class = ResponseSerializer
##    permission_classes = (permissions.IsAuthenticated,)
##
##    def perform_create(self, serializer):
##        serializer.save(
##            user=self.request.user,
##        )
##
##
##class MilestoneViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
##    queryset = Milestone.objects.all()
##    serializer_class = MileStoneSerializer
##    permission_classes = (permissions.IsAuthenticated,)


class UserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (CustomUserPermission,)
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        research_id = request.data.pop('research', None)
        research = Research.objects.filter(pk=research_id)
        if not research.exists():
            return JsonResponse({'non_field_errors': ['Select any research type.']}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        profile = instance.profile
        if research_id is not None:
            articles = Article.objects.filter(research=research)
            target_article = reduce(lambda x, y: y if x.profiles.count() > y.profiles.count() else x, articles)
            p_serializer = ProfileSerializer(profile, data={
                'article': target_article.id,
                'user': instance.id
            })
            p_serializer.is_valid(raise_exception=True)
            p_serializer.save()

        return HTTPResponse(serializer.data)

    def list(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            queryset = User.objects.all()
        else:
            queryset = User.objects.filter(username=self.request.user)
        serializer = UserSerializer(queryset, many=True)
        return HTTPResponse(serializer.data)


class ProfileViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (CustomProfilePermission,)

