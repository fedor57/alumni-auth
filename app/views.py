# -*- coding: utf-8 -*-

"""
Definition of views.
"""
import json

from datetime import datetime
from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.template import RequestContext

from app.models import alumni as Alumnus
from app.models import invites as Invite
from app.models import invite_links as InviteLink
from app.forms import CodeForm, InviteForm


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

def code_required(inner):
    """Decorate a view function to require authentication

    Issue a 403 Forbidden error if a valid code is not present; otherwise, pass
    control to the underlying view. Requires CodeMiddleware above in the chain.

    Invariant for the inner view: session['code'] designates a valid enabled
    code and request.code is the corresponding object."""

    def outer(request, *args, **named):
        if request.code is None:
            return HttpResponseForbidden('<h1>Похоже, что сеанс истек, войдите заново</h1>')
        return inner(request, *args, **named)
    return outer


def enter(request):
    """Add a code to the active set"""

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    code_param = request.POST.getlist('code')
    if len(code_param) != 1:
        return HttpResponseBadRequest("Must pass exactly one value for 'code'")
    code_param = code_param[0]

    try:
        new_code = Invite.objects.get(code=code_param)
    except Invite.DoesNotExist:
        request.session['not_found'] = True
    else:
        if new_code.is_disabled():
            request.session['disabled'] = True
        elif request.code == None:
            # Set new code as primary
            request.session['code']  = new_code.code
            request.session['codes'] = []
        elif request.code.alumni != new_code.alumni:
            # Forbid mixing codes for different alumni
            return render(request, 'app/alumni_switch.html', status=403)
        elif new_code.code not in request.session['codes']:
            # Add new code to active set
            request.session['codes'].append(new_code.code)
            request.session.modified = True

    return redirect('/')

def clear(request):
    """Clear the set of active codes, i.e. log out"""

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    request.session.flush()
    return redirect('/')


def index(request, code_param = ''):
    """Renders the ask code page."""
    assert isinstance(request, HttpRequest)

    myinvite = request.code
    viewdata = {}

    if 'not_found' in request.session:
        viewdata['not_found'] = True
        del request.session['not_found']
    elif 'disabled' in request.session:
        viewdata['code_disabled'] = True
        del request.session['disabled']

    if myinvite is not None:
        viewdata['code'] = myinvite.safe_form
        viewdata['alumnus_id'] = myinvite.alumni_id
        viewdata['alumni_name'] = str(myinvite.alumni)
        invited_by_list = InviteLink.objects.select_related('code_from__alumni').filter(code_to=myinvite, is_issued_by=True).order_by('add_time')
        if len(invited_by_list) > 0:
            viewdata['invited_by'] = invited_by_list[0].code_from.alumni
        viewdata['invite_form'] = InviteForm()
        viewdata['invites'] = InviteLink.objects.select_related('code_to__alumni').filter(
            code_from=myinvite,
            is_issued_by=True
        ).order_by('code_to__alumni__full_name')
        viewdata['invites'] = filter(lambda x: x.code_to.alumni != myinvite.alumni, viewdata['invites'])
        other_invites = []
        active_codes = request.session['codes']
        for invite in Invite.objects.filter(alumni_id=myinvite.alumni_id):
            if invite == myinvite:
                continue
            invited_by = InviteLink.objects.select_related('code_from__alumni').filter(code_to=invite, is_issued_by=True).order_by('add_time')
            if len(invited_by):
                invite.by = invited_by[0].code_from.alumni
                invite.at = invited_by[0].add_time.strftime('%d.%m.%y')
            if invite.code in active_codes:
                invite.activate = active_codes.index(invite.code)
            other_invites.append(invite)
        viewdata['other_invites'] = other_invites
    else:
        viewdata['form'] = CodeForm()
    viewdata['year'] = datetime.now().year
    return render(
        request,
        'app/index.html',
        viewdata
    )

@code_required
def generate_code(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    myinvite = request.code
    alumnus_id = int(request.POST['invitee'])
    try:
        invitee = Alumnus.objects.get(alumnus_id=alumnus_id)
    except Alumnus.DoesNotExist:
        raise Http404('Invitee not found')
    invite = Invite(alumni_id=alumnus_id)
    invite.save()
    link = InviteLink(code_from=myinvite, code_to=invite, is_issued_by=True)
    link.save()

    if invite.alumni_id == myinvite.alumni_id:
        idx = len(request.session['codes'])
        request.session['codes'].append(invite.code)
        request.session.save()
        return redirect('/code/' + str(idx))

    if 'inv_codes' not in request.session:
        request.session['inv_codes'] = []
    inv_idx = len(request.session['inv_codes'])
    request.session['inv_codes'].append(invite.code)
    request.session.save()
    return redirect('/invite/' + str(inv_idx))

@code_required
def invite(request, inv_idx, self_issued=False):
    myinvite = request.code
    if self_issued:
        inv_codes = request.session['codes']
    else:
        inv_codes = request.session.get('inv_codes', None)

    inv_idx = int(inv_idx)
    if inv_codes is None or inv_idx < 0 or inv_idx >= len(inv_codes):
        raise Http404('Invite not found')

    inv_code = Invite.objects.get(code=inv_codes[inv_idx])
    invitee = inv_code.alumni
    inviter = myinvite.alumni

    if self_issued:
        return render(
            request, 
            'app/code.html', 
            {
                'code': inv_code, 
                'alumni_name': str(inviter)
            }
        )

    return render(
        request,
        'app/invite.html',
        {
            'code': inv_code,
            'inviter': inviter,
            'invitee': invitee,
        }
    )

@code_required
def switch(request, inv_idx):
    inv_idx = int(inv_idx)
    request.session['code'], request.session['codes'][inv_idx] = request.session['codes'][inv_idx], request.session['code']
    return redirect('/')

@code_required
def disable(request, inv_idx):
    inv_idx = int(inv_idx)
    inv = Invite.objects.get(code=request.session['codes'][inv_idx])
    inv.status = Invite.STATUS_DISABLED
    inv.disabled_at = datetime.now()
    inv.save()
    del request.session['codes'][inv_idx]
    request.session.save()
    return redirect('/')


def get_alumni(request):
    q = request.GET.get('term', '')
    als = Alumnus.objects.filter(full_name__icontains = q)[:20]
    results = []
    for al in als:
        al_json = {}
        al_json['id'] = al.alumnus_id
        al_json['label'] = unicode(al)
        al_json['value'] = al.full_name
        results.append(al_json)
    data = json.dumps(results)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
