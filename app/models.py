"""
Definition of models.
"""

# Create your models here.
from random import SystemRandom
from django.db import models
from app.translit import translit

import re
import string

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
    STRENGTH = 16
    STATUS_OK = 1
    STATUS_DISABLED = 2
    STATUSES = (
        (1, 'OK'),
        (2, 'DISABLED'),
    )

    code = models.CharField(max_length=255)
    alumni = models.ForeignKey(alumni)
    add_time = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=STATUSES, default=STATUS_OK)
    disabled_at = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(invites, self).__init__(*args, **kwargs)
        if not self.code and self.alumni_id:
            code = [self.PREFIX, str(self.alumni.year) + translit(self.alumni.letter).lower()]
            full_name = re.sub(r'\([^)]*\)\s+', '', self.alumni.full_name)
            surname, name = full_name.split(' ', 1)
            code.append(translit(surname[:3]).lower() + translit(name[0]).lower())
            csprng = SystemRandom()
            code.append(''.join(csprng.choice(string.digits) for _ in range(self.STRENGTH)))
            self.code = "-".join(code)

    class Meta:
        verbose_name = 'Invite'
        verbose_name_plural = 'Invites'

    def __unicode__(self):
        return unicode(self.code) + " (" + unicode(self.alumni) + ")"

    def safe_form(self):
        code = self.code[:-self.STRENGTH] + 'x' * (self.STRENGTH-4) + self.code[-4:]
        return unicode(code)

    def is_disabled(self):
        return self.status == self.STATUS_DISABLED

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
