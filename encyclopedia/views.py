from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
import random
from markdown2 import Markdown

from . import util

class SearchForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs=
                {
                    "class": "search",
                    "placeholder": "Search Wikipedia Clone"
                }
            )
        )

class CreateForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea)

class EditForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea)


def index(request):
    """ Return a list of page titles """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm()
    })

def entry(request, title):
    """ Return a page with a matching title """
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": Markdown().convert(util.get_entry(title=title)),
        "search_form": SearchForm()
    })

def search(request):
    """ Search for a page """
    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = util.get_entry(title)
            print(f"search request: {entry}")
            if entry:
                return redirect(reverse('entry', args=[title]))
            else:
                related_entries = util.get_related_entrys(title)
                print(f"Related entries: {related_entries}")
                return render(request, "encyclopedia/search.html",
                {
                    "title": title,
                    "entries": related_entries,
                    "search_form": SearchForm()
                }
                )
    return redirect(reverse('index'))

def create(request):
    """ Create a new page """
    if request.method == "POST":
        form = CreateForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            print(f"Title: {title}")

            if title in util.list_entries():
                return render(request, "encyclopedia/create.html",
                {
                    "message": "Title already exists, try again.",
                    "create_form": form,
                    "search_form": SearchForm()
                })
            else:
                util.save_entry(title=title, content=content)
                return redirect(reverse('entry', args=[title]))


    return render(request, "encyclopedia/create.html",
                {
                    "message": None,
                    "create_form": CreateForm(),
                    "search_form": SearchForm()
                })


def edit(request, title):
    """ Edit an existing page """
    if request.method == "POST":
        form = EditForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect(reverse('entry', args=[title]))

    text = util.get_entry(title)
    return render(request, "encyclopedia/edit.html",
                {
                    "title": title,
                    "edit_form": EditForm(initial={"content":text}),
                    "search_form": SearchForm()
                })

def random_title(request):
    """ Returns a random page """
    entries = util.list_entries()
    entry = random.choice(entries)
    return redirect(reverse('entry', args=[entry]))


