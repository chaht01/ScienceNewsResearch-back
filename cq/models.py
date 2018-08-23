from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.hashers import make_password, is_password_usable
from django.dispatch import receiver
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    article = models.ForeignKey('Article', related_name='profiles', null=True, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    articles = Article.objects.all()
    articles_cnt = articles.count()
    if created:
        Profile.objects.create(
            user=instance,
            # article=(None if instance.is_superuser else articles[(instance.id % articles_cnt)])
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_save, sender=User)
def password_hashing(instance, **kwargs):
    if not is_password_usable(instance.password):
        instance.password = make_password(instance.password)


class Research(models.Model):
    title = models.CharField(max_length=1024)
    author = models.CharField(max_length=1024)
    link = models.CharField(max_length=1024)

    def __str__(self):
        return self.title


class Article(models.Model):
    research = models.ForeignKey('Research', related_name='articles',null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
#    date = models.DateTimeField()
    publisher = models.CharField(max_length=100)
    link = models.CharField(max_length=1024)

    def __str__(self):
        return self.title

class Sentence(models.Model):
    text = models.CharField(max_length=1024)
    paragraph_order = models.IntegerField()
    order = models.IntegerField()
    article = models.ForeignKey('Article', related_name='sentences',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

class Codefirst(models.Model):
    text=models.CharField(max_length=512)

    def __str__(self):
        return self.text

class Codesecond(models.Model):
    text=models.CharField(max_length=512)
    first_code=models.ForeignKey('Codefirst', related_name='secondcodes',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Question(models.Model):
    article = models.ForeignKey('Article', related_name='questions',null=True, on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    questioner = models.ForeignKey('auth.User', related_name='questions', on_delete=models.CASCADE)
    intention = models.CharField(max_length=1024, default='no intention')
#    created_at=models.DateTimeField(blank=True)
#    removed_at=models.DateTimeField(blank=True, null=True)
    code_first=models.ForeignKey('Codefirst', related_name='questions',null=True, on_delete=models.CASCADE)
    code_second=models.ForeignKey('Codesecond', related_name='questions',null=True, on_delete=models.CASCADE)
    created_step = models.IntegerField(default=0)
    removed_step = models.IntegerField(default=0)
    copied_from=models.ForeignKey('self', on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Reftext(models.Model):
    questioner=models.ForeignKey('auth.User', related_name='reftexts', on_delete=models.CASCADE)
    question=models.ForeignKey('Question', related_name='reftexts',null=True, on_delete=models.CASCADE)
    sentence=models.ForeignKey('Sentence', related_name='reftexts',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'question-' + str(self.question.id) + ':' \
               + 'sentence-' + str(self.sentence.id) +':'\
               + 'questioner-' +str(self.questioner.id)

class Shown(models.Model):
    answerer=models.ForeignKey('auth.User', related_name='showns', on_delete=models.CASCADE)
    question=models.ForeignKey('Question', related_name='showns',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'answerer-' + str(self.answerer.id) + ':' \
               + 'question-' + str(self.question.id)

class Take(models.Model):
    shown = models.ForeignKey('Shown', related_name='takes',null=True, on_delete=models.CASCADE)
    taken = models.BooleanField()

    def __str__(self):
        return 'shown-' + str(self.shown.id) + ':' \
               + 'taken-' + str(self.taken)

class Answertext(models.Model):
    take = models.ForeignKey('Take', related_name='answertexts',null=True, on_delete=models.CASCADE)
    sentence = models.ForeignKey('Sentence', related_name='answertexts',null=True, on_delete=models.CASCADE)
 #   answered_at = models.DateTimeField(blank=True)

    def __str__(self):
        return 'take-' + str(self.take.id) + ':' \
               + 'sentence-' + str(self.sentence.id)

class Judgement(models.Model):
    question_first=models.ForeignKey('Question', related_name='judgements_first',null=True, on_delete=models.CASCADE)
    question_second=models.ForeignKey('Question', related_name='judgements_second',null=True, on_delete=models.CASCADE)
    questioner=models.ForeignKey('auth.User', related_name='judgements', on_delete=models.CASCADE)
    score=models.IntegerField()
    similarity=models.ForeignKey('Similarity', related_name='judgements',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'question1-' + str(self.question_first.id) + ':' \
               + 'question2-' + str(self.question_second.id) + ':' \
               + 'questioner-' + str(self.questioner.id) + ':' \
               + 'score-' + str(self.score)

class Similarity(models.Model):
    question_first=models.ForeignKey('Question', related_name='similaritys_first',null=True, on_delete=models.CASCADE)
    question_second=models.ForeignKey('Question', related_name='similaritys_second',null=True, on_delete=models.CASCADE)
    similarity=models.FloatField()

    def __str__(self):
        return 'question1-' + str(self.question_first.id) + ':' \
               + 'question2-' + str(self.question_second.id) + ':' \
               + 'similarity-' + str(self.similarity)

""" class Take(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='takes')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='takes')
    user = models.ForeignKey('auth.User', related_name='takes')
    phase = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    remove = models.BooleanField(default=False)
    removed_phase = models.IntegerField(blank=True, null=True)
    removed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return 'article-' + str(self.article.id) + ':' \
               + 'question-' + str(self.question.id) + ':' \
               + 'user-' + str(self.user.id)


class Response(models.Model):
    milestone = models.ForeignKey('Milestone', related_name='responses', null=True)
    user = models.ForeignKey('auth.User', related_name='responses')
    sentence = models.ForeignKey('Sentence', related_name='responses', null=True)


class Milestone(models.Model):
    user = models.ForeignKey('auth.User', related_name='milestones')
    take = models.ForeignKey('Take', related_name='milestones')
    found = models.NullBooleanField()
    like_cnt = models.IntegerField(default=0)
    response_at = models.DateTimeField(auto_now_add=True)
    copied_from = models.ForeignKey('Milestone', related_name='milestones', null=True)
 """
