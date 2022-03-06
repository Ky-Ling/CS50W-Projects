import random
from django.shortcuts import render
from markdown2 import Markdown
from . import util
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.files.storage import default_storage


class SearchForm(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder":"Search Wiki", "style":"width:100%"}))

class NewPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={"placeholder":"Title", "id":"new-entry-title"}))
    data = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder":"Input the Content Here", "id":"new-entry"}))

class EditPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={"id":"edit-entry-title"}))
    data = forms.CharField(label="", widget=forms.Textarea(attrs={"id":"edit-entry"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    entry = util.get_entry(title.strip())
    
    if entry == None:
        entry = "## Page was not found!"
    
    markdowner = Markdown()
    entry = markdowner.convert(entry)

    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "title": title,
        "form": SearchForm()
    })

def search(request):

    if request.method == "POST":
        entries_found = []  
        entries_all = util.list_entries()

        # Take in the data the user submitted and save it as form
        form = SearchForm(request.POST)

        if form.is_valid():
            
            # Isolate the query from the "cleaned" version of the form data
            query = form.cleaned_data["query"]

            # Iterate all the entries 
            for entry in entries_all:

                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    
                    # Redirect the user to the list of entries
                    return HttpResponseRedirect(reverse("entry", args=[title]))

                if query.lower() in entry.lower():
                    entries_found.append(entry)

            return render(request, "encyclopedia/search.html", {
                "results": entries_found,
                "query": query,
                "form": SearchForm()
            })

    # If the form is invalid, re-render the page with existing info
    return render(request, "encyclopedia/search.html", {
        "results": "",
        "query": "",
        "form": SearchForm()
    })

def create(request):

    if request.method == "POST":

        new_entry = NewPageForm(request.POST)

        if new_entry.is_valid():
            # Extract title and data of the new entry
            title = new_entry.cleaned_data["title"]
            data = new_entry.cleaned_data["data"]
            
            entries_all = util.list_entries()

            # Check if entry exist in the list
            for entry in entries_all:
                if entry.lower() == title.lower():
                    return render(request, "encyclopedia/create.html", {
                        "form": SearchForm(),
                        "newPageForm": NewPageForm(),
                        "error": "This entry already exists, please try another!"
                    })

            new_entry_title = "# " + title
            new_entry_data = "\n" + data

            new_entry_content = new_entry_title + new_entry_data

            util.save_entry(title, new_entry_content)
            entry = util.get_entry(title)

            markdowner = Markdown()
            entry_converted = markdowner.convert(entry)

            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": entry_converted,
                "form": SearchForm()
            })   
    
    # Default Value
    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "newPageForm": NewPageForm()
    })
                
def editEntry(request, title):
    if request.method == "POST":
        # Get data for the entry will be edited
        entry = util.get_entry(title)

        # Display content on the textarea
        editPageForm = EditPageForm(initial={"title": title, "data": entry})

        # Return the page with forms filled with entry information
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "editPageForm": editPageForm,
            "entry": entry,
            "title": title
        })

def submitEditEntry(request, title):
    if request.method == "POST":

        # Extract info from form
        edit_form = EditPageForm(request.POST)

        if edit_form.is_valid():
            # Extract content and title from the form
            content = edit_form.cleaned_data["data"]
            title_edit = edit_form.cleaned_data["title"]

            # If the title is edited, delete the old version 
            if title_edit != title:
                filename = f"entries/{title}.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)

            # Save this new entry
            util.save_entry(title_edit, content)

            # Get the new entry
            entry = util.get_entry(title_edit)
            
            markdowner = Markdown()
            entry_converted = markdowner.convert(entry)

            msg_sussess = "Updated successfully!"

            # Return to the edited entry
            return render(request, "encyclopedia/entry.html", {
                "title": title_edit,
                "entry": entry_converted,
                "form": SearchForm(),
                "msg_success": msg_sussess
            })

def randomEntry(request):
    entries = util.list_entries()

    # Get the title of a randomly selected entry
    title = random.choice(entries)

    # Get the entry based on the random title
    entry = util.get_entry(title)

    markdowner = Markdown()
    entry_converted = markdowner.convert(entry)

    # return HttpResponseRedirect(reverse("entry", args=[title]))
    return render(request, "encyclopedia/entry.html", {
        "entry": entry_converted,
        "title": title,
        "form": SearchForm()
    })
