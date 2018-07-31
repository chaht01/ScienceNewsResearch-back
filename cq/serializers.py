import itertools
from functools import reduce
from django.contrib.auth.models import User
from rest_framework import serializers
from cq.models import Research, Article, Sentence, Question, Take, Response, Milestone, Profile


class UserSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    takes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    responses = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    milestones = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    profile = serializers.PrimaryKeyRelatedField( read_only=True)

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
        return profile.article.research.id

    class Meta:
        model = Profile
        fields = '__all__'


class ResearchSerializer(serializers.ModelSerializer):
    articles = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)
    questions = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)

    class Meta:
        model = Research
        fields = '__all__'
        read_only_fields = ('articles', 'questions')


class ArticleSerializer(serializers.ModelSerializer):
    sentences = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)
    takes = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)
    profiles = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    takes = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('takes', )


class SentenceSerializer(serializers.ModelSerializer):
    responses = serializers.PrimaryKeyRelatedField(many=True,  read_only=True)

    class Meta:
        model = Sentence
        fields = '__all__'
        read_only_fields = ('responses', )


class TakeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Take
        fields = '__all__'


class ResponseSerializer(serializers.ModelSerializer):
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






