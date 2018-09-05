from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.hashers import make_password, is_password_usable
from django.dispatch import receiver
from django.contrib.auth.models import User
from datetime import datetime


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
    code_first=models.ForeignKey('Codefirst', related_name='code_seconds',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Question(models.Model):
    article = models.ForeignKey('Article', related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=512)
    questioner = models.ForeignKey('auth.User', related_name='questions', on_delete=models.CASCADE)
    intention = models.CharField(max_length=1024, default='no intention')
    created_at=models.DateTimeField(auto_now_add=True)
    removed_at=models.DateTimeField(null=True)
    code_first=models.ForeignKey('Codefirst', related_name='questions', on_delete=models.CASCADE)
    code_second=models.ForeignKey('Codesecond', related_name='questions', null=True, on_delete=models.CASCADE)
    created_step = models.IntegerField(default=1)
    removed_step = models.IntegerField(null=True)
    copied_to=models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.text


class Reftext(models.Model):
    questioner = models.ForeignKey('auth.User', related_name='reftexts', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='reftexts', null=True, on_delete=models.CASCADE)
    sentence = models.ForeignKey('Sentence', related_name='reftexts', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'question-' + str(self.question.id) + ':' \
               + 'sentence-' + str(self.sentence.id) +':'\
               + 'questioner-' +str(self.questioner.id)


class Shown(models.Model):
    answerer = models.ForeignKey('auth.User', related_name='showns', on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='showns',null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'answerer-' + str(self.answerer.id) + ':' \
               + 'question-' + str(self.question.id)


@receiver(post_save, sender=Shown)
def create_take(sender, instance, created, **kwargs):
    if created:
        Take.objects.create(
            shown=instance,
            taken=False
        )


class Take(models.Model):
    shown = models.ForeignKey('Shown', related_name='takes', null=True, on_delete=models.CASCADE)
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
    question_first = models.ForeignKey('Question', related_name='judgement_firsts', on_delete=models.CASCADE)
    question_second = models.ForeignKey('Question', related_name='judgement_seconds', null=True, on_delete=models.CASCADE)
    questioner = models.ForeignKey('auth.User', related_name='judgements', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return 'question1-' + str(self.question_first.id) + ':' \
               + 'question2-' + str(self.question_second.id) if self.question_second is not None else None + ':' \
               + 'questioner-' + str(self.questioner.id) + ':' \
               + 'score-' + str(self.score)
