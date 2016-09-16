"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime

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

def invite(request, code):
    """Renders the invite page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/invite.html',
        {
            'title':'Invite',
            'message':'Invite it.',
            'year':datetime.now().year,
            'code':code,
        }
    )

from app.forms import CodeForm

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

import json
from django.http import HttpResponse
from app.models import alumni as Alumnus
from app.models import invites as Invite
from app.models import invite_links as InviteLink

def generate_code(request):
    code = request.GET['code']
    alumnus_id = request.GET['id']
    source_code = Invite.objects.get(code=code)
    inviter = source_code.alumni
    invitee = Alumnus.objects.get(alumnus_id = alumnus_id)
    inv = Invite(alumni_id = alumnus_id)
    inv.save()
    link = InviteLink(code_from=source_code, code_to=inv)
    link.save()

    data = {
        'code': inv.code,
        'invitee': unicode(invitee),
        'invitee_name': invitee.full_name,
        'inviter': unicode(inviter),
    }
    return HttpResponse(json.dumps(data), 'application/json')


def get_alumni(request):
    #if request.is_ajax():
    q = request.GET.get('term', '')
    als = Alumnus.objects.filter(full_name__icontains = q )[:20]
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
