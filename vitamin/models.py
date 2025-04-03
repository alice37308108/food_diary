from django.db import models
from django.utils import timezone
from django.conf import settings


class VitaminIntake(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    intake_count = models.IntegerField(default=0)
    daily_goal = models.IntegerField(default=10)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.intake_count}/{self.daily_goal}"

    def get_progress_percentage(self):
        return (self.intake_count / self.daily_goal) * 100 if self.daily_goal > 0 else 0

    def is_completed(self):
        return self.intake_count >= self.daily_goal