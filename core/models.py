from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    teamname = models.CharField(max_length=255, unique=True)
    teamid = models.CharField(max_length=255)
    score = models.IntegerField(default=500)

    USERNAME_FIELD = 'teamname'
    REQUIRED_FIELDS = ['username']  # keep username to satisfy AbstractUser requirements


class Challenge(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField()
    type = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=50)    
    solved_by = models.ManyToManyField(CustomUser, related_name='solved_challenges', blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_challenges' , default=None, null=True)
    is_visible = models.BooleanField(default=True)
    def __str__(self):
        return self.title


class Hint(models.Model):
    title = models.CharField(max_length=255)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    hint_text = models.TextField()
    hint_number = models.IntegerField(default=1)
    image = models.ImageField(upload_to='hints/', blank=True, null=True)
    value = models.IntegerField()
    def __str__(self):
        return f"Hint {self.hint_number} for {self.challenge.title}"
    

class Submission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)
    solution = models.TextField()
    is_correct = models.BooleanField(default=False)
    is_false = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - {self.challenge.author}"
    
# models.py
class UserHint(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hint = models.ForeignKey(Hint, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'hint')
    
    def __str__(self):
        return f"{self.user.username} - {self.hint.title}"
    
