
## Open Street Map Data Wrangling with SQL

## Project Summary <a name="top"></a>


### Objective: 
Thoroughly audit and clean the OSM dataset for you selected city, converting it from XML to CSV format. Then importing the cleaned .csv data file into a Sqlite database and analyze insights within the data.

#### Map area:
+ Location: Ahmedabad, Gujarat, India
- [Mapzen URl for Ahmedabad, Gujarat, India](https://mapzen.com/data/metro-extracts/metro/ahmedabad_india)

#### Reason for the choice of area: 
I have chosen Ahmedabad city's area as it is my home town.So i want to explore more about the my city.


Table of Contents 
----
[](#top)
0. [Data Audit](#audit)
1. [Problems Encountered](#problems)
2. [Data Overview with SQL](#data_overview)
3. [Exploring Data further with SQL](#exploration)
4. [Conclusion](#conclusion)
5. [References](#reference)

<h2><a name="audit"></a> **1. Data Audit**</h2>
> #### What is Data Auditing?
    Data auditing is the process of programatically checking the data using some validation rules that are written.This involves profiling the data and assessing the impact of poor quality data on the data performance.

     Below is the code I have used for auditing the OSM XML file of Ahmedabad city just to have idea about the data.(code can be found in check.py file).Besides this full auditing file can be found in audit.py file


```python
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


```

                Area Name    Latitude   Longitude
    0           Ahmedabad  23.0216238  72.5797068
    1              Naroda  23.0861141  72.6584406
    2           Vastrapur  23.0081745  72.5193869
    3           Maninagar  22.9980691  72.6118069
    4  Sabarmati Junction  23.0778134  72.5885153
    

* I have parsed through the Ahmedabad City dataset with ElementTree and counted the number of unique element types to get an overall understanding of the data by using count_tags function.

* with the use of parsing code which is written in "mapparser.py" file we got the following output which shows the no of unique tags

    **'bounds': 1,
     'member': 2278,
     'nd': 657695,
     'node': 565470,
     'osm': 1,
     'relation': 510,
     'tag': 102739,
     'way': 84533**

* In the functions __key_type_category__ & __processing_map__. We check the value of "k" for each "tag" and see if they can be suitable keys in SQL. We also check whether there are any other potential problems.
* As we saw in the earlier, we would like to change the data model and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and also if we have any tags with problematic characters.

* For the function 'key_type', we count for each of three tag categories in a dictionary:

    1.  __"LOWER"__, for tags that contain only lowercase letters and are valid,
    2.  __"LOWER_COLON"__, for otherwise valid tags with a colon in their names,
    3.  __"PROBLEMCHARS"__, for tags with problematic characters, and

    ** Below is the count for each four categories: **

    **'LOWER': 100647, 'LOWER_COLON': 2051, 'PROBLEMCHARS': 7, 'other': 34**
    
    
* During analysis we found that there are **387** unique users have contributed for ahmedabad city map.

<h2><a name="problems"></a> **2. Problem encountered**</h2>

>It is found that many streets had abbreviations,many streets names were written in different languages,many had speeling mistakes.It is also found that field pincode.zipdoce have invalid number written or have less digits may be because of manual entry.As ahmedabad city have pin code starting from 38 remaining other pincodes were considered as invalid. In this section, I have audited only Street abbreviation and pincode issue


<h3><a name="street"></a> **Street address abbreviation **</h3>
* The main problem we encountered in this dataset are the street name abbreviation inconsistency. Many streets had abbreviations, many had spelling mistakes, and some were written all together in a different language itself. 

* I have a regex matching the last element in the string, where usually the street type is provided. Also there is a list of mapping which that need not to be cleaned and a expectance list, that will be used for matching / validating the data.Below is the old name corrected with the better name. (Using audit.py)



```python
#expected names in the dataset
expected = ["Ahmedabad", "Road","Feet", "NR", "Avenue", "SBK", "Gandhi", "Bridge", "Society",
                "Gujarat","Airport", "Satellite", "Square"," Bus Rapid Transit System(BRTS)","Bapunagar",
               "Circle","Crossroad","Area"]
#old name:better name  

mapping = {"ahmedabad": "Ahmedabad","Ahmadabad": "Ahmedabad", "Ahamadabad": "Ahmedabad",
            "Nr.": "NR",
            "Ave.": "Avenue",
            "sbk": "SBK",
            "gandhi": "Gandhi",
            "bridge": "Bridge",
            "Ft.": "Feet",
            "ft": "Feet",
            "road": "Road","Rd": "Road","Rd.": "Road","rasta": "Road","Roads": "Road","Marg": "Road","orad": "Road","way": "Road","रोड" : "Road",# 'रोड' = Road in Hindi Language
            "society": "Society","soc.": "Society","Socity": "Society","Sosciety": "Society",
            "Gujarat.": "Gujarat",
            "एरपोर्ट" : "Airport",# "एरपोर्ट" = Aiport in Hindi Language
            "Settellte" : "Satellite",
            "SQUAR": "Square",
            "BRTS" : " Bus Rapid Transit System(BRTS)",
            "Bapuangar" :"Bapunagar",
            "Circle," : "Circle",
            "chokdi":"Crossroad","Crossroads": "Crossroad","area": "Area","char rasta":"Crossroad"
                }
    
```

* Converting xml to csv : we have converted xml data into following individual csv and made database.Below is the list. 

        1.nodes.csv
        2.nodes_tags.csv
        3.ways.csv
        4.ways_nodes.csv
        5.ways_tags.csv
        5.ahmedabad1.db

<h2><a name="data_overview"></a> **3. Data Overview with SQL**</h2>
> In this section we will be exploring the ahmedabad database.We have used SQL for the exploration purpose.

### 3.1 Number of nodes:


```python
def number_of_nodes():
	result = cur.execute('SELECT COUNT(*) FROM nodes')
	return result.fetchone()[0]

print "Number of nodes: " , number_of_nodes()


#OUTPUT
Number of nodes:  565470
```

### 3.2 Number of ways:


```python
def number_of_ways():
	result = cur.execute('SELECT COUNT(*) FROM ways')
	return result.fetchone()[0]

print "Number of ways: " , number_of_ways()

# OUTPUT
Number of ways:  84533
```

### 3.3 Number of Unique Users:


```python
def number_of_unique_users():
	result = cur.execute('SELECT COUNT(DISTINCT(e.uid)) \
            FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e')
	return result.fetchone()[0]

print "Number of unique users: " , number_of_unique_users()

#OUTPUT
Number of unique users:  382
```

### 3.4 Top contributing Users:


```python
def top_contributing_users():
	users = []
	for row in cur.execute('SELECT e.user, COUNT(*) as num \
            FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e \
            GROUP BY e.user \
            ORDER BY num DESC \
            LIMIT 10'):
		users.append(row)
	return users

print "Top contributing users: " , top_contributing_users()

#OUTPUT

Top contributing users:  [(u'uday01', 177284), 
                          (u'sramesh', 136607), 
                          (u'chaitanya110', 122213),
                          (u'shashi2', 49502),
                          (u'shravan91', 22900),
                          (u'vkvora', 21952), 
                          (u'shiva05', 19669), 
                          (u'Rajsamand Local Guide', 13914),
                          (u'bhanu3', 12512),
                          (u'Oberaffe', 7056)]
```

### 3.5 Number of users contributing only once:


```python
def number_of_users_contributing_once():
	result = cur.execute('SELECT COUNT(*) \
            FROM \
                (SELECT e.user, COUNT(*) as num \
                 FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e \
                 GROUP BY e.user \
                 HAVING num=1) u')
	return result.fetchone()[0]

print "Number of users contributing once: " , number_of_users_contributing_once()

#OUTPUT
Number of users contributing once:  92
```

<h2><a name="exploration"></a> **4. Exploring Data further with SQL**</h2>

### 4.1 Finding Common Ammenities:


```python
def common_ammenities():
    amenities=[]
    
    for row in cur.execute('SELECT value, COUNT(*) as num \
            FROM nodes_tags \
            WHERE key="amenity" \
            GROUP BY value \
            ORDER BY num DESC \
            LIMIT 10'):
        amenities.append(row)
    return amenities

print "Common ammenities: " , common_ammenities()

#OUTPUT

Common ammenities:  [(u'place_of_worship', 71), (u'restaurant', 50), (u'hospital', 33), (u'bank', 32),
                     (u'school', 27), (u'atm', 24), (u'fuel', 23), (u'fast_food', 22), (u'cafe', 16), (u'library', 14)]
```

### 4.2 Finding Top Religions:


```python
def top_religion():
    religion_list =[]
    
    for row in cur.execute('SELECT value, COUNT(*) as num \
            FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="place_of_worship") i \
                ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="religion" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC \
            LIMIT 5'):
        religion_list.append(row)
	
    return religion_list

print "Top Religion: " , top_religion()

#OUTPUT 

Top Religion:  [(u'hindu', 35), (u'jain', 5), (u'muslim', 4), (u'christian', 2), (u'nonsectarian', 1)]
```

### 4.3 Popular Cuisines:


```python
def popular_cuisines():
    cuisines_list =[]
    
    for row in cur.execute('SELECT value, COUNT(*) as count \
            FROM nodes_tags \
            JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="restaurant") i \
            ON nodes_tags.id=i.id \
            WHERE nodes_tags.key="cuisine" \
            GROUP BY nodes_tags.value \
            ORDER BY count DESC\
            LIMIT 10'):
        cuisines_list.append(row)
        
    return cuisines_list
print "Popular Cuisines: " , popular_cuisines()

#OUTPUT
Popular Cuisines:  [(u'regional', 7), (u'indian', 3), (u'vegetarian', 3), (u'pizza', 2),
                    (u'Punjabi,_SouthIndia,_Gujarati Thali.', 1), (u'burger', 1),
                    (u'burger;sandwich;regional;ice_cream;grill;cake;coffee_shop;pasta;noodles;pancake;pizza;chicken;fish_and_chips;curry;indian;vegan;fish;breakfast;savory_pancakes;tea;seafood;sausage;local;barbecue;vegetarian', 1),
                    (u'international', 1), (u'italian', 1), (u'sandwich', 1)]
```

### 4.4 Top List of Postcodes/Pincodes:


```python
def top_postcodes():
    top_postcode_list=[]
    
    
    for row in cur.execute('SELECT value, COUNT(*) as count\
                           FROM nodes_tags \
                           WHERE key = "postcode"\
                           GROUP BY nodes_tags.value \
                           ORDER BY count DESC\
                           LIMIT 10'):
        top_postcode_list.append(row)
    return top_postcode_list
print "Top postcodes:",top_postcodes()
#OUTPUT
Top postcodes: [(u'380009', 14), (u'380015', 13), (u'380054', 11), (u'380001', 10), 
                (u'380006', 9), (u'380008', 9), (u'382480', 7), (u'380007', 4), (u'380013', 4), (u'382481', 4)]
```

### 4.5 Top Types of Buildings found:


```python
def top_type_of_buildings():
    building_list=[]
    
    
    for row in cur.execute('SELECT value, COUNT(*) as count\
                           FROM ways_tags \
                           WHERE key = "building"\
                           GROUP BY ways_tags.value \
                           ORDER BY count DESC\
                           LIMIT 10'):
        building_list.append(row)
    return building_list
print "Top Types of Buildings:",top_type_of_buildings()  

#OUTPUT
Top Types of Buildings: [(u'yes', 70471), (u'house', 776), (u'apartments', 374),
                         (u'commercial', 139),(u'residential', 64), (u'university', 29),
                         (u'industrial', 23), (u'school', 20), (u'college', 8), (u'dormitory', 6)]
```

[<div align="center">Back to top</div>](#top)

<h2><a name="conclusion"></a> **5. Conclusion**</h2>

> **_Benifits of the Map Data:_**

> Using this data analysis of various region an be done easily.It can very useful for the market researcher as it gives lots information about the no of restaturants and cafes in the particular area.Using this one can analyze in which area no of cafes are less which directly affect the the business.Same is the case with amenities (like bank,hospitals) government can also do study using this data to improve growth of the particular area


> **_Ideas to improve data quality of OSM:_**

> When we audited the data, it was clear that although there were minor errors which might be cause by human input or might be just some random error but the dataset is fairly well-cleaned. Considering there are hundreds of contributors for this map, there is a great numbers of human errors in this project. I would recommend a structured input form,  so that every user who wants to contribute for the Map Community, can input the same data via the form so that it is entered in a Structural way.This will reduce these kind of errors . These structures can also have certain field formats which will be validated as the user enters the data.Also, we can create a robust script to clean the data on a weekly or regularly basis. 

> We can also develope the script which cleans the data on regular basis like after every six months.It may require the special team to authenticate the cahnges.To clean whole data every 6 months required use of Big dataframewrok like apache spark for implementation.

> For adding cusines or information related to food places we can also intigrate with the data from food app like zomato(India's top rated food App) for more accuracy.As zomato is independent app it is require to officially buy information about the food places.Integration of the only food related area/restaurant with general map may be difficult but use of indiavidual layers of only food iteam places on original map data can help.Updation/Insertion of Id in each file may cause the problem that we need look in.


<h2><a name="reference"></a> **6. References**</h2>

- Udacity's "Data Wrangling with SQL" subcourse under Data Analyst Course

- [Name finder:Abbreviations Guide , OpenstreetMap Wiki](http://wiki.openstreetmap.org/wiki/Name_finder:Abbreviations) 

- [Sqlite basic commands](https://www.sitepoint.com/getting-started-sqlite3-basic-commands/)

- [OpenStreetMap Data Wrangling with SQL by Pratyush Kumar](https://github.com/pratyush19/Udacity-Data-Analyst-Nanodegree/tree/master/P3-OpenStreetMap-Wrangling-with-SQL)

- [Wiki for Openstreetmap](http://wiki.openstreetmap.org/)

- [Data auditing wikipedia](https://en.wikipedia.org/wiki/Data_auditing)

- [What is Data Wrangling?](http://www.datawatch.com/what-is-data-wrangling/)

### Files included in the Folder

    1.india_ahmedabad.osm : original osm file 
    2.india_ahmedabad_sample.osm : sample data of the OSM file
    3.audit.py : audit street, city and update their names
    4.data.py : build CSV files from OSM and also parse, clean and shape data
    5.database.py : create database of the CSV files
    6.mapparser.py : find unique tags in the data
    7.query.py : different queries about the database using SQL
    8.sample.py : extract sample data from the OSM file
    9.Data_Wrangling_With_SQL.ipynb : Jupyter notebook containing the code as well as documentation for easy implementation 
    of the project
    10.Data_Wrangling_with_SQL.html : html of this notebook
    11.Data_Wrangling_with_SQL.md : Markdown of this notebook
    12.check.py : contains overview function script
    13.schema.py : Contains schema file took from udacity course file for conversion.
    14.ahmedabad1.db :contains the database of ahmedabad.

