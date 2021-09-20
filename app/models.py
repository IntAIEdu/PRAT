#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# File for the definition of the database
#
# Authors: .. Andre, Luca Mirenda, Andrea Sava
#------------------------------------------------------------------

from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import event, DDL

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    """ Table for storing user data"""
    uid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128))
    surname = db.Column(db.String(128)) 
    email = db.Column(db.String(120), index = True, unique = True)
    psw = db.Column(db.String(128))
    books = db.relationship('bookStructure', backref='loader',
                            lazy='dynamic')

    
    def __repr__(self):
        return '<User {}>'.format(self.email)
    
    def set_password(self, password):
        self.psw = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.psw, password)
    
    def get_id(self):
           return (self.uid)
    

    
    
class bookStructure (db.Model):
    """ Table for storing the structure of the book, with section and starting sentence"""
    bid = db.Column(db.Integer, db.ForeignKey('book.bid'), primary_key = True)
    section = db.Column(db.String(20), primary_key = True)
    sentence = db.Column(db.Integer)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    
    def __repr__(self):
        return '<Book_Structure {}>'.format(self.bid)
    
class Conll (db.Model):
    """ Table for storing the texts in conll format"""
    bid = db.Column(db.Integer, primary_key = True)
    cap = db.Column(db.Integer, primary_key = True)
    conll = db.Column(db.Text)
    conll_processed = db.Column(db.Text)
    
    def __repr__(self):
        return '<Conll {}>'.format(self.conll)
    
class Book (db.Model):
    """ Store book data"""
    bid = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    year = db.Column(db.Integer)
    category = db.Column(db.String(100))
    language = db.Column(db.String(100))
    authors = db.relationship('Author', backref='books',
                            lazy='dynamic')
    
    
    def __repr__(self):
        return '<Book {}>'.format(self.title)
    
class Author (db.Model):
    """Store data of authors of books"""
    bid = db.Column(db.Integer, db.ForeignKey('book.bid'), primary_key = True)
    name = db.Column(db.String(120), primary_key = True) 
    
    def __repr__(self):
        return '<Author {}>'.format(self.name)
    
class Terminology (db.Model):
    """ Store the terminology with the relative wikipedia url"""
    tid = db.Column(db.Integer, primary_key = True)
    lemma = db.Column(db.String(120))
    wiki_url = db.Column(db.Text)
    
    def __repr__(self):
        return '<Terminology {}>'.format(self.lemma)
    
class Terminology_reference (db.Model):
    """Store where each term is used"""
    tid = db.Column(db.Integer, db.ForeignKey('terminology.tid'), primary_key = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key = True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key = True)
    
    def __repr__(self):
        return '<Terminology_reference {}>'.format(self.tid)
    
class Baseline_Methods (db.Model):
    """ Results of all the automatic method of extraction"""
    lemma1 = db.Column(db.Integer, db.ForeignKey('terminology.tid'), primary_key = True)
    lemma2 = db.Column(db.Integer, db.ForeignKey('terminology.tid'), primary_key = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key = True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key = True)
    m1 = db.Column(db.Float)
    m2 = db.Column(db.Float)
    m2_sentence = db.Column(db.Integer)
    m3 = db.Column(db.Float)
    m4 = db.Column(db.Integer)
    m4a = db.Column(db.Float)
    m4b = db.Column(db.Float)
    m5 = db.Column(db.Float)
    m6 = db.Column(db.Float)
    
    def __repr__(self):
        return '<Baseline_Methods {}>'.format(self.lemma1)
    
class Annotation_user (db.Model):
    """Store which user added which relation"""
    ann_user_id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'))
    aid = db.Column(db.Integer, db.ForeignKey('annotations.aid'))
    ann_type = db.Column(db.Integer, db.ForeignKey('annotation_types.tid'))
    
