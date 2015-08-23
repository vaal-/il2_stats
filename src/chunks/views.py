from django.http import Http404
from django.shortcuts import render

from .models import Chunk


def page(request, key, template):
    chunk = Chunk.objects.get_or_create(key=key)[0]
    return render(request, template, {'chunk': chunk})
