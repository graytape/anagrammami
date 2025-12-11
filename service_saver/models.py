from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Anagrams(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='anagrams')
    model = models.CharField(max_length=255)
    anagrams = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    create_date = models.DateField(default=datetime.today().strftime('%Y-%m-%d'))

    class Meta:
        verbose_name_plural = "Anagrams"
