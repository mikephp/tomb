from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import render_to_response
from django.template import RequestContext

# Create your views here.

def index(request):
    books = Book.objects.all()
    authors = Author.objects.all()
    publishers = Publisher.objects.all()
    ctx = {'books': books, 'authors': authors, 'publishers': publishers}
    return render_to_response('bookstore/index.html', ctx)

from django import forms

class ContactForm(forms.Form):
    subject = forms.CharField(max_length = 100)
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea)


def contact(request):
    if request.method == 'POST':
        print 'Got POST Request'
        form = ContactForm(request.POST)
        if form.is_valid():
            cf = form.cleaned_data
            print cf
            return redirect('/store/thanks')
    else:
        print 'Got GET Request'
        form = ContactForm(initial = {'subject':'Initial subject', 'message':'Initial message'})
    return render_to_response('bookstore/contact.html', {'form':form}, RequestContext(request))

def thanks(request):
    ctx = {'subject': request.GET.get('subject', 'unknown'),
           'email': request.GET.get('email', 'unknown'),
           'message': request.GET.get('message', 'unknown')}
    return render_to_response('bookstore/thanks.html', ctx)
