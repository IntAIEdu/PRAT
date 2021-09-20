# da terminale: python2 computeAgreement_PRET.py > fileout.txt
import nltk
from nltk.metrics import agreement
from nltk.metrics.agreement import AnnotationTask
from sklearn.metrics import cohen_kappa_score
import random
#from statsmodels.stats.inter_rater import (fleiss_kappa, cohens_kappa,to_table, aggregate_raters)

#prima di eseguire questo script, nella cartella da terminale
#sed -i 's/ /_/g' ./*.json

import json
import codecs
import os
import glob

extension = 'json'
raters=[]	
	
def creaCoppieAnnot(rater1,rater2,term_pairs, pairs):
        coppieannot={}
        conteggio={"1,1":0, "1,0": 0, "0,1":0, "0,0":0}
        for pair in pairs:
                if pair in term_pairs[rater1]:
                        if pair in term_pairs[rater2] :
                                coppieannot[pair]="1,1"
                                conteggio["1,1"]+=1
                        else:
                                coppieannot[pair]="1,0"
                                conteggio["1,0"]+=1
                                
                if pair not in term_pairs[rater1]:
                        if pair not in term_pairs[rater2] :
                                coppieannot[pair]="0,0"
                                conteggio["0,0"]+=1
                        else:
                                coppieannot[pair]="0,1"
                                conteggio["0,1"]+=1
        return coppieannot, conteggio
    

def computeK(conteggio, pairs):
        Po=(conteggio["1,1"]+conteggio["0,0"])/float(len(pairs)) 
        Pe1= ((conteggio["1,1"]+conteggio["1,0"])/float(len(pairs))) * ((conteggio["1,1"]+conteggio["0,1"])/float(len(pairs)))
        Pe2= ((conteggio["0,1"]+conteggio["0,0"])/float(len(pairs)))* ((conteggio["1,0"]+conteggio["0,0"])/float(len(pairs)))
        Pe=Pe1+Pe2
        k=(Po-Pe)/float(1-Pe)
        return k

def main():
        term_pairs={}
        #pairs=[]
        all_combs=[]
        #concetti estratti automaticamente condivisi da tutti gli annotatori (file txt esterno)
        InputTerminology=codecs.open("t2kconcepts.txt","r","utf-8").read()
        terminology=InputTerminology.split("\n")
        conceptst2k=[]
        for concept in terminology:
                conceptst2k.append(concept.upper())	
	
        #creo tutte le possibili coppie di concetti automatici	
        for term in conceptst2k:
                for i in range(len(conceptst2k)):
                        if term != conceptst2k[i]:
                                combination=term+"-"+conceptst2k[i]
                                combination_inv=conceptst2k[i]+"-"+term
                                #non inserisco le inverse (sia AB che BA).
                                if combination_inv not in all_combs:
                                        all_combs.append(combination)
				
	
        #per ogni json che contiene l'annotazione			
        for file in glob.glob('*.{}'.format(extension)):
                name=os.path.splitext(os.path.basename(file))[0]
                #print "File: ", name
                raters.append(name)
                term_pairs[name]=[]
                with open(file) as data_file:
                        reader = json.load(data_file)
                        reader=reader["savedInsertedRelations"]
                for annot_pairs in reader:
				#annot_pairs={u'weight': u'strong', u'advanced': u'NETWORK_SOFTWARE', u'sent': u'3', u'prerequisite': u'NETWORK'}
				#considera solo le coppie che contengono termini della terminologia automatica
                        if annot_pairs["prerequisite"] in conceptst2k and annot_pairs["advanced"] in conceptst2k:
                                concept_pair=annot_pairs["prerequisite"]+"-"+annot_pairs["advanced"]
                                #pairs.append(concept_pair)
                                term_pairs[name].append(concept_pair)
	

		
        for rater1 in raters:
                for rater2 in raters:
                        copppieannotate, conteggio=creaCoppieAnnot(rater1,rater2,term_pairs,all_combs)
                        print (rater1, rater2)
                        print ("All agree\t"+str(conteggio["1,1"]))
                        print ("1st only\t"+str(conteggio["1,0"]))
                        print ("2nd only\t"+str(conteggio["0,1"]))
                        print ("All disag\t"+str(conteggio["0,0"]))
                        print (computeK(conteggio, all_combs))
                        
			
main()