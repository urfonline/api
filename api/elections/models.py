from django.db import models

from api.core.utils import upload_to_content

def upload_to_elections_candidate(instance, filename):
    return upload_to_content('elections/candidates', filename)

class Position(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to=upload_to_elections_candidate, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Election Candidate"
        verbose_name_plural = "Election Candidates"

