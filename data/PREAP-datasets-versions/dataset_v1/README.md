**AUTOMATIC concepts annotation and manual PR annotation**

CONTENT OF THIS FOLDER

'dataset_metadata_v1.json' & 'dataset_metadata_v1.jpg': JSON-LD & visual RDF graph encoding metadata information about the dataset and the related annotation process (according to Dataset class properties of schema.org vocabulary, based upon W3C DCAT vocabulary).

'rawText_v1.txt': raw text of the textbook chapter used for PR annotation.

'text_v1_POS.conll': linguistically analysed text (at the morphosyntactic level, i.e. Part-of-Speech) in conll format, annotated using the Penn Treebank P.O.S. Tagset.

'concept_list_automatically_extracted.txt': list of concepts  automatically extracted using T2K (see http://www.italianlp.it/demo/t2k-text-to-knowledge).

'GOLD-PR_v1_concepts': list of concepts automatically extracted and used in PR annotation (i.e., automatic concept annotation -concepts automatically extracted but not used during PR annotation are not reported in this list).

'text_v1_AnnotTerms.conll': linguistically analysed text (at the morphosyntactic level, i.e. Part-of-Speech tags usding Penn Treebank P.O.S. Tagset) in conll format. This file also contains concept annotation using IOB standard, i.e. concept occurrences are marked in the last column of the conll file. B- marks where the concept starts, I- is used to mark multi-words concepts (used from the second word onward). 


'concept_list.index': this file allows to trace concepts back on the annotated text. For each concept of the 'concept_list_onlyConceptsUsed' file, the index reports: 
	- Typical Form: the most frequent form of the concept observed in the corpus.
	- idSentence: the sentence where the concept appears, identified by a progressive number acquired from the progressive numeration fo sentences in the 'text_v1_POS.conll' file. 
	- idTermStart: where the concept starts within the sentence (e.g., if the value is 4, the concept starts at the 4th token in the sentence). Again, the id corresponds to the ids reported in 'text_v1_POS.conll' file .
	- WordLength: lenght of the concept in terms of tokens. 
	- ConceptInText: the form of the concept in the text of that specific instance. 

'GOLD-PR_v1_PRpairsOnly.tsv': the list of concept pairs marked as PRs during annotation. Note that only manually created pairs are included: non-PRs and transitive pairs are are to be acquired as described in Alzetta et al., 2019, 'Prerequisite or Not Prerequisite? That’s the Problem! An NLP-based Approach for Concept Prerequisites Learning', CLiC-it 2019.
