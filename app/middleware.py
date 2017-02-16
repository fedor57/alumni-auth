# -*- coding: utf-8 -*-

from django.conf import settings
from django.http import HttpResponseForbidden

from app.models import invites as Invite


def SessionVersionMiddleware(inner):
    """Middleware for session versioning

    Check that session['version'] is equal to SESSION_VERSION, clear session
    data if it isn't."""

    def outer(request):
        if request.session.get('version', 0) != settings.SESSION_VERSION:
            request.session.clear()
        try:
            response = inner(request)
        finally:
            request.session['version'] = settings.SESSION_VERSION
        return response
    return outer


def CodeMiddleware(inner):
    """Middleware for code authentication

    If a valid enabled code is present in session['code'], save a corresponding
    model object to request.code. Issue a 403 Forbidden error for disabled
    codes. Otherwise, pass control to the underlying view.

    Invariant for the inner view: either session['code'] does not exist and
    request.code is None, or session['code'] designates a valid enabled code
    and request.code is the corresponding object."""

    def outer(request):
        request.code = None
        if 'code' in request.session:
            try:
                request.code = Invite.objects.get(code=request.session['code'])
            except Invite.DoesNotExist:
                pass
            if request.code is None or request.code.is_disabled():
                request.session.flush()
                return HttpResponseForbidden('<h1>Похоже, что сеанс истек, войдите заново</h1>')
        return inner(request)
    return outer
