import itertools
import random
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

    @staticmethod
    def create_reftexts(user, question, sentence_ids):
        Reftext.objects.filter(question=question).delete()
        r_ids = []
        for s_id in sentence_ids:
            instance = Reftext.objects.create(questioner=user, question=question,
                                              sentence=Sentence.objects.get(id=s_id))
            r_ids.append(instance.id)
        results = Reftext.objects.filter(id__in=r_ids)
        r_serializer = ReftextSerializer(results, many=True)
        return r_serializer

    def perform_create(self, serializer):
        code_first_id = self.request.data.get('code_first')
        code_second_id = self.request.data.get('code_second')
        code_first = Codefirst.objects.get(id=code_first_id)
        try:
            code_second = Codesecond.objects.get(id=code_second_id)
        except Codesecond.DoesNotExist:
            code_second = None
        serializer.save(questioner=self.request.user, article=self.request.user.profile.article, code_first=code_first, code_second=code_second)


    @detail_route(methods=['patch'])
    def update_reftexts(self, request, pk=None):
        serializer = QuestionViewSet.create_reftexts(self.request.user, self.get_object(), self.request.data.pop('sentence_ids'));
        return HTTPResponse(serializer.data[:])

    @detail_route(methods=['patch', 'put'])
    def delete(self, request, pk=None):
        removed_step = request.data.get('removed_step')
        question = self.get_object()
        serializer = self.get_serializer(question, data={'removed_step': removed_step, 'removed_at': datetime.now()}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

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
    pagination_class = None
    queryset = Reftext.objects.all()
    serializer_class = ReftextSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(questioner=self.request.user)


class ShownViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    pagination_class = None
    queryset = Shown.objects.all()
    serializer_class = ShownSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(answerer=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return HTTPResponse(serializer.data)

    def create(self, request, *args, **kwargs):
        showns = Shown.objects.filter(answerer=self.request.user)
        questions_candidates = Question.objects.exclude(showns__in=showns)
        questions_mine_step12 = questions_candidates.filter(questioner=self.request.user).filter(created_step__lt=3).filter(copied_to=None)
        questions_others = questions_candidates.exclude(questioner=self.request.user).filter(copied_to=None)
        questions = questions_mine_step12.union(questions_others)
        threshold = 5
        candidates_ids = []
        if len(questions) < threshold:
            samples = questions
        else:
            samples = random.sample(list(questions), threshold) # Should be redefined
        for question in samples:
            instance = Shown.objects.create(answerer=self.request.user, question=question)
            candidates_ids.append(instance.id)
        results = Shown.objects.filter(id__in=candidates_ids)
        s_serializer = ShownSerializer(results, many=True)
        return HTTPResponse(s_serializer.data[:])

    @detail_route(methods=['patch'])
    def update_answertext(self, request, pk=None):
        shown = self.get_object()
        sentences = request.data.pop('sentence_ids', [])

        # create new milestone
        t_serializer = TakeSerializer(data={'shown': shown.id, 'taken': True})
        t_serializer.is_valid(raise_exception=True)
        take = t_serializer.save()

        # save highlights(Response)
        answertexts_form = []
        for sentence_id in sentences:
            answertexts_form.append({
                'take': take.id,
                'sentence': sentence_id,
            })
        r_serializer = AnswertextSerializer(data=answertexts_form, many=True)
        r_serializer.is_valid(raise_exception=True)
        r_serializer.save()

        serializer = TakeSerializer(take, data={'taken': True, 'answertexts': r_serializer})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HTTPResponse(serializer.data)


class TakeViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    pagination_class = None
    queryset = Take.objects.all()
    serializer_class = TakeSerializer
    permission_classes = (permissions.IsAuthenticated,)


class AnswertextViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    pagination_class = None
    queryset = Answertext.objects.all()
    serializer_class = AnswertextSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(answerer=self.request.user)


# Not sure whether we need this
class JudgementViewSet(NestedViewSetMixin,viewsets.ModelViewSet):
    pagination_class = None
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
    pagination_class = None
    # Note that similarity only exist for question pairs s.t. question_first_id<question_second_id
    queryset = Similarity.objects.all()
    serializer_class = SimilaritySerializer
    permission_classes = (permissions.IsAuthenticated,)


class UserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (CustomUserPermission,)
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        research_id = request.data.get('research', None)
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

