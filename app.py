from flask import Flask, request
import xml.etree.ElementTree as ET
from dcr.structure import *
from dcr.compare import *
import dcr.extractor as ex
app = Flask(__name__)

#   COMPARE HIGHLIGHTS ALGORITHM
#   Given two graphs, compare them by identifying annotation matches.
#   Created 29.07.21, Rasmus Iven Strømsted, DCR Solutions

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
        source = ex.dcrxml(graph, types)

    for graph in root.findall('.//target_graph/*'):
        target = ex.dcrxml(graph, types)
    
    for type in types:
        matcher = CompareSpans(source, target, type)
        score = matcher.overlaps(type)
        scores[type] = score
        scores['final_score'] = scores['final_score'] + scores[type]['score']
    
    if scores['final_score'] != 0:
        scores['final_score'] = scores['final_score'] / len(types)


    return scores

