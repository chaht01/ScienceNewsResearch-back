from django.contrib.auth.models import User
from rest_framework import serializers
from cq.models import Research, Article, Sentence, Question, Take, Response, Milestone, Profile


class UserSerializer(serializers.ModelSerializer):
    questions = serializers.HyperlinkedRelatedField(many=True, view_name='question-detail', read_only=True)
    takes = serializers.HyperlinkedRelatedField(many=True, view_name='take-detail', read_only=True)
    responses = serializers.HyperlinkedRelatedField(many=True, view_name='response-detail', read_only=True)
    milestones = serializers.HyperlinkedRelatedField(many=True, view_name='milestone-detail', read_only=True)
    profile = serializers.HyperlinkedRelatedField(view_name='profile-detail', read_only=True)

    class Meta:
        model = User
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class ResearchSerializer(serializers.ModelSerializer):
    articles = serializers.HyperlinkedRelatedField(many=True, view_name='article-detail', read_only=True)
    questions = serializers.HyperlinkedRelatedField(many=True, view_name='question-detail', read_only=True)

    class Meta:
        model = Research
        fields = '__all__'
        read_only_fields = ('articles', 'questions')


class ArticleSerializer(serializers.ModelSerializer):
    sentences = serializers.HyperlinkedRelatedField(many=True, view_name='sentence-detail', read_only=True)
    takes = serializers.HyperlinkedRelatedField(many=True, view_name='take-detail', read_only=True)
    profiles = serializers.HyperlinkedRelatedField(many=True, view_name='profile-detail', read_only=True)

    class Meta:
        model = Article
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    takes = serializers.HyperlinkedRelatedField(many=True, view_name='take-detail', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('takes', )


class SentenceSerializer(serializers.ModelSerializer):
    responses = serializers.HyperlinkedRelatedField(many=True, view_name='response-detail', read_only=True)

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

    class Meta:
        model = Response
        fields = '__all__'

    def update(self, instance, validated_data):
        return instance


class TakeBindMilestoneSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    milestones = serializers.HyperlinkedRelatedField(many=True, view_name='milestone-detail', read_only=True)

    class Meta:
        model = Take
        fields = '__all__'

    def create(self, validated_data):
        take = Take.objects.create(user=self.context['request'].user, **validated_data)
        milestone = Milestone.objects.create(user=self.context['request'].user,
                                             take=take)
        Response.objects.create(milestone=milestone,
                                user=self.context['request'].user)
        return take


class MileStoneSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    responses = serializers.HyperlinkedRelatedField(many=True, view_name='response-detail', read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'





