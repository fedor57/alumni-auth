"""
Definition of models.
"""

# Create your models here.
from django.db import models
from app.translit import translit
from random import randint


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

    def __unicode__(self):
        return self.full_name + ", " + unicode(self.year) + self.letter

#    def __str__(self):
#        return self.__unicode__()


class invites(models.Model):
    PREFIX = '57'
    code = models.CharField(max_length=255)
    alumni = models.ForeignKey(alumni)
    add_time = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(invites, self).__init__(*args, **kwargs)
        if not self.code and self.alumni_id:
            code = [self.PREFIX, str(self.alumni.year) + translit(self.alumni.letter).lower()]
            surname, name = self.alumni.full_name.split(' ')
            code.append(translit(surname[:3]).lower() + translit(name[0]).lower())
            code.append(str(randint(1000000000000000, 9999999999999999)))
            self.code = "-".join(code)

    class Meta:
        verbose_name = 'Invite'
        verbose_name_plural = 'Invites'

    def __unicode__(self):
        return unicode(self.code) + " (" + unicode(self.alumni) + ")"

#    def __str__(self):
#        return self.__unicode__()


class invite_links(models.Model):
    code_to = models.ForeignKey(invites, related_name="invite_links_to")
    code_from = models.ForeignKey(invites, related_name="invite_links_from")
    is_issued_by = models.BooleanField(default=False)
    is_merged_to = models.BooleanField(default=False)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Invite link'
        verbose_name_plural = 'Invite links'

    def __unicode__(self):
        return unicode(self.code_from) + " -> " + unicode(self.code_to)

 #   def __str__(self):
 #       return self.__unicode__()
