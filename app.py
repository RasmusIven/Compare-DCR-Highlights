import flask
from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
import typing
from typing import List, Set, Dict, Tuple, Optional
import json


#   COMPARE HIGHLIGHTS ALGORITHM
#   Given two graphs, compare them by identifying annotation matches.
#   Created 29.07.21, Rasmus Iven Strømsted, DCR Solutions

#------------------------------------- Classes ---------------------------------------#

def percentage(part, whole):
    return 100 * float(part)/float(whole)

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

    
class H:
    def __init__(self, start, end):
        self.start: int = start
        self.end: int = end
    
    def span(self) -> list:
        return [self.start, self.end]

    
class Compare:
    def __init__(self, source: list, target: list, types: list):
        self.source = source
        self.target = target
        self.types = types
        self.results = dict()
    
    def set_result(self, result:list, typ:str):
        print(results)
        print(typ)
        self.results[typ] = result
    
    def get_score(self, typ) -> int:
        source_count = len(self.source[f'{typ}'])
        print(source_count)
        #old_match_count = len(self.results[f'{typ}'])
        score = 0
        for match in self.results[f'{typ}']:
            score = score + match['score']
        print(score, source_count)
        return percentage(score, source_count)

    
    
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
            score = 0.75

        return score

    # given two lists of elements with highlights, find overlaps in highlights.
    def overlaps(self, typ) -> list:
        matches = []
        for a in self.source[f'{typ}']:
            match = False
            for ah in a.highlights:
                for b in self.target[f'{typ}']:
                    for bh in b.highlights:
                        if match == False and self.give_score(ah.span(), bh.span() ) > 0:
                            match = True
                            score = self.give_score(ah.span(), bh.span())
                            matches.append({'score': score, 'matches': [a, b]})
                            break;
        return matches


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
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['POST'])
def home():

    root = ET.fromstring(request.data)
    types = []

    for compare_type in root.findall(".//compare_types/type"):
        types.append(compare_type.text)
    print(types)
    for graph in root.findall('.//source_graph/*'):
        print(graph)
        source = xml_extraction(graph, types)

    for graph in root.findall('.//target_graph/*'):
        target = xml_extraction(graph, types)
    
    matcher = CompareSpans(source, target, types)
    matcher.results['role'] = matcher.overlaps('role')
    print('score: ', matcher.get_score('role'))

    score = matcher.get_score('role')
    return json.dumps(score)
    
        

app.run()
