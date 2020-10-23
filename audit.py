# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:40:15 2017

@author: urmayshah
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
OSM_file ="india_ahmedabad.osm"

def Auditing_Function():
         #Regex for matching String name
        regex = re.compile(r'\b\S+\.?', re.IGNORECASE)
    
        #expected names in the dataset
        expected = ["Ahmedabad", "Road","Feet", "NR", "Avenue", "SBK", "Gandhi", "Bridge", "Society",
                    "Gujarat","Airport", "Satellite", "Square"," Bus Rapid Transit System(BRTS)","Bapunagar",
                   "Circle","Crossroad","Area"]
        
        mapping = {"ahmedabad": "Ahmedabad",
                   "Ahmadabad": "Ahmedabad",
                   "Ahamadabad": "Ahmedabad",
                   "Nr.": "NR",
                   "Ave.": "Avenue",
                   "sbk": "SBK",
                   "gandhi": "Gandhi",
                   "bridge": "Bridge",
                   "Ft.": "Feet",
                   "ft": "Feet",
                   "road": "Road",
                   "Rd": "Road",
                   "Rd.": "Road",
                   "rasta": "Road",
                   "Roads": "Road",
                   "Marg": "Road",
                   "orad": "Road",
                   "way": "Road",
                   "रोड" : "Road",# 'रोड' = Road in Hindi Language
                   "society": "Society",
                   "soc.": "Society",
                   "Socity": "Society",
                   "Sosciety": "Society",
                   "Gujarat.": "Gujarat",
                   "एरपोर्ट" : "Airport",# "एरपोर्ट" = Aiport in Hindi Language
                   "Settellte" : "Satellite",
                   "SQUAR": "Square",
                   "BRTS" : " Bus Rapid Transit System(BRTS)",
                   "Bapuangar" :"Bapunagar",
                   "Circle," : "Circle",
                   "chokdi":"Crossroad",
                   "Crossroads": "Crossroad",
                   "area": "Area",
                   "char rasta":"Crossroad"
                    }
        
    # Search string for the regex. If it is matched and not in the expected list then
    # add this as a key to the set.
    def audit_street(street_types, street_name): 
        m = regex.search(street_name)
        if m:
            street_type = m.group()
            if street_type not in expected:
                street_types[street_type].add(street_name)

    def is_street_name(elem):
        # Check if it is a street name
        return (elem.attrib['k'] == "addr:street")

    def audit(OSM_file):
        # return the list that satify the above two functions
        osm_file = open(OSM_file,"r")
        street_types = defaultdict(set)
        for event,elem in ET.iterparse(osm_file,events= ("start",)):
            if elem.tag =="node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_street_name(tag):
                        audit_street(street_types, tag.attrib['v'])
    
        return street_types
    
    print("\nPrinting existing names\n")
    pprint.pprint(dict(audit(OSM_file))) # print existing names
    
    def string_case(string_val):
        # change string into titleCase except for UpperCase
        if string_val.isupper():
            return string_val
        else:
            return string_val.title()

        # return the updated names
    def update_name(name, mapping):
        name = name.split(' ')
        for i in range(len(name)):
            if name[i] in mapping:
                name[i] = string_case(mapping[name[i]])
            else:
                name[i] = string_case(name[i])
        name = ' '.join(name)
        return name

    update_street = audit(OSM_file)
    print("print the updated names\n")
    
     # print the updated names
    for street_type, ways in update_street.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print("{0}=>{1}".format(name,better_name))
    print("\n")
    
    
    #pincode auditing
    
    def pincode_audit(invalid_pincodes,pincode):
        first_two_digits = pincode[0:2]
        
        #they are not digits at all, then add them to invalid_zipcodes
        if not first_two_digits.isdigit():
            invalid_pincodes[first_two_digits].add(pincode)
        
        #Ahmedabad has postal codes of 6 digits and they start with 38
        elif first_two_digits != '38':
             invalid_pincodes[first_two_digits].add(pincode)
        
        #contains spaces
        elif ((' ') in pincode) == True:
            invalid_pincodes[first_two_digits].add(pincode)
                    
        elif len(pincode)>6:
                m = re.search(r'\d\d\d\d\d\d$',pincode)
                if m:
                    pincode = m.group()
                    invalid_pincodes[pincode].add(pincode)
        return invalid_pincodes

    #checking if it is a postcode
    def is_pincode(elem):
        return (elem.attrib['k'] == "addr:postcode")

    def audit_zip(osmfile):
        osm_file = open(osmfile, "r") # in the notbook its encoding='utf8' rather than "r"
        invalid_pincodes = defaultdict(set)
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_pincode(tag):
                        pincode_audit(invalid_pincodes,tag.attrib['v'])

        return invalid_pincodes

    # Printing invalid Zipcodes
    print("Printing Invalid Pincodes\n")
    pprint.pprint(dict(audit_zip(OSM_file)))


    # Cleaning up pin codes. Removing white spaces
    def update_pincode_name(pincode):
        #Removing white spaces
        pincodeval = pincode
        updatedZipcode = pincode.replace(" ","")
        
        if updatedZipcode == pincode:
            return (0,pincodeval)
        else:
            return (1,updatedZipcode)

    def update_pin(osmfile):
        osm_file = open(osmfile,"r")# encoding='utf8')
        invalid_pincodes = defaultdict(set)
        print("Correcting the zipcodes\n")
        
        for event, elem in ET.iterparse(osm_file, events=("start",)):
            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if is_pincode(tag):
                        pincode_audit(invalid_pincodes,tag.attrib['v'])
            
                        #updating with proper values
                        for k,val in dict(invalid_pincodes).items():
                            for value in val :
                                if value == tag.attrib['v']:
                                    Updates_Zips = update_pincode_name(tag.attrib['v'])
                                    better_name = Updates_Zips[1]
                                    if Updates_Zips[0] == 1:
                                        tag.attrib['v'] = better_name
                                        print("Updated :{0} => {1} for {2}".format(value,better_name,tag.attrib['k']))
                                    else:
                                        print("No Update Required for :{0} => {1}".format(value,better_name))
    print("\n")
    update_pin(OSM_file)

if __name__ == '__main__':
    
    # Audit.py executed as script, call the mainCall() to mark the starting point of the execution.
    Auditing_Function()
 