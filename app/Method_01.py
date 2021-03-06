# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# Class for evaluating prerequisite relationship using
# hyponyms, hypernyms and meronyms
#
# Authors: ...
# Modified by Luca Mirenda
#------------------------------------------------------------------

import nltk;
from nltk.corpus import wordnet as wn;
from app import db
from app.models import Baseline_Methods, Bs_status
import sys

class Method_1():
    """
    Class for evaluating prerequisite relationship using hyponyms, hypernyms and meronyms

    Attributes:
        - words: list of strings
        - bid: book id
        - cap: chapted id
        - pre_req: dict with all prerequisites
    """
    
    def __init__(self, words, bid, cap):
        """
            :param words: array of concepts
            :param bid: Book's id
            :param cap: chapter's id

        """
        self.words = words
        self.bid = bid
        self.cap = cap
        self.pre_req = dict.fromkeys(words)
        for word in self.pre_req:
            self.pre_req[word] = []
        print(type(pre_req))



    def hyponyms(self, concept):
        """ get a concept and takes all meanings from wordnet. Then gets all the hyponyms of 
            that word and check if it's inside the list words

             :param concept: string
             :return
        """
        meanings = wn.synsets(concept)
        for word in meanings:
            for types in word.hyponyms():
                for lemma in types.lemmas():
                    self.search_inv(concept, lemma.name().lower())
    
    def hypernyms(self, concept):
        """ get a concept and takes all meanings from wordnet. Then gets all the hypernyms of 
            that word and check if it's inside the list words

            :param concept: string

        """

        # iperonimi fino alla root
        meanings = wn.synsets(concept)
        for word in meanings:
            for paths in (word.hypernym_paths()):
                for level in paths:
                    for lemma in level.lemmas():
                        self.search(concept, lemma.name().lower())
    
    def meronyms(self, concept):
        """ get a concept and takes all meanings from wordnet. Then gets all the different meronyms of 
            that word and check if it's inside the list words

            :param concept:string
        """
        meanings = wn.synsets(concept)
        for word in meanings:
            for meronym in word.part_meronyms():
                for lemma in meronym.lemmas():
                    self.search_inv(concept, lemma.name().lower())
            for meronym in word.substance_meronyms():
                for lemma in meronym.lemmas():
                    self.search_inv(concept, lemma.name().lower())
            for meronym in word.member_holonyms():
                for lemma in meronym.lemmas():
                    self.search_inv(concept, lemma.name().lower())
                    
    
    def search(self, concept, lemma):
        """ add lemma as prerequisite of concept

             :param concept
             :param lemma
        """
        if(lemma in self.words):
            self.pre_req[concept].append(lemma)
            
    def search_inv(self, concept, lemma):
        """ add concept as prerequisite of lemma

             :param concept
             :param lemma
        """
        if(lemma in self.words):
            self.pre_req[lemma].append(concept)
    
    def populate_db(self, words, bid, cap):
        """
        loop inside words and create or update the corrisponding row in Baseline_methods table. The value of m1 is based
        on the presence of lemma2 inside pre_req[lemma1]

        :param words
        :param bid
        :param cap

        """
        for concept in words:
            for lemma in [lemma for lemma in words if concept != lemma]:
                bs = Baseline_Methods.query.filter_by(bid=bid, cap=cap, lemma1=concept, lemma2=lemma).first()
                if not bs:
                    if lemma in self.pre_req[concept]:
                        bs = Baseline_Methods(bid=bid, cap=cap, lemma1=concept, lemma2=lemma, m1=1)
                        db.session.add(bs)
                    else:
                        bs = Baseline_Methods(bid=bid, cap=cap, lemma1=concept, lemma2=lemma, m1=0)
                        db.session.add(bs)
                else: 
                   if lemma in self.pre_req[concept]:
                       bs.m1 = 1                
                   elif not bs.m1:
                       bs.m1 = 0
        db.session.commit()

    def updateStatus(self, status):
        """
        Update the status of a baseline method

        :param status: string (succeeded, ready, running, not ready)
        """

        row = Bs_status.query.filter_by(bid=self.bid, cap=self.cap, method=1).first()
        if not row:
            stato = Bs_status(bid=self.bid, cap=self.cap, method=1, status=status)
            db.session.add(stato)
        else:
            row.status = status
        db.session.commit()
                    
    def method_1(self):
        """Launch Method 1 and update database"""
        try:
            self.updateStatus("running")
            self.words = [word.lower() for word in self.words]

            for i, word in enumerate(self.words):
                self.words.remove(word)
                self.hyponyms(word)
                self.hypernyms(word)
                self.meronyms(word)
                self.words.insert(i, word)

            self.populate_db(self.words, self.bid, self.cap)
            self.updateStatus("succeeded")
        except:
            self.updateStatus("failed")
            print("error:", sys.exc_info())
            raise