class Annotations (db.Model):
    """ Store all relations"""
    aid = db.Column(db.Integer, primary_key = True)
    lemma1 = db.Column(db.Integer, db.ForeignKey('terminology.tid'), index = True)
    lemma2 = db.Column(db.Integer, db.ForeignKey('terminology.tid'), index = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'))
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'))
    id_phrase = db.Column(db.Integer)
    
class partialAnnotations (db.Model):
    """ Save partial annotation (the user will be able to continue from here)"""
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'))
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'))
    annotation = db.Column(db.Text)

class goldStandard (db.Model):
    """ Save the gold standard and its parameters"""
    gid = db.Column(db.Integer, primary_key = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'))
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'))
    uids = db.Column(db.String(120))
    name = db.Column(db.String(120))
    gold =  db.Column(db.Text)
    agreements = db.Column(db.String(120))
    
class User_Experience (db.Model):
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'))
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'))
    exp_type = db.Column(db.Integer, db.ForeignKey('experience_types.tid'))
    
class Annotation_types (db.Model):
    tid = db.Column(db.Integer, primary_key = True)
    ann_type = db.Column(db.String(64), unique = True)    
    
class Experience_types (db.Model):
    tid = db.Column(db.Integer, primary_key = True)
    exp_type = db.Column(db.String(64), unique = True) 

class Bs_status (db.Model):
    """ Table for the status of the method (succeeded, running, ready, not ready)"""
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key = True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key = True)
    method = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.String(32))

class Bs_threshold(db.Model):
    """ Table for saving the thresholds of the baseline methods """
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key = True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key = True)
    method = db.Column(db.Integer, primary_key = True)
    threshold = db.Column(db.Float)


class Terminology_status (db.Model):
    """ Table for saving the status of the terminology """
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key = True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key = True)
    status = db.Column(db.String(32))


class Revision_type(db.Model):
    """ Table for storing the type of the revision (Confirm, Delete, Change weight)"""
    rev_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))

class Revision_tag(db.Model):
    """ Table for storing the revision tag (e.g. Definition) and the relative type of revision"""
    tag_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    rev_id = db.Column(db.Integer, db.ForeignKey('revision_type.rev_id'))

class Revised_annotations(db.Model):
    """ Table for the annotation revised """
    ann_user_id = db.Column(db.Integer, db.ForeignKey('annotation_user.ann_user_id'), primary_key = True)
    rev_id = db.Column(db.Integer, db.ForeignKey('revision_type.rev_id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('revision_tag.tag_id'))

class Revision_status(db.Model):
    """ Table for storing the status of the revision (started, not started) """
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key=True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key = True)
    status = db.Column(db.String(32))

class Burst_params(db.Model):
    """ Table for storing the selected params for a burst method"""
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key=True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key=True)
    s = db.Column(db.Float)
    gamma = db.Column(db.Float)
    level = db.Column(db.Float)
    #formula = db.Column(db.String(32))

class Allen_type(db.Model):
    type = db.Column(db.String(32), primary_key=True)

class Burst_params_allen(db.Model):
    """ Table for storing the weights for each allen type for the burst method"""
    bid = db.Column(db.Integer, db.ForeignKey('burst_params.bid'), primary_key=True)
    cap = db.Column(db.Integer, db.ForeignKey('burst_params.cap'), primary_key=True)
    type = db.Column(db.Integer, db.ForeignKey('allen_type.type'), primary_key=True)
    weight = db.Column(db.Float)

class Burst_results(db.Model):
    """ Table for storing the results of the Burst"""
    burst_id = db.Column(db.Integer, primary_key = True)
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key = True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key = True)
    lemma = db.Column(db.Integer, db.ForeignKey('terminology.lemma'))
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    freq = db.Column(db.Integer)
    status = db.Column(db.String(32))

class Burst_rel_allen(db.Model):
    """ Store each burst couple and the type of allen relation"""
    bid = db.Column(db.Integer, db.ForeignKey('conll.bid'), primary_key=True)
    cap = db.Column(db.Integer, db.ForeignKey('conll.cap'), primary_key=True)
    burst1 = db.Column(db.Integer, db.ForeignKey('burst_results.burst_id'), primary_key=True)
    burst2 = db.Column(db.Integer, db.ForeignKey('burst_results.burst_id'), primary_key=True)
    type = db.Column(db.Integer, db.ForeignKey('allen_type.type'))

