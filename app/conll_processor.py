import json
import pandas as pd
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom


"""
INPUTS:
    - conll from UDPipe (in a tab separated file)
    - minimal metadata provided by the user (title of the text, sentence IDs of the chapter titles):
        prendere queste info dalla fase di caricamento testo + inserimento titoli
    - (optional) concepts provided by the user
    
OUTPUTS:
    - txt file containing the text with xml tags
    - js file containing variables for the conll, the sentence list, the mappings concept_to_tok and tok_to_concept
"""


# UDpipe conll
#conll_filename = "prova_conll.csv"
# metadata
#   text_title = "Introduction to Information Retrieval"
## IDs of the sentences with the titles
# list of starting concepts, if provided
#concepts = []


# open conll and initialize mappings
#conll_df = pd.read_csv(conll_filename, encoding="utf-8", sep="\t", index_col=0)
#tok_to_concept = []
#concept_to_tok = []


# 1) BUILD A LIST WITH SENTENCE AND THEIR INFO
def create_sent_list(conll_df, titles_id):
    temp_sent_list = []

    for s in conll_df["sentence_id"].unique().tolist():    
        temp_sent_list.append({"sent_id": s, 
                          "text": conll_df[conll_df["sentence_id"]==s].iloc[0]["sentence"], 
                          "type": "chapter title" if s in titles_id else "normal sentence"})
    return temp_sent_list    

# 2) ADD IOB TAGS FOR MARKING CONCEPTS IN THE CONLL DATAFRAME
def add_iob(conll_df):
    """
    Ho eliminato questa parte perché non partiremo con una terminologia.
    Ho solamente aggiunto una colonna con valori IOB nulli per rendere il codice dopo eseguibile.
    """
    conll_df["iob"] = "_"
    return conll_df


# 3) GENERATE TEXT WITH XML TAGS

