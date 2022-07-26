PREAP Annotation Protocol

Resources publicly available on GitHub7:
– PREAP annotation protocol:
– PREAP Annotation Manual for Annotators
– PREAP Specifications for Project Manager
– Datasets and Source Texts used in the Evaluation
– Case Study documentation
– List of concepts, annotated PR-dataset, row text
– JSON-LD and visual RDF graph encoding metadata information about the
dataset and the related annotation process.
– Datasets and related data used in the ML Experimental tests
– PRAT tool for PR annotation and analysis




# PRAT prerequisite annotation tool 
PRAT is a tool to support the creation and analysis of Gold Standard Concept Maps 
where nodes are domain concepts and arcs are preresquisite relations between concept pairs.\
It is design according to the principles of **PREAP (PRErequisite Annotation Protocol)**.

## Features of the tool:
<li>supports the user during the annotation phase, according to the principles of PREAP
<li>provides different views of the concept maps
<li>provides agreement metrics between annotators
<li>provides annotation check and formal validation
<li>provides some  automatic methods to extract prerequisite relations
<li>allows to match Gold Standard Concept Maps against the output of automatic metods for prerequisite extraction


## Installation:
Prerequisites:

	 Python 3.4 or newer


*1. Creation of the virtual environment:*	
    
   Create a folder in which you want to have the src
   then, open the terminal and enter the following commands:
   
    - pip install virtualenv 
    - virtualenv venv       
    - venv\Scripts\activate
    
*2. Now that you have a virtual environment you can install all the packages required through:*

	-pip install -r requirements.txt 
	
*3. Database creation:*

	- flask db init
	- flask db migrate
	- flask db upgrade
  
  From the python console:

    >>> import nltk
    >>> nltk.download('punkt')
    >>> nltk.download('stopwords')
    >>> nltk.download('wordnet')
    

To start the website insert (with the virtual environment activated): flask run 

Now you can open your browser on http://127.0.0.1:5000/


