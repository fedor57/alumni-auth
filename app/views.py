# -*- coding: utf-8 -*-

"""
Definition of views.
"""

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

import json
from django.http import HttpResponse
from app.models import alumni as Alumnus
from app.models import invites as Invite
from app.models import invite_links as InviteLink

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )


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

def index(request):
    """Renders the ask code page."""
    assert isinstance(request, HttpRequest)
    myinvite = None
    viewdata = {}
    if request.method == 'POST':
        code = request.POST['code']
        request.session['code'] = code
        return redirect('/')
    if 'code' in request.session:
        try:
            myinvite = Invite.objects.get(code=request.session['code'])
        except:
            viewdata['not_found'] = True
    if myinvite is not None:
        viewdata['code'] = myinvite.code
        viewdata['alumni_name'] = str(myinvite.alumni)
        invited_by_list = InviteLink.objects.select_related('code_from__alumni').filter(code_to=myinvite).filter(is_issued_by=True).order_by('add_time')
        if len(invited_by_list) > 0:
            viewdata['invited_by'] = invited_by_list[0].code_from.alumni
        viewdata['invite_form'] = InviteForm()
        viewdata['invites'] = InviteLink.objects.select_related('code_to__alumni').filter(code_from=myinvite).order_by('code_to__alumni__full_name')
    else:
        viewdata['form'] = CodeForm()
    viewdata['year'] = datetime.now().year
    return render(
        request,
        'app/index.html',
        viewdata
    )


def generate_code(request):
    if 'inv_code' not in request.session:
        return redirect('/')
    code = Invite.objects.get(code=request.session['code'])
    if request.method == 'POST':
        alumnus_id = request.POST['invitee']
        invitee = Alumnus.objects.get(alumnus_id=alumnus_id)
        inv = Invite(alumni_id = alumnus_id)
        inv.save()
        link = InviteLink(code_from=code, code_to=inv)
        link.save()
        request.session['inv_code'] = inv.code
        return redirect('/new-invitation')
    inv_code = Invite.objects.get(code=request.session['inv_code'])
    invitee = inv_code.alumni
    inviter = code.alumni
    del request.session['inv_code']
    return render(
        request,
        'app/invite.html',
        {
            'code': inv_code,
            'inviter': inviter,
            'invitee': invitee,
        }
    )


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
    if 'inv_code' in request.session:
        del request.session['inv_code']
    return redirect('/')
