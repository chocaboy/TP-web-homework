from django.contrib.auth.models import User
from django.db import models


class QuestionManager(models.Manager):
    def by_tag(self, tag_name): 
        return self.get_queryset().filter(tags__name=tag_name)
    
    def new(self):
        return self.get_queryset().order_by('-created_at')
    
    def hot(self):
        return self.get_queryset().annotate(likes_count=models.Count('likes')).order_by('-likes_count')


# 1. Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return self.user.username


# 2. Tag
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


# 3. Question (использует Profile и Tag)
class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = QuestionManager()

    def __str__(self):
        return self.title
    def get_url(self):
        return f"/question/{self.id}/"
    def likes_count(self):
        return self.likes.count()



# 4. Answer
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text[:50]
    def likes_count(self):
        return self.likes.count()


# 5. Лайки
class QuestionLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'question')


class AnswerLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'answer')
