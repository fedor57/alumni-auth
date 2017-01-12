# -*- coding: utf-8 -*-

"""
Definition of views.
"""
import json

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from app.models import alumni as Alumnus
from app.models import invites as Invite
from app.models import invite_links as InviteLink
from app.forms import CodeForm, InviteForm


def askcode(request):
    """Renders the ask code page."""
    assert isinstance(request, HttpRequest)
    form_class = CodeForm()
    return render(
        request,
        'app/askcode.html',
        {
            'form': form_class,
        }
    )

def index(request, code_param = ''):
    """Renders the ask code page."""
    assert isinstance(request, HttpRequest)
    myinvite = None
    viewdata = {}
    if request.method == 'POST':
        code_param = request.POST['code']
        if code_param is not None and len(code_param) > 0:
            myinvite = Invite.objects.get(code=code_param)
            if request.session.get('code', None):
                if 'codes' not in request.session:
                    request.session['codes'] = []
                request.session['codes'].append(code_param)
            else:
                request.session['code'] = code_param
            request.session.save()
            return redirect('/')
    if 'code' in request.session:
        try:
            myinvite = Invite.objects.get(code=request.session['code'])
        except:
            viewdata['not_found'] = True
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
        other_invites = []
        active_codes = request.session.get('codes', [])
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


def generate_code(request):
    if request.method != 'POST':
        return redirect('/')
    myinvite = None
    if 'code' in request.session:
        try:
            myinvite = Invite.objects.get(code=request.session['code'])
        except:
            myinvite = None
    if myinvite is None:
        return redirect('/')
    alumnus_id = int(request.POST['invitee'])
    invitee = Alumnus.objects.get(alumnus_id=alumnus_id)
    invite = Invite(alumni_id = alumnus_id)
    invite.save()
    link = InviteLink(code_from=myinvite, code_to=invite, is_issued_by=True)
    link.save()

    if invite.alumni_id == myinvite.alumni_id:
        if 'codes' not in request.session:
            request.session['codes'] = []
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


def invite(request, inv_idx, self_issued=False):
    myinvite = None
    if 'code' in request.session:
        try:
            myinvite = Invite.objects.get(code=request.session['code'])
        except:
            myinvite = None
    if myinvite is None:
        return HttpResponseForbidden('<h1>Похоже, что сеанс истек, войдите заново</h1>')
    if self_issued:
        inv_codes = request.session.get('codes', None)
    else:
        inv_codes = request.session.get('inv_codes', None)

    inv_idx = int(inv_idx)
    if inv_codes is None or inv_idx < 0 or inv_idx >= len(inv_codes):
        return HttpResponseNotFound('<h1>Приглашение не найдено, откройте страницу заново</h1>')

    inv_code = Invite.objects.get(code=inv_codes[inv_idx])
    if self_issued:
        return render(request, 'app/code.html', {'code': inv_code})
    invitee = inv_code.alumni
    inviter = myinvite.alumni
    return render(
        request,
        'app/invite.html',
        {
            'code': inv_code,
            'inviter': inviter,
            'invitee': invitee,
        }
    )


def switch(request, inv_idx):
    inv_idx = int(inv_idx)
    old_code = request.session['code']
    request.session['code'], request.session['codes'][inv_idx] = request.session['codes'][inv_idx], request.session['code']
    return redirect('/')


def get_alumni(request):
    #if request.is_ajax():
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
    #else:
    #    data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def logout(request):
    del request.session['code']
    if 'inv_codes' in request.session:
        del request.session['inv_codes']
    if 'codes' in request.session:
        del request.session['codes']
    return redirect('/')
