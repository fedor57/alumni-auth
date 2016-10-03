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

def index(request, code=None):
    """Renders the ask code page."""
    assert isinstance(request, HttpRequest)
    myinvite = None
    viewdata = {}
    if request.method == 'POST':
        code = request.POST['code']
        return redirect('/' + code)
    if code:
        try:
            myinvite = Invite.objects.get(code=code)
        except:
            viewdata['not_found'] = True
    if myinvite is not None:
        viewdata['code'] = myinvite.code
        viewdata['alumni_name'] = str(myinvite.alumni)
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


def invite(request, code=None):
    """Renders the invite page."""
    assert isinstance(request, HttpRequest)
    code = Invite.objects.get(code=code)
    invitee = code.alumni
    link = InviteLink.objects.get(code_to_id=code.id)
    inviter = link.code_from.alumni
    return render(
        request,
        'app/invite.html',
        {
            'code': code,
            'inviter': inviter,
            'invitee': invitee,
        }
    )

def generate_code(request, code=None):
    alumnus_id = request.POST['invitee']
    source_code = Invite.objects.get(code=code)
    invitee = Alumnus.objects.get(alumnus_id = alumnus_id)
    inv = Invite(alumni_id = alumnus_id)
    inv.save()
    link = InviteLink(code_from=source_code, code_to=inv)
    link.save()
    return redirect('/invite/' + inv.code)


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
