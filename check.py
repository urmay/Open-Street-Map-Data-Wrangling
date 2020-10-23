import xml.etree.cElementTree as ET
import pandas as pd
import os

datafile = "india_ahmedabad.osm" # Name of the data set used while auditing
OSMFILE = datafile

tree = ET.parse(datafile)
root = tree.getroot()
allnodes=root.findall('node')

areaname = [] # set as a null list in case proper tag not found
dfTupleList = []
 
for node in allnodes:
    latitude = node.get('lat')
    longitude = node.get('lon')
    
    for tag in node.findall('tag'):
        if tag.attrib['k'] == 'name':
            # add code here to get the cityname
            areaname.append(tag.attrib['v'])
            #Printing the list
            dfTupleList.append((tag.attrib['v'],latitude,longitude))

df = pd.DataFrame(dfTupleList)
df.columns = ['Area Name','Latitude','Longitude']
print df.head()