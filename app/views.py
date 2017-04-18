# -*- coding: utf-8 -*-


import json
import time

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.utils import timezone

from app.models import alumni as Alumnus
from app.models import invites as Invite
from app.models import invite_links as InviteLink
from app.models import Application
from app.forms import CodeForm, InviteForm
import utils


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
    code_param = code_param[0].strip()

    try:
        new_code = Invite.objects.get(code=code_param)
    except Invite.DoesNotExist:
        request.session['not_found'] = True
    else:
        if not new_code.is_enabled() or new_code.is_temporary():
            request.session['disabled'] = True
        elif request.code is None:
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
            request.code.merge_to(new_code, request.session.session_key)

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
    viewdata['year'] = timezone.now().year
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
    alumnus_id = request.POST.getlist('invitee')
    if len(alumnus_id) != 1:
        return HttpResponseBadRequest("Must pass exactly one value for 'invitee'")
    try:
        alumnus_id = int(alumnus_id[0])
    except ValueError:
        raise Http404('Invitee not found')
    try:
        invitee = Alumnus.objects.get(alumnus_id=alumnus_id)
    except Alumnus.DoesNotExist:
        raise Http404('Invitee not found')

    invite = Invite(alumni_id=alumnus_id)
    invite.save()
    link = InviteLink(code_from=myinvite, code_to=invite, is_issued_by=True, session=request.session.session_key)
    link.save()

    if invite.alumni_id == myinvite.alumni_id:
        idx = len(request.session['codes'])
        request.session['codes'].append(invite.code)
        request.session.modified = True
        return redirect('/code/' + str(idx))

    if 'inv_codes' not in request.session:
        request.session['inv_codes'] = []
    inv_idx = len(request.session['inv_codes'])
    request.session['inv_codes'].append(invite.code)
    request.session.modified = True
    return redirect('/invite/' + str(inv_idx))


@code_required
def invite(request, inv_idx, self_issued=False):
    myinvite = request.code
    if self_issued:
        inv_codes = request.session['codes']
    else:
        inv_codes = request.session.get('inv_codes', [])

    inv_idx = int(inv_idx)
    assert inv_idx >= 0
    if inv_idx >= len(inv_codes):
        raise Http404('Code or invite not found')

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
    assert inv_idx >= 0
    if inv_idx >= len(request.session['codes']):
        return HttpResponseBadRequest("Code index out of range")

    request.session['code'], request.session['codes'][inv_idx] = request.session['codes'][inv_idx], request.session['code']
    return redirect('/')


@code_required
def disable(request, inv_idx):
    inv_idx = int(inv_idx)
    assert inv_idx >= 0
    if inv_idx >= len(request.session['codes']):
        return HttpResponseBadRequest("Code index out of range")

    inv = Invite.objects.get(code=request.session['codes'][inv_idx])
    inv.disable()
    inv.save()
    del request.session['codes'][inv_idx]
    request.session.modified = True
    return redirect('/')


def get_alumni(request):
    q = request.GET.get('term', '')
    names, year, letter = utils.split_search(q)
    als = Alumnus.objects.all().order_by('full_name', 'year', 'letter')
    for name in names:
        als = als.filter(full_name__icontains=name)
    if year:
        als = als.filter(year=year)
    if letter:
        als = als.filter(letter=letter)
    als = als[:20]
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


def check_code(request):
    time.sleep(0.1)
    code = request.POST.get('code', '')
    try:
        inv = Invite.objects.get(code=code)
    except Invite.DoesNotExist:
        return HttpResponse(json.dumps({'status': 'not_found'}), 'application/json')
    result = {
        'full_name': inv.alumni.full_name,
        'cross_name': u'{} {}{}'.format(inv.alumni.full_name, inv.alumni.year, inv.alumni.letter),
        'year': inv.alumni.year,
        'letter': inv.alumni.letter,
        'status': inv.verbose_status(),
        'disabled_at': inv.disabled_at,
    }
    if inv.disabled_at:
        result['disabled_at'] = inv.disabled_at.strftime('%Y-%m-%d %H:%M:%S')
    return HttpResponse(json.dumps(result), 'application/json')


def get_app_code(request):
    code = request.POST.get('code', '')
    app_id = request.POST.get('app', '')
    valid_for = request.POST.get('valid_for', None)
    result = {}

    try:
        application = Application.objects.get(slug=app_id)
        code = Invite.objects.get(code=code)
        if valid_for is not None:
            valid_for = int(valid_for)
            if valid_for < 0:
                valid_for = 0
    except Application.DoesNotExist:
        return HttpResponseBadRequest(json.dumps(dict(
            status='bad_request',
            error='application not trusted'
        )), 'application/json')
    except Invite.DoesNotExist:
        return HttpResponseBadRequest(json.dumps(dict(
            status='bad_request',
            error='code not trusted'
        )), 'application/json')
    except ValueError:
        return HttpResponseBadRequest(json.dumps(dict(
            status='bad_request',
            error='valid_for is incorrect'
        )), 'application/json')

    if code.is_temporary():
        if code.application != application:
            return HttpResponseBadRequest(json.dumps(dict(
                status='bad_request',
                error='code not trusted'
            )), 'application/json')
        if valid_for is not None:
            code.ensure_expires_after(valid_for)
        result['original_code'] = code.safe_form()
        result['code'] = code.code
        result['expires_at'] = code.expires_at_timestamp()
        result['expires_date'] = code.expires_at.strftime('%d.%m.%Y %H:%M')
    else:
        temporary_for = Invite.temporary_for(code, application, valid_for, request.session.session_key)
        result['original_code'] = code.safe_form()
        result['code'] = temporary_for.code
        result['expires_at'] = temporary_for.expires_at_timestamp()
        result['expires_date'] = temporary_for.expires_at.strftime('%d.%m.%Y %H:%M')
    return HttpResponse(json.dumps(result), 'application/json')


def qa(request):
    return render(request, 'app/qa.html')


def reroute(request, *args, **kwargs):
    return redirect('/')