def create_text(conll_df, sent_list, text_title, concept_to_tok, tok_to_concept):
    concept_to_tok = []
    # initialize the xml tree
    root = Element('xml')
    root.set('version', '1.0')
    root.append(Comment(text_title))
    
    # nest everything inside <chapter></chapter>
    chapter_node = SubElement(root, "chapter")
    
    sent_node = SubElement(chapter_node, 'chapterTitle')
    
    # iterate through the list of sentences
    for s in sent_list:
        sent_id = s["sent_id"]
        sent_type = s["type"]
        
        # add a special node if it's a title
        
        if sent_type == "chapter title":
            sent_node = SubElement(chapter_node, 'chapterTitle')
        elif sent_type == "section title":
            # add double space before
            SubElement(chapter_node, 'br')
            SubElement(chapter_node, 'br')
            sent_node = SubElement(chapter_node, "sectionTitle")
        elif sent_type == "subsection title":
            # add double space before
            SubElement(chapter_node, 'br')
            SubElement(chapter_node, 'br')
            sent_node = SubElement(chapter_node, "subsectionTitle")
        else:
            # normal sentence: add single space before
            #if "sent_node" in globals(): # to handle the very first token
            sent_node.tail = " "
            sent_node = SubElement(chapter_node, "sent")
            
        sent_node.set("sent_id", str(sent_id))
    
        
        # iterate over the tokens in the current sentence  
            # NOTE: global_tok is the unique ID of each token (i.e. the ID of its row in the conll), 
                # curr_num_tok is the ID of each token in its sentence (i.e. its position in the sent, 
                    # i.e. the column token_id in the conll)
        for global_tok_id in conll_df[conll_df["sentence_id"] == sent_id].index:
            curr_tok = conll_df.loc[global_tok_id]
            curr_iob = conll_df.loc[global_tok_id]["iob"]
            curr_num_tok = conll_df.loc[global_tok_id]["token_id"]
            try:
                prev_tok = conll_df.loc[int(global_tok_id)-1]["lemma"]
                prev_iob = conll_df.loc[int(global_tok_id)-1]["iob"]
                prev_concept_id = str(conll_df.loc[int(global_tok_id)-1]["part_of_concept"])
            except KeyError:
                prev_tok = ""
                prev_iob = "_"
                prev_concept = ""
    
            if curr_iob == "_":
                tok_node = SubElement(sent_node, "token")
                # convert to string, otherwise it won't be parsed
                tok_node.set("tok_id", str(global_tok_id))
                tok_node.set("partof_sent", str(sent_id))
                tok_node.set("pos_in_sent", str(curr_num_tok))
                tok_node.text = curr_tok["token"]
                
                if prev_iob[0] in ["B", "I"]:
                    # the final token of a concept has been reached:
                    # find the concept node and insert an attribute with ID 
                    # (it's the concept node with still empty ID)
                    for c_n in sent_node.findall("concept"):
                        if str(c_n.attrib["concept_id"]) == "": 
                            c_n.set("concept_id", prev_concept_id)
                            # find token nodes included in the concept and insert a ref to the concept
                            for t_n in c_n.findall("token"):
                                if int(t_n.attrib["global_tok_id"]) in concept_to_tok[int(prev_concept_id)]:
                                    t_n.set("partof_autoconcept", prev_concept_id)
                            #if curr_tok["token"] not in [",", ".", ";", ":", "'", ")", "?", "!", "'s"] and prev_tok != "(":
                            c_n.tail = " "
                    
                
            if curr_iob.startswith("B"):
                if prev_iob == "_": 
                    concept_node = SubElement(sent_node, "concept")
                    concept_node.set("class", "automatic_concept")
                    concept_node.set("concept_id", "")
                    tok_node = SubElement(concept_node, "token")   
                    # convert to string, otherwise it won't be parsed
                    tok_node.set("tok_id", str(global_tok_id))
                    tok_node.set("partof_sent", str(sent_id))
                    tok_node.set("pos_in_sent", str(curr_num_tok))
                    tok_node.text = curr_tok["token"]
                
                else:
                    # the final token of a concept has been reached:
                    # find the concept node and insert an attribute with ID 
                    # (it's the concept node with still empty ID)
                    for c_n in sent_node.findall("concept"):
                        if str(c_n.attrib["concept_id"]) == "": 
                            c_n.set("concept_id", prev_concept_id)
                            # find token nodes included in the concept and insert a ref to the concept
                            for t_n in c_n.findall("token"):
                                if int(t_n.attrib["tok_id"]) in concept_to_tok[int(prev_concept_id)]:
                                    t_n.set("partof_autoconcept", prev_concept_id)
                            #if curr_tok["token"] not in [",", ".", ";", ":", "'", ")", "?", "!", "'s"] and prev_tok != "(":
                            c_n.tail = " "
    
                    
                    concept_node = SubElement(sent_node, "concept")
                    concept_node.set("class", "automatic_concept")
                    concept_node.set("concept_id", "")
                    tok_node = SubElement(concept_node, "token")        
                    # convert to string, otherwise it won't be parsed
                    tok_node.set("tok_id", str(global_tok_id))
                    tok_node.set("partof_sent", str(sent_id))
                    tok_node.set("pos_in_sent", str(curr_num_tok))
                    tok_node.text = curr_tok["token"]
            
                    
            if curr_iob.startswith("I"):
                tok_node = SubElement(concept_node, "token")
                # convert to string, otherwise it won't be parsed
                tok_node.set("tok_id", str(global_tok_id))
                tok_node.set("partof_sent", str(sent_id))
                tok_node.set("pos_in_sent", str(curr_num_tok))
                tok_node.text = curr_tok["token"]
                
            # add whitespace if needed
            #if curr_tok["token"] not in [",", ".", ";", ":", "'", ")", "?", "!", "'s"] and prev_tok != "(":
            tok_node.tail = " "
                    
            
        # add double line breaks after titles
        if sent_type in ["chapter title", "section title", "subsection title"]:
            SubElement(chapter_node, 'br')
            SubElement(chapter_node, 'br')
          
    
     # delete a possible empty <chapterTitle />
    tagged_text = str(tostring(root).decode("utf-8")).replace("<chapterTitle />", "")
    return tagged_text

    #print('autoconcepts: ' + str(concepts))
    #print('sentList: ' + str(sent_list))
    #print('conll: ' + str(conll_df.reset_index().to_dict(orient="records")))
    #print('conceptToTok: ' + str(concept_to_tok))
    #print('tokToConcept: ' + str(tok_to_concept))


def conll_processor(conll, title, sentences):
    conll_df = pd.read_csv(pd.compat.StringIO(conll))
    text_title = title
    titles_id = sentences 
    tok_to_concept = []
    concept_to_tok = []
    sent_list = create_sent_list(conll_df, titles_id)
    conll_df = add_iob(conll_df)
    text = create_text(conll_df, sent_list, text_title, concept_to_tok, tok_to_concept)
    return text, sent_list
"""
TODO:
    - the pattern </token> </concept> should be replaced with </token></concept> (only if concepts are provided)
    
Eventually TODO. Fix these minor issues to improve readability
    - add whitespace after , and ;
    - delete whitespace after (
    - delete whitespaces before . and ,
"""


### Export xml and json

    # tagged text
    # list of sentences 
    # conll dataframe
    # mapping concept_to_tok
    # mapping tok_to_concep

