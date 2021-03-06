# -*- coding: utf-8 -*-
#------------------------------------------------------------------
# File with all the wtforms
#
# Authors: .., Luca Mirenda, Andrea Sava
#------------------------------------------------------------------
from flask_wtf import FlaskForm
from flask import flash, redirect, url_for
from wtforms import widgets, StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField,FloatField, FileField, SelectMultipleField
from wtforms.validators import InputRequired, Email, EqualTo, ValidationError, Optional
from flask_wtf.file import FileRequired, FileAllowed
from app.models import User


class LoginForm(FlaskForm):
    """ Form for log the user """
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    """ Form for the registration """
    name = StringField('Name', validators=[InputRequired()])
    surname = StringField('Surname', validators=[InputRequired()])
    email = StringField('Email', validators =[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    repeat_password = PasswordField('Repeat Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        """ Check if email is already in database """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            flash("Email already used", "danger")
            raise ValidationError('')

class TextDeleteForm(FlaskForm):
    """ Form for the selection of the book to delete """
    book_cap = SelectField('Book', choices = [])
    submit = SubmitField('Delete Text')

class TextDownloadForm(FlaskForm):
    """ Form for the selection of the book to download """
    book_cap = SelectField('Book', choices = [])
    submit = SubmitField('Delete Download')

class BaselineForm(FlaskForm):
    """ Form for the selection of the book and the method to use for the automatic extraction of prerequisites """
    book_cap = SelectField('Book', choices = [])
    baseline_method = SelectField('Method', choices = [('1','1: Lexical Relations'), ('2','2: Lexical Syntactic Pattern Match'), ('3','3: Relational Metric'), ('4','4: Wikipedia'), ('5','5: Textbook Structure'),('6','6: Temporal Patterns')])
    threshold = FloatField('Threshold')

    # Burst method
    default = BooleanField('Default params', default='checked')
    s = FloatField('S', default='1.05')
    gamma = FloatField('Gamma', default='0.0001')
    level = FloatField('Level', default='1')
    # Allen weights
    equals = FloatField('Equals', default='2')
    before = FloatField('Before', default='5')
    after = FloatField('After', default='0')
    meets = FloatField('Meets', default='3')
    metby = FloatField('Met-by', default='0')
    overlaps = FloatField('Overlaps', default='7')
    overlappedby = FloatField('Overlapped-by', default='1')
    during = FloatField('During', default='7')
    includes = FloatField('Includes', default='7')
    starts = FloatField('Starts', default='4')
    startedby = FloatField('Started-by', default='2')
    finishes = FloatField('Finishes', default='2')
    finishedby = FloatField('Finished-by', default='8')

    max_gap = FloatField('Max gap', default='4')
    norm_formula = StringField('Norm Formula',default="modified")
    use_inverses = BooleanField('Use inverses', default='unchecked')


    submit = SubmitField('Launch Method')


class BaselineResultsForm(FlaskForm):
    """ Form for the selection of the book and the baseline method for the visualization of the results """
    book_cap = SelectField('Book', choices = [])
    baseline_method = SelectField('Method', choices = [('1','1: Lexical Relations'), ('2','2: Lexical Syntactic Pattern Match'), ('3','3: Relational Metric'), ('4','4: Wikipedia'), ('5','5: Textbook Structure'),('6','6: Temporal Patterns')])
    submit = SubmitField('View Results')

class NonValidatingSelectField(SelectField):
    """ Selection field that must not be validated """
    def pre_validate(self, form):
        pass

class NonValidatingSelectMultipleField(SelectMultipleField):
    """ Multiple selection field that must not be validated """
    def pre_validate(self, form):
        pass

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def pre_validate(self, form):
        pass


class GoldStandardForm(FlaskForm):
    """ Form for the selection of the annotations to use for the creation of the gold standard"""
    book_cap = SelectField('Book', choices = [])
    annotation = MultiCheckboxField('Annotation')
    agreements = NonValidatingSelectField('Combination criteria', choices = [])
    name = StringField("Name")
    submit = SubmitField('Launch Creation')
    
class AnalysisForm(FlaskForm):
    """ Form for the selection of the book and the type of analysis to visualize """
    book_cap = SelectField('Book', choices = [])
    analysis_type = SelectField('Type of Analysis', choices = [('1','Data Summary'), ('2','Linguistic Analysis'), ('3','Agreement Calculation'), ('4', "Fleiss's kappa")])
    annotation_1 = NonValidatingSelectField('Annotation/Method', choices = [])
    annotation_2 = NonValidatingSelectField('Annotation/Method', choices = [('Default', 'Choose an annotation or a method')], default='Default')
    submit = SubmitField('Launch Analysis')
    
class ComparisonForm(FlaskForm):
    """ Form for the selection of the 2 annotations to compare """
    book_cap = SelectField('Book', choices = [])
    comparison_1 = NonValidatingSelectField('Item 1', choices = [])
    comparison_2 = NonValidatingSelectField('Item 2',choices = [])
    gold = NonValidatingSelectField('Gold', choices=[('None',"None")], default='None')
    submit = SubmitField('Launch Comparison')

class RevisionForm(FlaskForm):
    """ Form for the selection of the book to revise """
    book_cap = SelectField('Book', choices = [])
    submit = SubmitField('Launch Revision')
    
class PreAnnotatorForm(FlaskForm):
    """ Form for the selection of the book to annotate """
    book_cap = SelectField('Book', choices = [])
    submit = SubmitField('Start')
    
class PreVisualizationForm(FlaskForm):
    """ Form for the selection of the annotation for the visualization """
    book_cap = SelectField('Book', choices = [])
    author = NonValidatingSelectField('Author', choices = [])
    visualization_type = SelectField('Type of Visualization', choices = [('1','Matrix'), ('2','Arc Diagram'), ('3','Graph'),('4','Gantt Graph')])
    submit = SubmitField('Launch Visualization')


    
class UploadTerminologyForm(FlaskForm):
    """ Form for uploading the terminology for a book """
    book_cap = SelectField('Select the Corpus Name', choices = [])
    text = FileField('Upload a .txt file containing a list of words', validators=[
            FileRequired(),
            FileAllowed(['txt'], 'File txt only')
            ])
    submit = SubmitField('Upload')
    
    
            