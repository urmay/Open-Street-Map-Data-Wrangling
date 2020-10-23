# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 16:06:13 2017

@author: urmayshah
"""
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import audit
import cerberus

import schema

OSM_PATH = ""

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER = re.compile(r'^([a-z]|_)*$')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def osm_xml_to_csv_func(OSM_PATH):

    def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                      problem_chars=PROBLEMCHARS, default_tag_type='regular'):
        """Clean and shape node or way XML element to Python dict"""
    
        node_attribs = {}
        way_attribs = {}
        way_nodes = []
        #tags = []  # Handle secondary tags the same way for both node and way elements
    
        
        if element.tag == 'node':
            tags = []
            #for element in element.iter('node'):
            
            for key in element.attrib:
                if key in node_attr_fields:
                    node_attribs[key] = element.attrib[key]
            for child in element.iter('tag'):
                nodeTagsDict = {}
                #if re.search(PROBLEMCHARS, child.attrib['k']):
                if PROBLEMCHARS.search(child.attrib['k']):
                    pass
                else:
                    nodeTagsDict['id'] = element.attrib['id']
                    #if re.search(LOWER_COLON, child.attrib['k']):
                    if LOWER_COLON.search(child.attrib['k']):
                        nodeTagsDict['type'] = child.attrib['k'].split(':',1)[0]
                        nodeTagsDict['key'] = child.attrib['k'].split(':',1)[1]
                        nodeTagsDict['value'] = child.attrib['v']
                    else:
                        nodeTagsDict['key'] = child.attrib['k']
                        nodeTagsDict['type'] = default_tag_type
                        nodeTagsDict['value'] = child.attrib['v']
                    tags.append(nodeTagsDict)
            return {'node': node_attribs, 'node_tags': tags}
            
        elif element.tag == 'way':
            tags = []
            #for element in element.iter('way'):
            for key in element.attrib:
                if key in way_attr_fields:
                    way_attribs[key] = element.attrib[key]
                    i = 0
            for child in element.iter('nd'):
                wayNodesDict = {}
                wayNodesDict['id'] = element.attrib['id']
                wayNodesDict['node_id'] = child.attrib['ref']
                wayNodesDict['position'] = i
                i += 1
                way_nodes.append(wayNodesDict)
            for child in element.iter('tag'):
                wayNodesDict = {}
                #if re.search(PROBLEMCHARS, child.attrib['k']):
                if PROBLEMCHARS.search(child.attrib['k']):
                    pass
                else:
                    wayNodesDict['id'] = element.attrib['id']
                    #if re.search(LOWER_COLON, child.attrib['k']):
                    if LOWER_COLON.search(child.attrib['k']):
                        wayNodesDict['type'] = child.attrib['k'].split(':',1)[0]
                        wayNodesDict['key'] = child.attrib['k'].split(':',1)[1]
                        wayNodesDict['value'] = child.attrib['v']
                    else:
                        wayNodesDict['key'] = child.attrib['k']
                        wayNodesDict['type'] = default_tag_type
                        wayNodesDict['value'] = child.attrib['v']
                    tags.append(wayNodesDict)
                    
            return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    
    
# ================================================== #
#               Helper Functions                     #
# ================================================== #
    def get_element(OSM_PATH, tags=('node', 'way', 'relation')):
        """Yield element if it is the right type of tag"""
    
        context = ET.iterparse(OSM_PATH, events=('start', 'end'))
        _, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag in tags:
                yield elem
                root.clear()
    
    
    def validate_element(element, validator, schema=SCHEMA):
        """Raise ValidationError if element does not match schema"""
        if validator.validate(element, schema) is not True:
            field, errors = next(validator.errors.iteritems())
            message_string = "\nElement of type '{0}' has the following errors:\n{1}"
            error_string = pprint.pformat(errors)
            
            raise Exception(message_string.format(field, error_string))
    
    
    class UnicodeDictWriter(csv.DictWriter, object):
        """Extend csv.DictWriter to handle Unicode input"""
    
        def writerow(self, row):
            super(UnicodeDictWriter, self).writerow({
                k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
            })
    
        def writerows(self, rows):
            for row in rows:
                self.writerow(row)
    
    
     


    # ================================================== #
    #               Main Function                        #
    # ================================================== #
    def process_map(file_in, validate):
            """Iteratively process each XML element and write to csv(s)"""
        
            with codecs.open(NODES_PATH, 'w') as nodes_file, \
                 codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
                 codecs.open(WAYS_PATH, 'w') as ways_file, \
                 codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
                 codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:
        
                nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
                node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
                ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
                way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
                way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
        
                nodes_writer.writeheader()
                node_tags_writer.writeheader()
                ways_writer.writeheader()
                way_nodes_writer.writeheader()
                way_tags_writer.writeheader()
        
                validator = cerberus.Validator()
        
                for element in get_element(file_in, tags=('node', 'way')):
                    el = shape_element(element)
                    if el:
                        if validate is True:
                            validate_element(el, validator)
        
                        if element.tag == 'node':
                            nodes_writer.writerow(el['node'])
                            node_tags_writer.writerows(el['node_tags'])
                        elif element.tag == 'way':
                            ways_writer.writerow(el['way'])
                            way_nodes_writer.writerows(el['way_nodes'])
                            way_tags_writer.writerows(el['way_tags'])
                            
    
    process_map(OSM_PATH,False)  

if __name__ == '__main__':
    # Data.py is executed as script follow this order of the functions
    
    # Before shaping the osm xml, it is madatory to clean your data. 
    #Thus we are calling audit.py so that after cleaning , we can proceed with the conversion.
    print(" Auditing the data ")
    audit.Auditing_Function()
    #copying the cleaned file here
    
    print("i came here:: problem???")
    OSM_PATH = audit.OSM_file
    print("successfully step 1")
    osm_xml_to_csv_func(OSM_PATH)
    print("step 2")
    # Now call osm_to_xml_func() for the conversion
    print("\nConverting Osm_XML to csv Format after cleaning ")
    
    print("\nData converted to csv. Please run the file \"query.py\" for checking various explorations done on the data")

