import itertools
from functools import reduce
from django.contrib.auth.models import User
from rest_framework import serializers
from cq.models import Article, Research, Question, Profile, Sentence, Codefirst, Codesecond, Reftext, Shown, Take, Answertext, Judgement
from datetime import datetime


class UserSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    reftexts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    showns = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    judgements = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    profile = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class ProfileSerializer(serializers.ModelSerializer):
    research = serializers.SerializerMethodField('research_id')


    def research_id(self, profile):
        if profile.article is not None:
            return profile.article.research.id
        return None

    class Meta:
        model = Profile
        fields = '__all__'


class ResearchSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=1024)
    author = serializers.CharField(max_length=1024)
    link = serializers.CharField(max_length=1024)

    articles = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)

    class Meta:
        model = Research
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=1024)
    publisher = serializers.CharField(max_length=100)
    link = serializers.CharField(max_length=1024)

    sentences = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)
    profiles = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class SentenceSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=1024)
    paragraph_order = serializers.IntegerField()
    order = serializers.IntegerField()
    reftexts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    answertexts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Sentence
        fields = '__all__'


class CodesecondSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=512)
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Codesecond
        fields = '__all__'


class CodefirstSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=512)

    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    code_second = serializers.SerializerMethodField()

    def get_code_second(self, obj):
        return CodesecondSerializer(Codesecond.objects.filter(code_first=obj.id), many=True).data

    class Meta:
        model = Codefirst
        fields = '__all__'


class ReftextSerializer(serializers.ModelSerializer):
    questioner = serializers.ReadOnlyField(source='questioner.username')

    class Meta:
        model= Reftext
        fields='__all__'


class QuestionSerializer(serializers.ModelSerializer):
    article = serializers.PrimaryKeyRelatedField(read_only=True)
    questioner = serializers.ReadOnlyField(source='questioner.username')
    showns = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    reftexts = ReftextSerializer(many=True, read_only=True)
    judgement_firsts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    judgement_seconds = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    code_first = CodefirstSerializer(read_only=True)
    code_second = CodesecondSerializer(read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class QuestionShownSerializer(serializers.ModelSerializer):
    questioner = serializers.ReadOnlyField(source='questioner.username')
    code_first = CodefirstSerializer(read_only=True)
    code_second = CodesecondSerializer(read_only=True)
    article_title = serializers.SerializerMethodField()
    article_publisher = serializers.SerializerMethodField()
    article_sentences = serializers.SerializerMethodField()

    def get_article_sentences(self, obj):
        return string.article.sentences
        

    def get_article_title(self, obj):
        return obj.article.title

    def get_article_publisher(self, obj):
        return obj.article.publisher

    class Meta:
        model = Question
        fields = '__all__'


class JudgeQuestionSerializer(serializers.ModelSerializer):
    questioner = serializers.ReadOnlyField(source='questioner.username')
    judgement_firsts = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    judgement_seconds = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'questioner', 'judgement_firsts', 'judgement_seconds')


class AnswertextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answertext
        fields= '__all__'


class TakeSerializer(serializers.ModelSerializer):
    taken = serializers.BooleanField()
    answertexts = AnswertextSerializer(many=True, read_only=True)

    class Meta:
        model = Take
        fields = '__all__'


class ShownSerializer(serializers.ModelSerializer):
    answerer = serializers.ReadOnlyField(source='answerer.username')
    takes = TakeSerializer(many=True, read_only=True)
    question = QuestionShownSerializer(read_only=True)

    class Meta:
        model = Shown
        fields = '__all__'


class JudgementSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField()
    questioner = serializers.ReadOnlyField(source='questioner.username')
    question_first = JudgeQuestionSerializer(read_only=True)

    class Meta:
        model = Judgement
        fields= '__all__'


# class SimilaritySerializer(serializers.ModelSerializer):
#     similarity = serializers.FloatField()
#     judgements = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#
#     class Meta:
#         model = Similarity
#         fields = '__all__'


""" class ResponseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    text = serializers.SerializerMethodField('text_from_sentence')

    def text_from_sentence(self, response):
        return str(response.sentence)

    class Meta:
        model = Response
        fields = '__all__'

    def update(self, instance, validated_data):
        return instance


class MileStoneSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    responses = ResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'


class TakeBindMilestoneSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    milestones = MileStoneSerializer(many=True, read_only=True)

    class Meta:
        model = Take
        fields = '__all__'

    def create(self, validated_data):
        # Check if exist `Take` related to both same `Article` and `Question`
        related_takes = Take.objects\
            .filter(article=validated_data.get('article'))\
            .filter(question=validated_data.get('question'))

        query_set = list(related_takes)
        milestones = list(map(lambda x: list(x.milestones.filter(copied_from=None).exclude(found=None)), query_set))
        milestones_flatten = list(itertools.chain.from_iterable(milestones))
        latest_milestone = None if len(milestones_flatten) is 0 \
            else reduce(lambda x, y: y if x.response_at < y.response_at else x, milestones_flatten)

        if latest_milestone is not None:
            take = Take.objects.create(user=self.context['request'].user, **validated_data)
            milestone = Milestone.objects.create(
                user=self.context['request'].user,
                take=take,
                found=latest_milestone.found,
                copied_from=latest_milestone)
            for response in latest_milestone.responses.all():
                response.pk = None
                response.milestone = milestone
                response.user = self.context['request'].user
                response.save()
        else:
            take = Take.objects.create(user=self.context['request'].user, **validated_data)
            Milestone.objects.create(user=self.context['request'].user, take=take)

        return take
 """





