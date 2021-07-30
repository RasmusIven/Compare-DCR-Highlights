import xml.etree.ElementTree as ET
from dcr.structure import *
#------------------------------------- Import annotations from XML ---------------------------------------#

def dcrxml(xml, types) -> dict:
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
