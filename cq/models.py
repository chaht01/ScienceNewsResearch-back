from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.hashers import make_password, is_password_usable
from django.dispatch import receiver
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    article = models.ForeignKey('Article', related_name='profiles', null=True)


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
    research = models.ForeignKey('Research', related_name='articles')
    title = models.CharField(max_length=1024)
    date = models.DateTimeField()
    publisher = models.CharField(max_length=100)
    link = models.CharField(max_length=1024)

    def __str__(self):
        return self.title


class Question(models.Model):
    research = models.ForeignKey('Research', related_name='questions')
    text = models.CharField(max_length=512)
    owner = models.ForeignKey('auth.User', related_name='questions')
    created_phase = models.IntegerField()

    def __str__(self):
        return self.text


class Sentence(models.Model):
    text = models.CharField(max_length=1024)
    paragraph_order = models.IntegerField()
    order = models.IntegerField()
    article = models.ForeignKey('Article', related_name='sentences')

    def __str__(self):
        return self.text


class Take(models.Model):
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

