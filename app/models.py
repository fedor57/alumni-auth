import datetime
from random import SystemRandom
import re
import string
import time

from django.db import models
from django.utils import timezone

from app.translit import translit


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


class Application(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=200)
    url = models.URLField()
    disabled = models.BooleanField(default=False)
    valid_for = models.PositiveIntegerField()

    def __unicode__(self):
        return self.slug


class invites(models.Model):
    PREFIX = '57'
    STRENGTH = 16
    STATUS_OK = 1
    STATUS_DISABLED = 2
    STATUS_BANNED = 3
    STATUSES = (
        (1, 'OK'),
        (2, 'DISABLED'),
        (3, 'BANNED'),
    )

    code = models.CharField(max_length=255)
    alumni = models.ForeignKey(alumni)
    application = models.ForeignKey(Application, null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(choices=STATUSES, default=STATUS_OK)
    disabled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def temporary_for(cls, invite, application, valid_for, session):
        try:
            new_code = invite_links.objects.get(
                code_from_id=invite.id,
                is_temporary_for=True,
                code_to__application_id=application.id
            ).code_to
            if valid_for is not None:
                new_code.ensure_expires_after(valid_for)
            return new_code
        except invite_links.DoesNotExist:
            pass

        if valid_for is None:
            valid_for = application.valid_for

        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=valid_for)
        csprng = SystemRandom()
        temp_code = '-'.join((
            'T1',
            application.slug,
            ''.join(csprng.choice(string.digits) for _ in range(cls.STRENGTH + 2))
        ))
        new_code = invites(code=temp_code, application=application, alumni_id=invite.alumni_id, expires_at=expires_at)
        new_code.save()
        link = invite_links(code_from=invite, code_to=new_code, session=session, is_temporary_for=True)
        link.save()
        return new_code

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

    def is_enabled(self):
        return self.status == self.STATUS_OK

    def is_temporary(self):
        return self.application_id is not None

    def disable(self, at=None):
        if at is None:
            at = timezone.now()

        self.status = self.STATUS_DISABLED
        if at > timezone.now():
            at = timezone.now()
        if self.disabled_at is None or self.disabled_at > at:
            self.disabled_at = at

    def merge_to(self, other_code, session):
        link = invite_links(code_from=self, code_to=other_code, is_merged_to=True, session=session)
        link.save()

    def verbose_status(self):
        if self.status == self.STATUS_OK:
            return 'ok'
        if self.status == self.STATUS_DISABLED:
            return 'disabled'
        if self.status == self.STATUS_BANNED:
            return 'banned'
        return None

    def expires_at_timestamp(self):
        if self.expires_at is not None:
            return time.mktime(self.expires_at.timetuple())
        return None

    def ensure_expires_after(self, valid_for):
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=valid_for)
        if expires_at > self.expires_at:
            self.expires_at = expires_at
            self.save()

#    def __str__(self):
#        return self.__unicode__()


class invite_links(models.Model):
    code_to = models.ForeignKey(invites, related_name="invite_links_to")
    code_from = models.ForeignKey(invites, related_name="invite_links_from")
    is_issued_by = models.BooleanField(default=False)
    is_merged_to = models.BooleanField(default=False)
    is_temporary_for = models.BooleanField(default=False)
    add_time = models.DateTimeField(auto_now_add=True)
    session = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = 'Invite link'
        verbose_name_plural = 'Invite links'

    def __unicode__(self):
        return unicode(self.code_from) + " -> " + unicode(self.code_to)

 #   def __str__(self):
 #       return self.__unicode__()




