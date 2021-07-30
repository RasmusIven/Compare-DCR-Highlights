from flask import Flask, request
import xml.etree.ElementTree as ET
import typing
from typing import List, Set, Dict, Tuple, Optional
import json
app = Flask(__name__)


#   COMPARE HIGHLIGHTS ALGORITHM
#   Given two graphs, compare them by identifying annotation matches.
#   Created 29.07.21, Rasmus Iven Strømsted, DCR Solutions

#------------------------------------- Classes ---------------------------------------#

def percentage(part, whole):
    if part > 0 and whole > 0:
        return 100 * float(part)/float(whole)
    else:
        return 0

def overlap(start1, end1, start2, end2):
    """
    Check if the ranges overlap.
    """
    return (end1 >= start2) and (end2 >= start1)



class Elem:
    def __init__(self, type, ID):
        self.type: str  = type
        self.id: str = ID
        self.highlights: list = []

    def set_H(self, H):
        self.highlights.append(H)
        
    def get_H(self) -> list:
        return self.highlights
    
    def get_spans(self) -> list:
        ranges = []
        for H in self.highlights:
            ranges.append(H.span())
        return ranges
        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    
class H:
    def __init__(self, start, end):
        self.start: int = start
        self.end: int = end
    
    def span(self) -> list:
        return [self.start, self.end]

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
class Compare:
    def __init__(self, source: list, target: list, types: list):
        self.source = source
        self.target = target
        self.types = types
        self.results = dict()
    
    def set_result(self, result:list, typ:str):
        self.results[typ] = result
    

    
    
class CompareSpans(Compare):
    def give_score(self, aspan, bspan) -> int:
        """
        Given two annotations, checks if they are identical, or otherwise a overlap.
        Returns a score of 0, 0.5 or 1
        """
        score = 0
        if aspan == bspan:
            score = 1
        elif overlap(aspan[0], aspan[1], bspan[1], bspan[1]):
            score = 0.9

        return score

    # given two lists of elements with highlights, find overlaps in highlights.
    def overlaps(self, typ) -> list:
        matches = []
        source = self.source[f'{typ}']
        target = self.target[f'{typ}']
        scores ={}
        scores['points'] = 0
        for a in source:
            match = False
            if a.type == typ:
                for ah in a.highlights:
                    for b in target:
                        if b.type == typ:
                            for bh in b.highlights:
                                if match == False and self.give_score(ah.span(), bh.span() ) > 0:
                                    match = True
                                    score = self.give_score(ah.span(), bh.span())
                                    scores['points'] = scores['points'] + score
                                    matches.append({'score': score, 'matches': [a, b]})
                                    print(vars(a), vars(b))
                                    target.remove(b)
                                    source.remove(a)
                                    break;
            
        scores['amount'] = len(target) + len(source) + len(matches)
        scores['score'] = percentage(scores['points'], scores['amount'])
        return scores


#------------------------------------- Import annotations from XML ---------------------------------------#

def xml_extraction(xml, types) -> dict:
    dict = {}
    highlights = []
    elements = []
    root = xml
    #root = tree.getroot()
    
    for type in types:
        elements = []
        for new_elem in root.findall(f".//highlights/highlight[@type='{type}']"):

            # Find ID in XML
            for child in new_elem.findall(".//items/item"):
                Id = child.attrib['id']

            # find existing or create element ID to add highlights to
            match = False
            for elem in elements:
                if Id == elem.id:
                    match = True
                    addto = elem
                    break;
            # Create element:
            if match == False:
                addto = Elem(f'{type}', Id)
                elements.append(addto)

            # Add ranges as highlights to element
            for range in new_elem.findall(".//layers/layer/ranges/"):
                h = H(range.attrib['start'], range.attrib['end'])
                if str(range.text) != "":
                    h.text = range.text
                highlights.append(h)
                addto.set_H(h)
        dict[f'{type}'] = elements
    return dict


#------------------------------------- Compare annotations Functions ---------------------------------------#


#------------------------------------- REST Handler ---------------------------------------#

@app.route('/', methods=['POST'])
def home():
    data = request.data
    root = ET.fromstring(data)
    types = []
    scores = {}
    scores['final_score'] = 0
    for compare_type in root.findall(".//compare_types/type"):
        types.append(compare_type.text)
    for graph in root.findall('.//source_graph/*'):
        source = xml_extraction(graph, types)

    for graph in root.findall('.//target_graph/*'):
        target = xml_extraction(graph, types)
    
    for type in types:
        matcher = CompareSpans(source, target, type)
        score = matcher.overlaps(type)
        scores[type] = score
        scores['final_score'] = scores['final_score'] + scores[type]['score']
    
    if scores['final_score'] != 0:
        scores['final_score'] = scores['final_score'] / len(types)


    return scores
