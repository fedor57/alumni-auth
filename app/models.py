"""
Definition of models.
"""

# Create your models here.
from django.db import models

# Each model extends models.Model
class alumni(models.Model): 
    alumnus_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150) 
    year = models.IntegerField()
    letter = models.CharField(max_length=2)
    add_time = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=50)
    class Meta:
        verbose_name = 'Alumnus'
        verbose_name_plural = 'Alumni'
    def __str__(self):
        return self.full_name + ", " + str(self.year) + self.letter

class invites(models.Model):
    code = models.BigIntegerField(primary_key=True)
    alumni_id = models.ForeignKey(alumni)
    add_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Invite'
        verbose_name_plural = 'Invites'
    def __str__(self):
        return str(self.code) + "(" + str(self.alumni) + ")"


class invite_links(models.Model):
    code_to = models.ForeignKey(invites, related_name="invite_links_to")
    code_from = models.ForeignKey(invites, related_name="invite_links_from")
    is_issued_by = models.BooleanField()
    is_merged_to = models.BooleanField()
    add_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'Invite link'
        verbose_name_plural = 'Invite links'
    def __str__(self):
        return str(self.code_to) + "->" + str(self.code_from)
