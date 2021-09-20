# -*- coding: utf-8 -*-

import app
from app import app, db
from app.models import Terminology
import wikipedia

def prova():
    words = Terminology.query.all()
    title = [word.wiki_url for word in words if word.wiki_url]
    for name in title:
        try:
            poss = wikipedia.page(title=name)
            print(poss)
        except wikipedia.exceptions.DisambiguationError as e:
            pass