import flask
from flask import Flask, request, jsonify
import xmltodict

#   COMPARE HIGHLIGHTS ALGORITHM
#   Given two graphs, compare them by identifying annotation matches.
#   Created 02.13.21, Rasmus Iven Strømsted, DCR Solutions

#------------------------------------- Import annotations from XML ---------------------------------------#
def get_annos_from_xml(xml, annotation_type):
    """
    Given a Graph XML, extracts information about a specific annotation type, and return as dict.
    """
    highlights = []
    lista = []
    user_annos = {}
    num_anno = 0
    for highlight in xml["dcrgraph"]["specification"]["resources"]["custom"]["highlighterMarkup"]["highlights"]["highlight"]:
        if highlight["@type"] == annotation_type:
            anno = {}
            for key, value in highlight["layers"]["layer"]["ranges"]["range"].items():
                if key == "@start":
                    anno['start'] = value
                elif key == "@end":
                    anno['end'] = value
                elif key == "#text":
                    anno['text'] = value
            for key, value in highlight["items"]["item"].items():
                if key == "@id":
                    anno['id'] = value
            user_annos[num_anno] = anno
            num_anno = num_anno + 1
    return user_annos


def get_graphname_from_xml(xml):
    """
    Given a Graph XML, returns the title.
    """
    return xml["dcrgraph"]["@title"]



#------------------------------------- Compare annotations Functions ---------------------------------------#
def overlap(start1, end1, start2, end2):
    """
    Check if the ranges overlap.
    """
    return (end1 >= start2) and (end2 >= start1)


def compare_anno(anno_a, anno_b):
    """
    Given two annotations, checks if they are identical, or otherwise a overlap.
    Returns a score of 0, 0.5 or 1
    """
    score = 0
    if (anno_a['start'] == anno_b['start']) and (anno_a['end'] == anno_b['end']):
        score = 1
    elif overlap(anno_a['start'], anno_a['end'], anno_b['start'], anno_b['end']):
        score = 0.5
        
    return score


def compare_list_annos(dict_a, dict_b):
    """
    Takes two dict and compares each element in the list. If there is a match, the score is updated.
    Returns score and list of annotation matches.
    """
    anno_matches = []
    matches = []
    t_score = (0, 0) # rating, count
    
    for anno_a in dict_a.items():
        matches_for_anno = {'anno': anno_a[1], 'matches': []}
        for anno_b in dict_b.items():
            score = compare_anno(anno_a[1], anno_b[1])
            if score > 0:
                
                if anno_b in matches: # check if annotation already made:
                    t_score = (t_score[0], t_score[1] + 1)
        
                else: # Add match
                    matches.append(anno_b)
                    t_score = (t_score[0] + score, t_score[1] + 1)
                matches_for_anno['matches'].append(anno_b[1])
                
        anno_matches.append(matches_for_anno)
    if t_score[0] == 0 or t_score[1] == 0:
        r_score = 0
    else:
        r_score = (t_score[0]/t_score[1])*100
    
    return r_score


#------------------------------------- REST Handler ---------------------------------------#
myapp = Flask(__name__)

@myapp.route("/")
def hello():
    return "Hello Flask, on Azure App Service for Linux"